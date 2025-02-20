from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.app_models import models
from app.app_schemas import schemas
from app.app_services.services import services_add_referral_code, services_add_user


async def get_user_by_email(db: AsyncSession, email: str):
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def create_user(db: AsyncSession, user: schemas.UserCreate):
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


async def create_referral_code(db: AsyncSession, user_id: int, expiration_days: int):
    return await services_add_referral_code(db, user_id, expiration_days)


async def delete_referral_code(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(models.ReferralCode).where(models.ReferralCode.user_id == user_id)
    )
    referral_code = result.scalar_one_or_none()
    if not referral_code:
        raise Exception("Нет активного реферального кода")

    await db.delete(referral_code)
    await db.commit()


async def get_referral_code_by_email(db: AsyncSession, email: str):
    user = await get_user_by_email(db, email)
    if user:
        return await db.execute(
            select(models.ReferralCode).where(models.ReferralCode.user_id == user.id)
        ).scalar_one_or_none()
    return None


async def get_referrals_by_referrer_id(db: AsyncSession, referrer_id: int):
    referrals = await db.execute(
        select(models.Referral).where(models.Referral.referrer_id == referrer_id)
    )
    return referrals.scalars().all()
