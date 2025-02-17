import httpx
from fastapi import HTTPException
from starlette import status

HUNTER_API_KEY = 'e1d2ff0438be44b0e1e0b69b9e5a25bdc46084d0'


async def verify_email(email: str):
    url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={HUNTER_API_KEY}"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Ошибка проверки email")
