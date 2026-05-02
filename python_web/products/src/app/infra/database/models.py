"""SQLAlchemy ORM models for the products service.

Defines all database tables including products, categories, brands,
fields, specifications, suppliers, and verification requests.
"""

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    func,
    DateTime,
    DECIMAL,
    CheckConstraint,
    UUID,
)
from sqlalchemy.orm import relationship
from backend_common.database.base import Base


class FieldGroupDb(Base):
    """ORM model for specification field groups."""

    __tablename__ = "field_groups"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    fields = relationship("FieldDb", back_populates="group")


class FieldDb(Base):
    """ORM model for specification fields belonging to a group."""

    __tablename__ = "fields"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    group_id = Column(
        Integer, ForeignKey("field_groups.id", ondelete="SET NULL"), nullable=True
    )

    group = relationship("FieldGroupDb", back_populates="fields")
    options = relationship(
        "FieldOptionDb", back_populates="field", cascade="all, delete"
    )
    category_fields = relationship(
        "CategoryFieldDb", back_populates="field", cascade="all, delete"
    )


class FieldOptionDb(Base):
    """ORM model for selectable options within a specification field."""

    __tablename__ = "field_options"
    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    value = Column(String(255), nullable=False)

    field = relationship("FieldDb", back_populates="options")


class CategoryFieldDb(Base):
    """ORM model linking categories to their specification fields."""

    __tablename__ = "category_fields"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    field_id = Column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    option_id = Column(
        Integer, ForeignKey("field_options.id", ondelete="CASCADE"), nullable=True
    )
    is_required = Column(Boolean, default=False)

    field = relationship("FieldDb", back_populates="category_fields")
    option = relationship("FieldOptionDb")
    category = relationship("CategoryDb", back_populates="category_fields")


class CategoryDb(Base):
    """ORM model for product categories with hierarchical parent-child support."""

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), nullable=False, unique=True)
    image_url = Column(String(2048), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    parent = relationship(
        "CategoryDb", back_populates="subcategories", remote_side="[CategoryDb.id]"
    )
    subcategories = relationship("CategoryDb", back_populates="parent")

    category_fields = relationship(
        "CategoryFieldDb", back_populates="category", cascade="all, delete"
    )

    brand_categories = relationship(
        "BrandCategoryDb", back_populates="category", cascade="all, delete-orphan"
    )
    brands = relationship("BrandDb", secondary="brand_categories", viewonly=True)


class SupplierDb(Base):
    """ORM model for product suppliers (external or internal)."""

    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)

    supplier_type = Column(String(50), nullable=False)

    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "supplier_type IN ('external', 'internal')", name="check_supplier_type"
        ),
    )

    platform_seller_details = relationship(
        "PlatformSellerDb", back_populates="supplier", uselist=False
    )


class PlatformSellerDb(Base):
    """ORM model for platform seller details tied to a supplier."""

    __tablename__ = "platform_sellers"

    supplier_id = Column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False)
    identification_number = Column(String(50), nullable=False)
    legal_address = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    bank_account_number = Column(String(50))
    is_active = Column(Boolean, default=False)

    supplier = relationship("SupplierDb", back_populates="platform_seller_details")


class BrandCategoryDb(Base):
    """ORM model for the many-to-many relationship between brands and categories."""

    __tablename__ = "brand_categories"

    brand_id = Column(
        Integer, ForeignKey("brands.id", ondelete="CASCADE"), primary_key=True
    )
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True
    )

    brand = relationship("BrandDb", back_populates="brand_categories")
    category = relationship("CategoryDb", back_populates="brand_categories")


class BrandDb(Base):
    """ORM model for product brands."""

    __tablename__ = "brands"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    logo_url = Column(String(2048))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    brand_categories = relationship(
        "BrandCategoryDb", back_populates="brand", cascade="all, delete-orphan"
    )
    categories = relationship("CategoryDb", secondary="brand_categories", viewonly=True)


class ProductImageDb(Base):
    """ORM model for product gallery images."""

    __tablename__ = "product_images"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    image_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=func.now())

    product = relationship("ProductDb", back_populates="images")


class ProductDb(Base):
    """ORM model for the main products table."""

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="NO ACTION"), nullable=False
    )
    supplier_id = Column(
        Integer, ForeignKey("suppliers.id", ondelete="NO ACTION"), nullable=False
    )
    brand_id = Column(
        Integer, ForeignKey("brands.id", ondelete="NO ACTION"), nullable=False
    )

    cover_image_url = Column(String(2048), nullable=True)

    title = Column(String(255), nullable=False)
    description = Column(String, nullable=True)

    price = Column(DECIMAL(10, 2), nullable=False)
    cost_price = Column(DECIMAL(10, 2), nullable=False, default=0)

    sku = Column(String(100), nullable=False, unique=True)
    stock_quantity = Column(Integer, nullable=False, default=0)
    original_url = Column(String(2048), nullable=True)

    is_scrapped = Column(Boolean, default=False)

    is_active = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    category = relationship("CategoryDb")
    supplier = relationship("SupplierDb")
    brand = relationship("BrandDb")

    images = relationship(
        "ProductImageDb",
        back_populates="product",
        foreign_keys="[ProductImageDb.product_id]",
        cascade="all, delete-orphan",
    )

    field_values = relationship(
        "ProductFieldValueDb", back_populates="product", cascade="all, delete-orphan"
    )


class ProductFieldValueDb(Base):
    """ORM model for product specification field values."""

    __tablename__ = "product_field_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    field_id = Column(
        Integer, ForeignKey("fields.id", ondelete="NO ACTION"), nullable=False
    )
    option_id = Column(
        Integer, ForeignKey("field_options.id", ondelete="NO ACTION"), nullable=False
    )

    product = relationship("ProductDb", back_populates="field_values")
    field = relationship("FieldDb")
    option = relationship("FieldOptionDb")


class VerificationRequestDb(Base):
    """ORM model for product and seller verification requests."""

    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_type = Column(String(30), nullable=False)
    status = Column(
        String(20), nullable=False, default="PENDING", server_default="PENDING"
    )
    supplier_id = Column(
        Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    resolved_by_admin_id = Column(String(36), nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now(), server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
