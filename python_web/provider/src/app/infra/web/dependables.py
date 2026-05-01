"""FastAPI dependency injection configuration.

Defines factory functions and typed dependency aliases for injecting
services, interactors, and use cases into API endpoint handlers.
"""

from typing import Annotated

import httpx
from backend_common.storage import MinioFileStorage, create_minio_client
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.config import settings
from src.app.core.orders.service import VendorOrderService
from src.app.core.products.interactors.create_product import CreateProductUseCase
from src.app.core.products.interactors.delete_draft import DeleteDraftUseCase
from src.app.core.products.interactors.delete_images import DeleteImagesUseCase
from src.app.core.products.interactors.submit_product import SubmitProductUseCase
from src.app.core.products.interactors.update_draft import UpdateDraftUseCase
from src.app.core.products.interactors.update_product import UpdateProductUseCase
from src.app.core.products.interactors.upload_images import UploadImagesUseCase
from src.app.core.products.service import VendorProductService
from src.app.core.sellers.interactors.register_seller import RegisterSellerInteractor
from src.app.core.sellers.service import SellerService
from src.app.infra.broker.publisher import ProductEventPublisher
from src.app.infra.database.config import get_db
from src.app.infra.database.repositories import (
    SqlAlchemyProductTaskRepository,
    SqlAlchemySellerRepository,
    SqlAlchemyVendorOrderRepository,
)
from src.app.infra.http_client.business_registry import StubBusinessRegistryValidator
from src.app.infra.http_client.catalog_client import get_catalog_http_client
from src.app.infra.http_client.iban_validator import StubIbanValidator
from src.app.infra.storage.minio_image_storage import MinioImageStorage

_minio_client = create_minio_client(
    endpoint=settings.MINIO_ENDPOINT,
    access_key=settings.MINIO_ACCESS_KEY,
    secret_key=settings.MINIO_SECRET_KEY,
    secure=settings.MINIO_SECURE,
)
_image_storage = MinioImageStorage(
    MinioFileStorage(_minio_client, settings.MINIO_BUCKET, settings.MINIO_PUBLIC_URL)
)

_iban_http_client: httpx.AsyncClient | None = None
_publisher: ProductEventPublisher | None = None


def init_publisher(pub: ProductEventPublisher) -> None:
    """Initialize the global event publisher singleton.

    Args:
        pub: ProductEventPublisher instance to use globally.
    """
    global _publisher
    _publisher = pub


def _get_publisher() -> ProductEventPublisher:
    """Get the global event publisher, raising if not initialized.

    Returns:
        The initialized ProductEventPublisher.

    Raises:
        RuntimeError: If the publisher has not been initialized.
    """
    if _publisher is None:
        raise RuntimeError("ProductEventPublisher not initialized")
    return _publisher


def init_iban_http_client() -> None:
    """Initialize the global HTTP client for IBAN and business registry validation."""
    global _iban_http_client
    _iban_http_client = httpx.AsyncClient(timeout=httpx.Timeout(5.0))


async def close_iban_http_client() -> None:
    """Close and clean up the global IBAN HTTP client."""
    global _iban_http_client
    if _iban_http_client:
        await _iban_http_client.aclose()
        _iban_http_client = None


def _get_iban_http_client() -> httpx.AsyncClient:
    """Get the global IBAN HTTP client, raising if not initialized.

    Returns:
        The initialized httpx AsyncClient.

    Raises:
        RuntimeError: If the client has not been initialized.
    """
    if _iban_http_client is None:
        raise RuntimeError("IBAN HTTP client not initialized")
    return _iban_http_client


def get_seller_service(db: AsyncSession = Depends(get_db)) -> SellerService:
    """Create a SellerService instance with database dependency.

    Args:
        db: Async database session.

    Returns:
        Configured SellerService instance.
    """
    repository = SqlAlchemySellerRepository(db)
    return SellerService(repository)


SellerServiceDep = Annotated[SellerService, Depends(get_seller_service)]


def get_register_seller_interactor(
    db: AsyncSession = Depends(get_db),
) -> RegisterSellerInteractor:
    """Create a RegisterSellerInteractor with all dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured RegisterSellerInteractor instance.
    """
    repository = SqlAlchemySellerRepository(db)
    iban_validator = StubIbanValidator()
    registry_validator = StubBusinessRegistryValidator()
    return RegisterSellerInteractor(
        repository=repository,
        publisher=_get_publisher(),
        iban_validator=iban_validator,
        registry_validator=registry_validator,
    )


RegisterSellerDep = Annotated[
    RegisterSellerInteractor, Depends(get_register_seller_interactor)
]


def get_vendor_product_service(
    db: AsyncSession = Depends(get_db),
) -> VendorProductService:
    """Create a VendorProductService with all dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured VendorProductService instance.
    """
    catalog_client = get_catalog_http_client()
    task_repo = SqlAlchemyProductTaskRepository(db)
    return VendorProductService(_get_publisher(), catalog_client, task_repo)


VendorProductServiceDep = Annotated[
    VendorProductService, Depends(get_vendor_product_service)
]


def get_create_product_use_case(
    db: AsyncSession = Depends(get_db),
) -> CreateProductUseCase:
    """Create a CreateProductUseCase with task repository.

    Args:
        db: Async database session.

    Returns:
        Configured CreateProductUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    return CreateProductUseCase(task_repo)


CreateProductUseCaseDep = Annotated[
    CreateProductUseCase, Depends(get_create_product_use_case)
]


def get_update_product_use_case(
    db: AsyncSession = Depends(get_db),
) -> UpdateProductUseCase:
    """Create an UpdateProductUseCase with dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured UpdateProductUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    catalog_client = get_catalog_http_client()
    return UpdateProductUseCase(task_repo, catalog_client)


UpdateProductUseCaseDep = Annotated[
    UpdateProductUseCase, Depends(get_update_product_use_case)
]


def get_upload_images_use_case(
    db: AsyncSession = Depends(get_db),
) -> UploadImagesUseCase:
    """Create an UploadImagesUseCase with dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured UploadImagesUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    return UploadImagesUseCase(task_repo, _image_storage)


UploadImagesUseCaseDep = Annotated[
    UploadImagesUseCase, Depends(get_upload_images_use_case)
]


def get_delete_images_use_case(
    db: AsyncSession = Depends(get_db),
) -> DeleteImagesUseCase:
    """Create a DeleteImagesUseCase with dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured DeleteImagesUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    return DeleteImagesUseCase(task_repo, _image_storage)


DeleteImagesUseCaseDep = Annotated[
    DeleteImagesUseCase, Depends(get_delete_images_use_case)
]


def get_submit_product_use_case(
    db: AsyncSession = Depends(get_db),
) -> SubmitProductUseCase:
    """Create a SubmitProductUseCase with dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured SubmitProductUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    return SubmitProductUseCase(task_repo, _get_publisher())


SubmitProductUseCaseDep = Annotated[
    SubmitProductUseCase, Depends(get_submit_product_use_case)
]


def get_update_draft_use_case(
    db: AsyncSession = Depends(get_db),
) -> UpdateDraftUseCase:
    """Create an UpdateDraftUseCase with task repository.

    Args:
        db: Async database session.

    Returns:
        Configured UpdateDraftUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    return UpdateDraftUseCase(task_repo)


UpdateDraftUseCaseDep = Annotated[
    UpdateDraftUseCase, Depends(get_update_draft_use_case)
]


def get_delete_draft_use_case(
    db: AsyncSession = Depends(get_db),
) -> DeleteDraftUseCase:
    """Create a DeleteDraftUseCase with task repository.

    Args:
        db: Async database session.

    Returns:
        Configured DeleteDraftUseCase instance.
    """
    task_repo = SqlAlchemyProductTaskRepository(db)
    return DeleteDraftUseCase(task_repo)


DeleteDraftUseCaseDep = Annotated[
    DeleteDraftUseCase, Depends(get_delete_draft_use_case)
]


def get_vendor_order_service(db: AsyncSession = Depends(get_db)) -> VendorOrderService:
    """Create a VendorOrderService with dependencies.

    Args:
        db: Async database session.

    Returns:
        Configured VendorOrderService instance.
    """
    repository = SqlAlchemyVendorOrderRepository(db)
    return VendorOrderService(repository=repository, publisher=_get_publisher())


VendorOrderServiceDep = Annotated[VendorOrderService, Depends(get_vendor_order_service)]
