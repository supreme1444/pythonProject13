from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.app_database.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    user = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.now())

    referral_codes = relationship("ReferralCode", back_populates="user")
    referrals = relationship("Referral", back_populates="referrer", foreign_keys="Referral.referrer_id")


class ReferralCode(Base):
    __tablename__ = "referral_codes"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    code = Column(String, unique=True, index=True)
    expiration_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now())

    user = relationship("User", back_populates="referral_codes")


class Referral(Base):
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"))
    referral_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.now())

    referrer = relationship("User", back_populates="referrals", foreign_keys=[referrer_id])
