import json
from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import jwt as pyjwt

from backend.database import get_db
from backend.models import User, ChatSession, Message
from backend.auth import SECRET_KEY, ALGORITHM
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
                        print(f"[WS Debug] node_name: {node_name}, type(node_state): {type(node_state)}, node_state: {node_state}")
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
            if session.title == "New Conversation":
                # Give a simple title based on first query
                session.title = question[:50] + "..." if len(question) > 50 else question
                db.add(session)
                
            db.commit()

            # Send final response to WebSocket
            await websocket.send_json({
                "type": "final_answer",
                "content": generation,
                "export_links": export_links,
                "flags": flags
            })

    except WebSocketDisconnect:
        print(f"Client disconnected from session: {session_id}")
