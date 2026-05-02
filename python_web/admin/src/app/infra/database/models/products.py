"""SQLAlchemy models for the products database (categories, products, fields, sellers, verification)."""

from sqlalchemy import (
    DECIMAL,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

from src.app.infra.database.base import Base


class FieldGroupDb(Base):
    """Database model for grouping related product fields."""

    __tablename__ = "field_groups"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)

    fields = relationship("FieldDb", back_populates="group")


class FieldDb(Base):
    """Database model for a product specification field."""

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
    """Database model for a selectable option within a field."""

    __tablename__ = "field_options"

    id = Column(Integer, primary_key=True, autoincrement=True)
    field_id = Column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    value = Column(String(255), nullable=False)

    field = relationship("FieldDb", back_populates="options")


class CategoryFieldDb(Base):
    """Database model linking a field to a category with an optional required flag."""

    __tablename__ = "category_fields"

    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(
        Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False
    )
    field_id = Column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    is_required = Column(Boolean, default=False)

    __table_args__ = (
        UniqueConstraint("category_id", "field_id", name="uq_category_field"),
    )

    field = relationship("FieldDb", back_populates="category_fields")
    category = relationship("CategoryDb", back_populates="category_fields")


class CategoryDb(Base):
    """Database model for a product category with hierarchical parent support."""

    __tablename__ = "categories"

    image_upload = None

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

    def __repr__(self):
        return self.name or f"Category #{self.id}"


class SupplierDb(Base):
    """Database model for a product supplier."""

    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    supplier_type = Column(String(50), nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return self.name or f"Supplier #{self.id}"


class BrandDb(Base):
    """Database model for a product brand."""

    __tablename__ = "brands"

    logo_upload = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, unique=True)
    logo_url = Column(String(2048))
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())

    def __repr__(self):
        return self.name or f"Brand #{self.id}"


class ProductImageDb(Base):
    """Database model for an image associated with a product."""

    __tablename__ = "product_images"

    image_upload = None

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    image_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime, default=func.now())

    product = relationship("ProductDb", back_populates="images")


class ProductDb(Base):
    """Database model for a product listing in the marketplace."""

    __tablename__ = "products"

    cover_image_upload = None

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
    sell_type = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
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
        "ProductFieldValueDb",
        back_populates="product",
        cascade="all, delete-orphan",
    )


class ProductFieldValueDb(Base):
    """Database model for a specific field value chosen for a product."""

    __tablename__ = "product_field_values"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False
    )
    field_id = Column(
        Integer, ForeignKey("fields.id", ondelete="CASCADE"), nullable=False
    )
    option_id = Column(
        Integer, ForeignKey("field_options.id", ondelete="NO ACTION"), nullable=False
    )

    product = relationship("ProductDb", back_populates="field_values")
    field = relationship("FieldDb")
    option = relationship("FieldOptionDb")


class PlatformSellerDb(Base):
    """Database model for a platform seller linked to a supplier."""

    __tablename__ = "platform_sellers"

    supplier_id = Column(
        Integer, ForeignKey("suppliers.id", ondelete="CASCADE"), primary_key=True
    )
    user_id = Column(String(36), nullable=False)
    identification_number = Column(String(50), nullable=False)
    legal_address = Column(String(255), nullable=False)
    contact_phone = Column(String(50))
    contact_email = Column(String(255))
    bank_account_number = Column(String(50))
    is_active = Column(Boolean, default=False)

    supplier = relationship("SupplierDb")


class VerificationRequestDb(Base):
    """Database model for a seller or product verification request."""

    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)
    request_type = Column(String(30), nullable=False)
    status = Column(
        String(20), nullable=False, default="pending", server_default="pending"
    )
    supplier_id = Column(
        Integer, ForeignKey("suppliers.id", ondelete="SET NULL"), nullable=True
    )
    product_id = Column(
        Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True
    )
    resolved_by_admin_id = Column(String(36), nullable=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)

    supplier = relationship("SupplierDb")
    product = relationship("ProductDb")
