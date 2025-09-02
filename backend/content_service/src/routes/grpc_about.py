from fastapi import APIRouter, HTTPException, Query
from grpc_client import AboutClient

router = APIRouter()

@router.get("/api/v1/about")
async def get_about(lang: str = Query('en', description="Language code (en, ru, etc.)")):
    client = AboutClient()
    try:
        result = client.get_about(lang)
        if result:
            return {"items": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to get about info")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        client.close()