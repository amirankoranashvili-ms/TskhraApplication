"""SQLAlchemy models for the vendor database."""

from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import DeclarativeBase


class VendorBase(DeclarativeBase):
    """Declarative base for vendor database models."""

    pass


class VendorSellerDb(VendorBase):
    """Database model for a seller in the vendor service database."""

    __tablename__ = "platform_sellers"

    supplier_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    user_id = Column(PgUUID(as_uuid=True), nullable=False, unique=True)
    identification_number = Column(String(50), nullable=False, unique=True)
    legal_address = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="pending")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
