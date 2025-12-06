from __future__ import annotations

from typing import Dict, Set, Any, Optional
from fastapi import WebSocket


class DeskConnectionManager:
    def __init__(self) -> None:
        self._desks: Dict[str, Set[WebSocket]] = {}

    async def connect(self, desk_id: str, ws: WebSocket) -> None:
        """Accept WebSocket and add to desk connections."""
        await ws.accept()
        self._desks.setdefault(desk_id, set()).add(ws)

    def add_connection(self, desk_id: str, ws: WebSocket) -> None:
        """Add already-accepted WebSocket to desk connections."""
        self._desks.setdefault(desk_id, set()).add(ws)

    def disconnect(self, desk_id: str, ws: WebSocket) -> None:
        conns = self._desks.get(desk_id)
        if not conns:
            return
        conns.discard(ws)
        if not conns:
            self._desks.pop(desk_id, None)

    async def broadcast_to_desk(
        self,
        desk_id: str,
        message: dict[str, Any],
        exclude: Optional[WebSocket] = None,
    ) -> None:
        conns = self._desks.get(desk_id, set())
        dead: list[WebSocket] = []

        for cws in conns:
            if exclude is not None and cws is exclude:
                continue
            try:
                await cws.send_json(message)
            except Exception:
                dead.append(cws)

        for dws in dead:
            self.disconnect(desk_id, dws)


manager = DeskConnectionManager()