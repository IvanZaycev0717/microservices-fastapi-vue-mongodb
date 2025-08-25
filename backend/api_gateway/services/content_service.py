import httpx
from fastapi import HTTPException


class ContentService:
    def __init__(self):
        self.base_url = "http://localhost:8001"

    async def get_about(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(f"{self.base_url}/about", timeout=10.0)
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=502, detail=f"Content service unavailable: {str(e)}"
                )

    async def get_certificates(self):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/certificates", timeout=10.0
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=502, detail=f"Content service unavailable: {str(e)}"
                )

    async def get_certificate_by_id(self, certificate_id: int):
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/certificates/{certificate_id}", timeout=10.0
                )
                if response.status_code == 404:
                    raise HTTPException(status_code=404, detail="Certificate not found")
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=502, detail=f"Content service unavailable: {str(e)}"
                )
