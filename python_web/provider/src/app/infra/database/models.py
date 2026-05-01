"""SQLAlchemy ORM models for the provider service database.

Defines the database table mappings for platform sellers, product upload
tasks, vendor orders, and vendor order items.
"""

import uuid
from datetime import datetime, timezone

from backend_common.database.base import Base
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import Uuid


class PlatformSellerDb(Base):
    """ORM model for the platform_sellers table."""

    __tablename__ = "platform_sellers"

    supplier_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    user_id = Column(Uuid(as_uuid=True), nullable=False, unique=True, index=True)
    identification_number = Column(String(50), nullable=False, unique=True)
    legal_address = Column(String(255), nullable=False)
    contact_phone = Column(String(50), nullable=True)
    contact_email = Column(String(255), nullable=True)
    bank_account_number = Column(String(50), nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    upload_tasks = relationship("ProductUploadTaskDb", back_populates="seller")


class ProductUploadTaskDb(Base):
    """ORM model for the product_upload_tasks table."""

    __tablename__ = "product_upload_tasks"

    task_id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    supplier_id = Column(
        Integer, ForeignKey("platform_sellers.supplier_id"), nullable=False, index=True
    )
    product_id = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="PENDING")
    payload = Column(JSON, nullable=False)
    error_message = Column(String, nullable=True)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    seller = relationship("PlatformSellerDb", back_populates="upload_tasks")


class VendorOrderDb(Base):
    """ORM model for the vendor_orders table."""

    __tablename__ = "vendor_orders"
    __table_args__ = (
        UniqueConstraint(
            "order_id", "supplier_id", name="uq_vendor_order_per_supplier"
        ),
    )

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(Uuid(as_uuid=True), nullable=False, index=True)
    supplier_id = Column(
        Integer, ForeignKey("platform_sellers.supplier_id"), nullable=False, index=True
    )
    buyer_user_id = Column(Uuid(as_uuid=True), nullable=False)
    status = Column(String(20), nullable=False, default="PAID")
    vendor_subtotal = Column(Float, nullable=False, default=0.0)

    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    items = relationship(
        "VendorOrderItemDb", back_populates="vendor_order", cascade="all, delete-orphan"
    )
    seller = relationship("PlatformSellerDb")


class VendorOrderItemDb(Base):
    """ORM model for the vendor_order_items table."""

    __tablename__ = "vendor_order_items"

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vendor_order_id = Column(
        Uuid(as_uuid=True),
        ForeignKey("vendor_orders.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_id = Column(Integer, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    product_title = Column(String(500), nullable=False, default="")

    vendor_order = relationship("VendorOrderDb", back_populates="items")
