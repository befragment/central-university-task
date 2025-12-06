import uuid
import json
from datetime import date

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect, Depends

from core.connmanager import manager
from core.security import verify_token
from api.dependencies import get_deskdetail_repo, get_deskshare_repo
from repository.desk_detail import DeskDetailRepository
from repository.desk_share import DeskShareRepository
from model import DeskDetail
from api.utils import sticker_to_dict

router = APIRouter(tags=["websocket"])


@router.websocket("/{desk_id}")
async def desk_ws(
        ws: WebSocket,
        desk_id: str,
        token: str = Query(...),
        share_repo: DeskShareRepository = Depends(get_deskshare_repo),
        detail_repo: DeskDetailRepository = Depends(get_deskdetail_repo)
):
    # Сначала принимаем WebSocket, чтобы можно было отправить close code
    await ws.accept()

    payload = verify_token(token, "access")
    if not payload:
        await ws.close(code=4001, reason="Invalid token")
        return

    user_id_str = payload.get("user_id")
    if not user_id_str:
        await ws.close(code=4001, reason="Invalid token payload")
        return

    try:
        user_id = uuid.UUID(user_id_str)
        desk_uuid = uuid.UUID(desk_id)
    except ValueError:
        await ws.close(code=4000, reason="Invalid UUID format")
        return

    has_access = await share_repo.has_access(user_id, desk_uuid)

    if not has_access:
        await ws.close(code=4003, reason="Access denied")
        return

    # Регистрируем соединение (без повторного accept)
    manager.add_connection(desk_id, ws)

    try:
        stickers = await detail_repo.get_by_desk_id(desk_uuid)
        stickers_data = [sticker_to_dict(s) for s in stickers]

        await ws.send_json({
            "event": "desk:init",
            "data": {"stickers": stickers_data},
        })

        while True:
            msg = await ws.receive_json()
            event = msg.get("event")
            data = msg.get("data") or {}

            if event == "sticker:create":
                await handle_sticker_create(
                    ws, desk_id, desk_uuid, data, detail_repo
                )
                continue
            if event == "sticker:update":
                await handle_sticker_update(
                    ws, desk_id, desk_uuid, data, detail_repo
                )
                continue

            if event == "sticker:delete":
                await handle_sticker_delete(
                    ws, desk_id, desk_uuid, data, detail_repo
                )
                continue

            await ws.send_json({
                "event": "error",
                "data": {"code": "UNKNOWN_EVENT", "message": "Unknown event"},
            })

    except WebSocketDisconnect:
        manager.disconnect(desk_id, ws)

    except Exception as e:
        manager.disconnect(desk_id, ws)
        raise


async def handle_sticker_create(
        ws: WebSocket,
        desk_id: str,
        desk_uuid: uuid.UUID,
        data: dict,
        repo: DeskDetailRepository,
):
    temp_id = data.get("temp_id")
    coord = data.get("coord", {"x": 0, "y": 0})
    size = data.get("size", {"width": 150, "height": 100})
    color = data.get("color", "#FFEB3B")
    text = data.get("text", "")

    sticker = DeskDetail(
        id=uuid.uuid4(),
        desk_id=desk_uuid,
        coord=json.dumps(coord),
        size=json.dumps(size),
        color=color,
        text=text,
        created_at=date.today(),
        updated_at=date.today(),
    )

    sticker = await repo.create(sticker)

    await manager.broadcast_to_desk(desk_id, {
        "event": "sticker:created",
        "data": {
            "temp_id": temp_id,
            "sticker": sticker_to_dict(sticker),
        },
    })


async def handle_sticker_update(
        ws: WebSocket,
        desk_id: str,
        desk_uuid: uuid.UUID,
        data: dict,
        repo: DeskDetailRepository,
):
    sticker_id_str = data.get("sticker_id")
    if not sticker_id_str:
        await ws.send_json({
            "event": "error",
            "data": {"code": "VALIDATION_ERROR", "message": "sticker_id required"},
        })
        return

    try:
        sticker_id = uuid.UUID(sticker_id_str)
    except ValueError:
        await ws.send_json({
            "event": "error",
            "data": {"code": "VALIDATION_ERROR", "message": "Invalid sticker_id format"},
        })
        return

    sticker = await repo.get_by_id(sticker_id)
    if not sticker or sticker.desk_id != desk_uuid:
        await ws.send_json({
            "event": "error",
            "data": {"code": "NOT_FOUND", "message": "Sticker not found"},
        })
        return

    # Update fields if provided
    if "coord" in data:
        sticker.coord = json.dumps(data["coord"])
    if "size" in data:
        sticker.size = json.dumps(data["size"])
    if "color" in data:
        sticker.color = data["color"]
    if "text" in data:
        sticker.text = data["text"]

    sticker.updated_at = date.today()
    await repo.update(sticker)

    await manager.broadcast_to_desk(desk_id, {
        "event": "sticker:updated",
        "data": {
            "sticker_id": str(sticker_id),
            "coord": json.loads(sticker.coord),
            "size": json.loads(sticker.size),
            "color": sticker.color,
            "text": sticker.text,
        },
    })


async def handle_sticker_delete(
        ws: WebSocket,
        desk_id: str,
        desk_uuid: uuid.UUID,
        data: dict,
        repo: DeskDetailRepository,
):
    sticker_id_str = data.get("sticker_id")
    if not sticker_id_str:
        await ws.send_json({
            "event": "error",
            "data": {"code": "VALIDATION_ERROR", "message": "sticker_id required"},
        })
        return

    try:
        sticker_id = uuid.UUID(sticker_id_str)
    except ValueError:
        await ws.send_json({
            "event": "error",
            "data": {"code": "VALIDATION_ERROR", "message": "Invalid sticker_id format"},
        })
        return

    sticker = await repo.get_by_id(sticker_id)
    if not sticker or sticker.desk_id != desk_uuid:
        await ws.send_json({
            "event": "error",
            "data": {"code": "NOT_FOUND", "message": "Sticker not found"},
        })
        return

    await repo.delete(sticker)

    await manager.broadcast_to_desk(desk_id, {
        "event": "sticker:deleted",
        "data": {"sticker_id": str(sticker_id)},
    })