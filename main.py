from fastapi import FastAPI

from app.app_database.database import connect
from app.app_routers.routers import user_router

app = FastAPI(title="Referral API", docs_url="/docs")
app.include_router(user_router)

@app.on_event("startup")
async def startup():
    await connect()
