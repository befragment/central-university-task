from fastapi import APIRouter

router = APIRouter(
    tags=["common"],
)


@router.get("/health")
async def health():
    return {"status": "ok"}
