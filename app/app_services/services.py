import uuid
from datetime import datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.app_auth import auth
from app.app_crud import crud
from app.app_models import models
from app.app_schemas import schemas
from app.utils import verify_email


async def services_user_check(user: schemas.UserCreate):
    email_verification = await verify_email(user.email)
    if email_verification['data']['status'] != 'valid':
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")


async def services_add_user(hashed_password: str):
    return await auth.hash_password(hashed_password)


async def services_register_user(db, user: schemas.UserCreate):
    existing_user = await crud.get_user_by_email(db, user.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")

    hashed_password = await services_add_user(user.hashed_password)
    db_user = models.User(
        user=user.user,
        email=user.email,
        hashed_password=hashed_password
    )

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def services_add_referral_code(db, user_id: int, expiration_days: int):
    existing_code = await db.execute(
        select(models.ReferralCode).where(models.ReferralCode.user_id == user_id)
    )
    existing_code = existing_code.fetchone()

    if existing_code:
        raise Exception("У пользователя уже есть активный реферальный код.")

    expiration_date = datetime.now() + timedelta(days=expiration_days)
    referral_code = models.ReferralCode(
        user_id=user_id,
        code=str(uuid.uuid4()),
        expiration_date=expiration_date
    )
    db.add(referral_code)
    await db.commit()
    await db.refresh(referral_code)
    return referral_code


async def services_register_user_with_referral_code(db, user: schemas.UserCreate, referral_code: str):
    from app.app_crud.crud import create_user
    referral = await db.execute(
        select(models.ReferralCode).where(models.ReferralCode.code == referral_code)
    )
    referral_instance = referral.scalar_one_or_none()
    if not referral_instance:
        raise Exception("Недействительный реферальный код.")

    new_user = await create_user(db, user)
    referral_entry = models.Referral(referrer_id=referral_instance.user_id, referral_id=new_user.id)
    db.add(referral_entry)
    await db.commit()
    await db.refresh(referral_entry)

    return new_user
