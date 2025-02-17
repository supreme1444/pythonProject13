from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.app_auth import auth
from app.app_models import models
from app.app_schemas import schemas
from app.utils import verify_email


async def services_add_user(hashed_password_add):
    return await auth.hash_password(hashed_password_add)


async def services_user_check(user):
    email_verification = await verify_email(user.email)
    if email_verification['data']['status'] != 'valid':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email недействителен")


async def services_add_referral_code(db, user_id: int, expiration_days: int):
    existing_code = await db.execute(
        select(models.ReferralCode).where(models.ReferralCode.user_id == user_id)
    )
    existing_code = existing_code.fetchone()

    if existing_code:
        raise Exception("У пользователя уже есть активный реферальный код.")

    expiration_date = datetime.now() + timedelta(days=expiration_days)
    return expiration_date


async def services_register_user_with_referral_code(db, user: schemas.UserCreate, referral_code: str):
    from app.app_crud.crud import create_user
    referral = await db.execute(
        select(models.ReferralCode).where(models.ReferralCode.code == referral_code)
    )
    referral_instance = referral.scalar_one_or_none()
    if not referral_instance:
        raise Exception("Недействительный реферальный код.")
    new_user = await create_user(db, user)
    return new_user, referral_instance
