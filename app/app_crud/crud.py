import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.app_cache import ReferralCodeCache
from app.app_models import models
from app.app_schemas import schemas
from app.app_services import services
from app.app_services.services import services_add_user, services_add_referral_code

referral_code_cache = ReferralCodeCache()


async def create_user(db, user: schemas.UserCreate):
    hashed_password = await services_add_user(user.hashed_password)
    db_user = models.User(
        user=user.user,
        email=user.email,
        hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_email(db: AsyncSession, email: str):
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalars().first()


async def create_referral_code(db, user_id: int, expiration_days: int):
    expiration_date = await services_add_referral_code(db, user_id, expiration_days)
    referral_code = models.ReferralCode(
        user_id=user_id,
        code=str(uuid.uuid4()),
        expiration_date=expiration_date
    )
    db.add(referral_code)
    await db.commit()
    await db.refresh(referral_code)
    return referral_code


async def delete_referral_code(db, user_id: int):
    result = await db.execute(
        select(models.ReferralCode).where(models.ReferralCode.user_id == user_id)
    )
    referral_code = result.scalar_one_or_none()
    if not referral_code:
        raise Exception("Нет активного реферального кода")
    referral_code_cache.delete(str(user_id))
    await db.delete(referral_code)
    await db.commit()


async def get_referral_code_by_email(db, email: str):
    user = await db.execute(
        select(models.User).where(models.User.email == email)
    )
    user_instance = user.scalar_one_or_none()
    if user_instance:
        referral_code = referral_code_cache[str(user_instance.id)]
        if referral_code is None:
            referral_code_result = await db.execute(
                select(models.ReferralCode).where(models.ReferralCode.user_id == user_instance.id)
            )
            referral_code = referral_code_result.scalar_one_or_none()
            if referral_code:
                referral_code_cache[str(user_instance.id)] = referral_code
        return referral_code

    return None


async def get_referrals_by_referrer_id(db, referrer_id: int):
    referrals = await db.execute(
        select(models.Referral).where(models.Referral.referrer_id == referrer_id)
    )
    return referrals.scalars().all()


async def register_user_with_referral_code(db, user: schemas.UserCreate, referral_code: str):
    new_user, referral_instance = await services.services_register_user_with_referral_code(db, user, referral_code)
    referral_entry = models.Referral(referrer_id=referral_instance.user_id, referral_id=new_user.id)
    db.add(referral_entry)
    await db.commit()
    await db.refresh(referral_entry)

    return new_user
