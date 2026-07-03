import json
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
import jwt as pyjwt

from backend.database import get_db
from backend.models import User, ChatSession, Message
from backend.auth import SECRET_KEY, ALGORITHM, get_current_user
from agent.graph import create_agent_graph

router = APIRouter(
    prefix="/api/ws",
    tags=["WebSocket Chat"]
)

# Initialize LangGraph
agent_app = create_agent_graph()

async def get_current_user_ws(token: str, db: Session) -> User:
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
    except Exception:
        return None
    user = db.query(User).filter(User.email == email).first()
    return user

def generate_chat_summary(question: str, answer: str) -> str:
    try:
        from local_rag import llm
        if llm:
            prompt = (
                "Bạn là một trợ lý học thuật chuyên nghiệp. Hãy tóm tắt câu hỏi của người dùng và câu trả lời "
                "thành một tiêu đề ngắn gọn (không quá 6 từ, ví dụ: 'Thuật toán Attention trong Transformer', "
                "'Học sâu và xử lý ngôn ngữ', v.v.). Trả về DUY NHẤT tiêu đề tóm tắt đó, không giải thích gì thêm.\n\n"
                f"Câu hỏi: {question}\n"
                f"Trả lời: {answer[:150]}"
            )
            response = llm.invoke(prompt)
            summary = response.content.strip().replace('"', '').replace("'", "")
            summary = summary.rstrip(".")
            if summary and len(summary) > 3 and len(summary) < 60:
                return summary
    except Exception as e:
        print(f"[Summary Generation] Error: {e}")
    # Fallback
    return question[:40] + "..." if len(question) > 40 else question

@router.websocket("/chat/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: UUID, token: str, db: Session = Depends(get_db)):
    user = await get_current_user_ws(token, db)
    if not user:
        await websocket.close(code=1008) # Policy Violation
        return

    # Verify session belongs to user
    session = db.query(ChatSession).filter(ChatSession.id == session_id, ChatSession.user_id == user.id).first()
    if not session:
        await websocket.close(code=1008)
        return

    await websocket.accept()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                question = payload.get("question", "").strip()
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue
            
            if not question:
                continue

            # Save user message to DB
            user_msg = Message(session_id=session.id, role="user", content=question)
            db.add(user_msg)
            db.commit()

            # Retrieve chat history
            messages = db.query(Message).filter(Message.session_id == session.id).order_by(Message.created_at).all()
            chat_history = []
            
            # Group into user-agent pairs
            current_user_msg = None
            for msg in messages:
                if msg.role == "user":
                    current_user_msg = msg.content
                elif msg.role == "agent" and current_user_msg is not None:
                    chat_history.append({"user": current_user_msg, "agent": msg.content})
                    current_user_msg = None

            # Prepare graph inputs
            inputs = {
                "question": question,
                "chat_history": chat_history,
                "use_tavily": True,
                "export_to_workspace": True,
                "expert_required": True,
                "python_repl": True,
                "web_fallback": True,
                "documents": [],           
                "generation": "",          
                "structured_data": None    
            }

            config = {"configurable": {"thread_id": str(session.id)}, "recursion_limit": 10}

            # Send a processing start event
            await websocket.send_json({"type": "status", "message": "Agent processing started..."})

            state = {}
            # Stream events from LangGraph
            try:
                async for event in agent_app.astream(inputs, config=config, stream_mode="updates"):
                    # Event is a dictionary where keys are node names and values are the returned state updates
                    for node_name, node_state in event.items():
                        print(f"[WS Debug] node_name: {node_name}, type(node_state): {type(node_state)}, node_state: {repr(node_state)}")
                        await websocket.send_json({
                            "type": "node_update",
                            "node": node_name,
                            "message": f"Completed node: {node_name}"
                        })
                        if node_state is not None:
                            state.update(node_state)
                final_state = state
            except Exception as e:
                import traceback
                traceback.print_exc()
                await websocket.send_json({"type": "error", "message": f"Error during processing: {str(e)}"})
                continue

            if final_state is None:
                # Fallback if streaming didn't emit anything (shouldn't happen)
                final_state = await agent_app.ainvoke(inputs, config=config)

            # Get final outputs
            generation = final_state.get("generation", "No answer generated.")
            export_links = final_state.get("export_links", {})
            flags = {
                "expert_required": final_state.get("expert_required"),
                "python_repl": final_state.get("python_repl"),
                "web_fallback": final_state.get("web_fallback"),
                "export_to_workspace": final_state.get("export_to_workspace")
            }

            # Save agent message to DB
            agent_msg = Message(
                session_id=session.id, 
                role="agent", 
                content=generation,
                export_links=export_links,
                flags=flags
            )
            db.add(agent_msg)
            
            # Update session title if it's the first message
            if session.title in ["New Conversation", "Cuộc hội thoại mới", "New Chat"]:
                session.title = generate_chat_summary(question, generation)
                db.add(session)
                
            db.commit()
            db.refresh(agent_msg)

            # Send final response to WebSocket
            await websocket.send_json({
                "type": "final_answer",
                "id": str(agent_msg.id),
                "content": generation,
                "export_links": export_links,
                "flags": flags
            })

    except WebSocketDisconnect:
        print(f"Client disconnected from session: {session_id}")

@router.post("/messages/{message_id}/export")
def export_message(
    message_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Fetch the message
    msg = db.query(Message).filter(Message.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    # Check session owner
    session = db.query(ChatSession).filter(ChatSession.id == msg.session_id, ChatSession.user_id == current_user.id).first()
    if not session:
        raise HTTPException(status_code=403, detail="Not authorized to access this message")
        
    if msg.role != "agent":
        raise HTTPException(status_code=400, detail="Only agent responses can be exported")
        
    # Find the preceding user message to get the question context
    preceding_user_msg = db.query(Message).filter(
        Message.session_id == msg.session_id,
        Message.created_at < msg.created_at,
        Message.role == "user"
    ).order_by(Message.created_at.desc()).first()
    
    question = preceding_user_msg.content if preceding_user_msg else "Scientific Query"
    generation = msg.content
    
    # Run the export logic
    import re
    import os
    from tools.mermaid_renderer import render_mermaid_to_image
    from tools.google_workspace import export_to_google_docs, export_to_google_sheets, upload_image_to_drive, _get_google_credentials
    
    # Verify google workspace credentials and throw descriptive errors
    try:
        creds = _get_google_credentials()
        if not creds:
            raise HTTPException(
                status_code=400,
                detail="Google Workspace credentials are not configured or token is expired. Please check credentials.json/token.json or re-authenticate."
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

        # Helper function to generate a title
        def generate_short_title(text: str, prefix: str = "doc") -> str:
            clean = re.sub(r'[^\w\s-]', '', text).strip()
            words = clean.split()
            title_words = words[:5]
            return f"SIS_{prefix.upper()}_" + "_".join(title_words)
            
        doc_title = generate_short_title(question, "docs")
        clean_content = re.sub(r"```mermaid\s*(.*?)\s*```", "", generation, flags=re.DOTALL).strip()
        
        doc_content = f"QUESTION:\n{question}\n\n"
        if clean_content:
            doc_content += f"ANSWER:\n{clean_content}\n"
        else:
            doc_content += "ANSWER:\n(Please refer to the diagram below)\n"
            
        doc_result = export_to_google_docs(title=doc_title, content=doc_content, image_urls=image_urls)
        if "Error" in doc_result or "Credentials" in doc_result:
            raise Exception(doc_result)
        
        sheet_title = generate_short_title(question, "sheets")
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
        
        # Extract links from results
        export_links = {"docs": None, "sheets": None}
        doc_match = re.search(r"https?://\S+", doc_result)
        if doc_match:
            export_links["docs"] = doc_match.group(0).rstrip(".")
        sheet_match = re.search(r"https?://\S+", sheet_result)
        if sheet_match:
            export_links["sheets"] = sheet_match.group(0).rstrip(".")
            
        # Update message in db
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
