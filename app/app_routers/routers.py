from typing import List
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from app.app_auth import auth
from app.app_auth.auth import authenticate_user, create_access_token
from app.app_crud import crud
from app.app_database.database import get_db
from app.app_models import models
from app.app_schemas import schemas
from app.app_schemas.schemas import UserBase
from app.app_services.services import services_user_check


user_router = APIRouter()


@user_router.post("/register", response_model=schemas.UserResponse)
async def register(
        user: schemas.UserCreate,
        db: AsyncSession = Depends(get_db)
):
    """
        Регистрация с проверками email и юзера через clearbit,
        Hunter IO.

    """
    await services_user_check(user)
    if user.referral_code != "":
        try:
            new_user = await crud.register_user_with_referral_code(db, user, user.referral_code)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    else:
        existing_user = await crud.get_user_by_email(db, user.email)
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email уже зарегистрирован")
        new_user = await crud.create_user(db, user)

    return new_user


@user_router.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """
    Авторизация.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials",
                            headers={"WWW-Authenticate": "Bearer"})
    access_token = await create_access_token(data={"sub": user.user})

    return {"token_type": "bearer", "access_token": access_token}


@user_router.post("/referral-code", response_model=schemas.ReferralCodeResponse)
async def create_referral_code(
        expiration_days: int,
        db: AsyncSession = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
):
    """
        Создание реферального кода.
    """
    new_code = await crud.create_referral_code(db, user.id, expiration_days)
    return new_code


@user_router.delete("/referral-code", status_code=status.HTTP_204_NO_CONTENT)
async def delete_referral_code(
        db: AsyncSession = Depends(get_db),
        user: models.User = Depends(auth.get_current_user)
):
    """
        Удаление реферального кода.
    """
    await crud.delete_referral_code(db, user.id)


@user_router.get("/referral-code-by-email/{email}", response_model=schemas.ReferralCodeResponse)
async def get_referral_code_by_email(
        email: str,
        db: AsyncSession = Depends(get_db)
):
    """
        Получение реферального кода по email.
    """
    email = email.lower()
    try:
        user_email = UserBase(email=email)
    except ValidationError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    referral_code = await crud.get_referral_code_by_email(db, user_email.email)
    if not referral_code:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Реферальный код не найден")
    return referral_code


@user_router.get("/referrals/{referrer_id}", response_model=List[schemas.ReferralResponse])
async def get_referrals(
        referrer_id: int,
        db: AsyncSession = Depends(get_db)
):
    """
        Получение 	информации о рефералах по id реферера.
    """
    referrals = await crud.get_referrals_by_referrer_id(db, referrer_id)
    if not referrals:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="id не найден")
    return referrals
