import json

from model import DeskDetail

def sticker_to_dict(sticker: DeskDetail) -> dict:
    """Convert DeskDetail model to dict for JSON response."""
    return {
        "id": str(sticker.id),
        "coord": json.loads(sticker.coord) if isinstance(sticker.coord, str) else sticker.coord,
        "size": json.loads(sticker.size) if isinstance(sticker.size, str) else sticker.size,
        "color": sticker.color,
        "text": sticker.text,
    }