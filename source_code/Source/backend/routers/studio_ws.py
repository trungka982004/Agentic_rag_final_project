import json
import logging
import asyncio
from typing import Dict, Any, Optional
from uuid import UUID

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
import jwt as pyjwt

from backend.database import get_db
from backend.models import User, Project
from backend.auth import SECRET_KEY, ALGORITHM
from agent.studio_graph import create_studio_agent_graph

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/ws/studio",
    tags=["Academic Studio WebSocket Copilot"]
)

studio_agent = create_studio_agent_graph()

async def get_current_user_ws(token: str, db: Session) -> Optional[User]:
    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            return None
        return db.query(User).filter(User.email == email).first()
    except Exception as e:
        logger.warning(f"Studio WebSocket auth warning: {e}")
        return None

@router.websocket("/{project_id}")
async def studio_websocket_endpoint(
    websocket: WebSocket,
    project_id: str,
    token: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Real-time streaming WebSocket endpoint for Academic Studio Canvas AI Copilot."""
    await websocket.accept()
    logger.info(f"Studio WebSocket connected for project: {project_id}")

    try:
        while True:
            raw_data = await websocket.receive_text()
            try:
                data = json.loads(raw_data)
            except Exception:
                await websocket.send_json({"type": "error", "message": "Invalid JSON format"})
                continue

            mode = data.get("mode", "matrix")
            input_text = data.get("text", "")
            domain = data.get("domain", "it")

            if not input_text.strip():
                await websocket.send_json({"type": "error", "message": "Text payload cannot be empty"})
                continue

            node_map = {
                "matrix": "literature_matrix",
                "citation": "citation_suggest",
                "polish": "tone_polish",
                "audit": "reviewer2_audit"
            }
            active_node = node_map.get(mode, "literature_matrix")

            # 1. Dispatch Status
            await websocket.send_json({
                "type": "status",
                "detail": f"Studio Copilot executing: {active_node.replace('_', ' ').title()}..."
            })
            await websocket.send_json({
                "type": "node_update",
                "node": active_node,
                "status": "running"
            })

            # 2. Invoke LangGraph Studio Agent
            state_input = {
                "question": input_text,
                "domain": domain,
                "selected_doc": mode,
                "documents": [],
                "generation": "",
                "chat_history": []
            }
            config = {"configurable": {"thread_id": f"studio-{project_id}"}}

            loop = asyncio.get_event_loop()
            final_state = await loop.run_in_executor(
                None,
                lambda: studio_agent.invoke(state_input, config=config)
            )

            result_text = final_state.get("generation", "No generation produced.")

            # 3. Stream Response
            await websocket.send_json({
                "type": "final_answer",
                "content": result_text,
                "mode": mode
            })
            await websocket.send_json({
                "type": "node_update",
                "node": active_node,
                "status": "done"
            })

    except WebSocketDisconnect:
        logger.info(f"Studio WebSocket disconnected for project: {project_id}")
    except Exception as e:
        logger.error(f"Studio WebSocket exception: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
