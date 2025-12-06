import uuid
from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from core.connmanager import manager
from core.security import verify_token

router = APIRouter(prefix="/desk", tags=["desk"])


@router.websocket("/desk/{desk_id}")
async def desk_ws(
    ws: WebSocket,
    desk_id: str,
    token: str = Query(...)
    
):
    # 1) проверить доступ (owner/share)
    # if not await user_has_access(user.id, desk_id):
    #     await ws.close(code=1008)
    #     return

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

    await manager.connect(desk_id, ws)

    stickers = []  # TODO: загрузить из БД desk_detail по desk_id
    await ws.send_json({
        "event": "desk:init",
        "data": {"stickers": stickers},
    })

    try:
        while True:
            msg = await ws.receive_json()
            event = msg.get("event")
            data = msg.get("data") or {}

            if event == "sticker:created":
                temp_id = data.get("temp_id")

                sticker = {  # этот объект придет с фронта
                    "id": "server-uuid",
                    "coord": data.get("coord"),
                    "size": data.get("size"),
                    "color": data.get("color", "#FFEB3B"),
                    "text": data.get("text", ""),
                }

                # TODO: save to database

                await manager.broadcast_to_desk(desk_id, {
                    "event": "sticker:created",
                    "data": {"temp_id": temp_id, "sticker": sticker},
                })
                continue

            if event == "sticker:updated":
                sticker_id = data.get("sticker_id")
                if not sticker_id:
                    await ws.send_json({
                        "event": "error",
                        "data": {"code": "VALIDATION_ERROR", "message": "sticker_id required"},
                    })
                    continue

                # TODO: update sticker

                await manager.broadcast_to_desk(desk_id, {
                    "event": "sticker:updated",
                    "data": data,
                }, exclude=None)
                continue

            if event == "sticker:deleted":
                sticker_id = data.get("sticker_id")
                if not sticker_id:
                    await ws.send_json({
                        "event": "error",
                        "data": {"code": "VALIDATION_ERROR", "message": "sticker_id required"},
                    })
                    continue

                # TODO: delete sticker
                
                await manager.broadcast_to_desk(desk_id, {
                    "event": "sticker:deleted",
                    "data": {"sticker_id": sticker_id},
                })
                continue

            await ws.send_json({
                "event": "error",
                "data": {"code": "UNKNOWN_EVENT", "message": "Unknown event"},
            })

    except WebSocketDisconnect:
        manager.disconnect(desk_id, ws)
