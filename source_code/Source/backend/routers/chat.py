import json
import logging
import asyncio
import re
import os
from uuid import UUID
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt as pyjwt

from backend.database import get_db
from backend.models import User, ChatSession, Message
from backend.auth import SECRET_KEY, ALGORITHM, get_current_user
from agent.graph import create_agent_graph

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ws",
    tags=["WebSocket Chat"]
)

# Initialize LangGraph compilation
agent_app = create_agent_graph()

async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    """Extracts and validates user from JWT token during WebSocket handshake.

    Args:
        token: Authorization token string.
        db: Database session.

    Returns:
        The matched User database object or None.
    """
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except Exception as e:
        logger.warning(f"WebSocket token validation failed: {e}")
        return None
    user = db.query(User).filter(User.email == email).first()
    return user


def generate_chat_summary(question: str, answer: str) -> str:
    """Generates a concise 6-word summary of the first turn to serve as chat session title.

    Args:
        question: User query.
        answer: Agent response.

    Returns:
        A short title string.
    """
    try:
        from local_rag import llm
        if llm:
            prompt = (
                "You are a professional academic assistant. Summarize the user's question and response "
                "into a brief title (no more than 6 words, e.g., 'Attention Algorithm in Transformers', "
                "'Deep Learning & NLP', etc.). Return ONLY the summarized title, with no further explanation.\n\n"
                f"Question: {question}\n"
                f"Answer: {answer[:150]}"
            )
            response = llm.invoke(prompt)
            summary = response.content.strip().replace('"', '').replace("'", "")
            summary = summary.rstrip(".")
            if summary and 3 < len(summary) < 60:
                return summary
    except Exception as e:
        logger.error(f"Error generating chat session summary: {e}")
    
    return question[:40] + "..." if len(question) > 40 else question


@router.websocket("/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: UUID, token: str, db: Session = Depends(get_db)) -> None:
    """Handles real-time WebSocket chat connections, streaming LangGraph nodes, and persisting history.

    Args:
        websocket: Active WebSocket channel.
        session_id: Session identifier.
        token: JWT auth token.
        db: Database session.
    """
    user = await get_current_user_ws(token, db)
    if not user:
        logger.warning(f"Unauthorized WebSocket access attempt for session {session_id}.")
        await websocket.close(code=1008)
        return

    # Verify session ownership
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        logger.warning(f"Forbidden WebSocket session access for user {user.email} and session {session_id}.")
        await websocket.close(code=1008)
        return

    await websocket.accept()

    async def safe_send(payload: dict) -> bool:
        try:
            await websocket.send_json(payload)
            return True
        except Exception as e:
            logger.debug(f"Failed to send JSON over WebSocket: {e}")
            return False

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                
                raw_question = payload.get("question")
                question = raw_question.strip() if isinstance(raw_question, str) else ""
                
                raw_domain = payload.get("domain")
                preferred_domain = raw_domain.strip() if isinstance(raw_domain, str) else ""
                
                raw_selected_doc = payload.get("selected_doc")
                selected_doc = raw_selected_doc.strip() if isinstance(raw_selected_doc, str) else ""
                if not selected_doc:
                    selected_doc = None
            except json.JSONDecodeError:
                if not await safe_send({"type": "error", "message": "Invalid JSON format"}):
                    break
                continue
            
            if not question:
                continue

            # Save user prompt
            user_msg = Message(session_id=session.id, role="user", content=question)
            db.add(user_msg)
            db.commit()

            # Retrieve prior session context
            messages = db.query(Message).filter(Message.session_id == session.id).order_by(Message.created_at).all()
            chat_history = []
            
            # Format to user-agent pairs
            current_user_msg = None
            for msg in messages:
                if msg.role == "user":
                    current_user_msg = msg.content
                elif msg.role == "agent" and current_user_msg is not None:
                    chat_history.append({"user": current_user_msg, "agent": msg.content})
                    current_user_msg = None

            inputs = {
                "question": question,
                "original_question": None,
                "chat_history": chat_history,
                "preferred_domain": preferred_domain,
                "use_tavily": True,
                "export_to_workspace": True,
                "expert_required": True,
                "python_repl": True,
                "web_fallback": True,
                "documents": [],           
                "generation": "",          
                "structured_data": None,
                "selected_doc": selected_doc
            }

            config = {"configurable": {"thread_id": str(session.id)}, "recursion_limit": 10}

            if not await safe_send({"type": "status", "message": "Agent processing started..."}):
                break

            state = {}
            # Stream execution nodes in real-time
            try:
                async for event in agent_app.astream(inputs, config=config, stream_mode="updates"):
                    for node_name, node_state in event.items():
                        logger.info(f"LangGraph executed node: {node_name}")
                        if not await safe_send({
                            "type": "node_update",
                            "node": node_name,
                            "message": f"Completed node: {node_name}"
                        }):
                            break
                        if node_state is not None:
                            state.update(node_state)
                final_state = state
            except Exception as e:
                logger.error(f"Error during LangGraph streaming: {e}", exc_info=True)
                await safe_send({"type": "error", "message": f"Error during processing: {str(e)}"})
                continue

            if final_state is None:
                final_state = await agent_app.ainvoke(inputs, config=config)

            generation = final_state.get("generation", "No answer generated.")
            export_links = final_state.get("export_links", {})
            original_question = final_state.get("original_question")
            corrected_question = final_state.get("question") if original_question else None
            flags = {
                "expert_required": final_state.get("expert_required"),
                "python_repl": final_state.get("python_repl"),
                "web_fallback": final_state.get("web_fallback"),
                "export_to_workspace": final_state.get("export_to_workspace")
            }

            # Save generated agent response
            agent_msg = Message(
                session_id=session.id, 
                role="agent", 
                content=generation,
                export_links=export_links,
                flags=flags
            )
            db.add(agent_msg)

            is_first_message = session.title in ["New Conversation", "New Chat"]

            db.commit()
            db.refresh(agent_msg)

            if not await safe_send({
                "type": "final_answer",
                "id": str(agent_msg.id),
                "content": generation,
                "export_links": export_links,
                "flags": flags,
                "original_question": original_question,
                "corrected_question": corrected_question,
            }):
                break

            # Handle title condensation asynchronously in background
            if is_first_message:
                from backend.database import get_db as _get_db_factory
                async def _update_title_bg(q: str, ans: str, sess_id: UUID) -> None:
                    try:
                        title = generate_chat_summary(q, ans)
                        bg_db = next(_get_db_factory())
                        try:
                            from backend.models import ChatSession as _CS
                            bg_sess = bg_db.query(_CS).filter(_CS.id == sess_id).first()
                            if bg_sess and bg_sess.title in ["New Conversation", "New Chat"]:
                                bg_sess.title = title
                                bg_db.add(bg_sess)
                                bg_db.commit()
                        finally:
                            bg_db.close()
                    except Exception as _e:
                        logger.error(f"Background title generation failed: {_e}")
                asyncio.create_task(_update_title_bg(question, generation, session.id))

    except WebSocketDisconnect:
        logger.info(f"Client disconnected from session: {session_id}")


@router.post("/messages/{message_id}/export")
def export_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Trigger manual export of a specific assistant response.

    Args:
        message_id: Message UUID.
        current_user: Logged-in User.
        db: Database session.

    Returns:
        Export URLs dictionary.
    """
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    session = db.query(ChatSession).filter(ChatSession.id == msg.session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=403, detail="Not authorized to access this message")
        
    if msg.role != "agent":
        raise HTTPException(status_code=400, detail="Only agent responses can be exported")
        
    preceding_user_msg = db.query(Message).filter(
        Message.session_id == msg.session_id,
        Message.created_at < msg.created_at,
        Message.role == "user"
    ).order_by(Message.created_at.desc()).first()
    
    question = preceding_user_msg.content if preceding_user_msg else "Scientific Query"
    generation = msg.content
    
    from tools.mermaid_renderer import render_mermaid_to_image
    from tools.google_workspace import export_to_google_docs, export_to_google_sheets, upload_image_to_drive, _get_google_credentials
    
    try:
        creds = _get_google_credentials()
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="Google Workspace credentials are not configured. Please add credentials.json/token.json."
            )
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Authentication Credentials Error: {str(e)}"
        )

    try:
        image_urls = []
        mermaid_blocks = list(set(re.findall(r"```mermaid\s*(.*?)\s*```", generation, re.DOTALL)))
        for mmd_code in mermaid_blocks:
            image_path = render_mermaid_to_image(mmd_code.strip())
            if image_path:
                drive_url = upload_image_to_drive(image_path)
                if drive_url:
                    image_urls.append(drive_url)
                if os.path.exists(image_path):
                    try:
                        os.remove(image_path)
                    except Exception:
                        pass

        def generate_short_title_helper(text: str, prefix: str = "doc") -> str:
            clean = re.sub(r'[^\w\s-]', '', text).strip()
            words = clean.split()
            title_words = words[:5]
            return f"SIS_{prefix.upper()}_" + "_".join(title_words)
            
        doc_title = generate_short_title_helper(question, "docs")
        clean_content = re.sub(r"```mermaid\s*(.*?)\s*```", "", generation, flags=re.DOTALL).strip()
        
        doc_content = f"QUESTION:\n{question}\n\n"
        if clean_content:
            doc_content += f"ANSWER:\n{clean_content}\n"
        else:
            doc_content += "ANSWER:\n(Please refer to the diagram below)\n"
            
        doc_result = export_to_google_docs(title=doc_title, content=doc_content, image_urls=image_urls)
        if "Error" in doc_result or "Credentials" in doc_result:
            raise Exception(doc_result)
        
        sheet_title = generate_short_title_helper(question, "sheets")
        clean_generation = re.sub(r"```mermaid\s*(.*?)\s*```", "[Diagram Rendered in Doc]", generation, flags=re.DOTALL).strip()
        
        sheet_data = [
            ["Field", "Value"],
            ["Question", question],
            ["Answer", clean_generation],
            ["Status", "Completed"]
        ]
        sheet_result = export_to_google_sheets(title=sheet_title, data=sheet_data)
        if "Error" in sheet_result or "Credentials" in sheet_result:
            raise Exception(sheet_result)
        
        export_links = {"docs": None, "sheets": None}
        doc_match = re.search(r"https?://\S+", doc_result)
        if doc_match:
            export_links["docs"] = doc_match.group(0).rstrip(".")
        sheet_match = re.search(r"https?://\S+", sheet_result)
        if sheet_match:
            export_links["sheets"] = sheet_match.group(0).rstrip(".")
            
        msg.export_links = export_links
        db.add(msg)
        db.commit()
        db.refresh(msg)
        
        return {"export_links": export_links}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Google Workspace export failed: {str(e)}"
        )
