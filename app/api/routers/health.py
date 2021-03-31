from fastapi import APIRouter

router = APIRouter()


@router.get("/live")
async def liveness_check():
    """
    Returns OK if the service is running.
    """
    return "OK"
