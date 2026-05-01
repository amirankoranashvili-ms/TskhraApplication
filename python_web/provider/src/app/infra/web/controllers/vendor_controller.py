"""FastAPI controllers for vendor profile and product management.

Defines API endpoints for seller registration, product CRUD,
image management, and product submission workflows.
"""

from typing import Annotated, Any
from uuid import UUID

from backend_common.error_handlers import merge_responses
from backend_common.storage.validation import validate_upload_files
from fastapi import APIRouter, Depends, File, Path, Query, UploadFile, status
from pydantic import BaseModel, Field
from sqlalchemy import text

from src.app.core.products.interactors.create_product import CreateProductCommand
from src.app.core.products.interactors.delete_draft import DeleteDraftCommand
from src.app.core.products.interactors.delete_images import DeleteImagesCommand
from src.app.core.products.interactors.submit_product import SubmitProductCommand
from src.app.core.products.interactors.update_draft import UpdateDraftCommand
from src.app.core.products.interactors.update_product import UpdateProductCommand
from src.app.core.products.interactors.upload_images import (
    ImageFile,
    UploadImagesCommand,
)
from src.app.core.schemas.product_schemas import (
    DeleteImagesRequest,
    ProductCreateRequest,
    ProductUpdate,
)
from src.app.core.schemas.seller_schemas import (
    PlatformSellerCreate,
    PlatformSellersResponse,
)
from src.app.core.sellers.entities import PlatformSeller
from src.app.infra.auth.auth import get_current_user_id, require_kyc_verified
from src.app.infra.database.config import engine
from src.app.infra.web.dependables import (
    CreateProductUseCaseDep,
    DeleteDraftUseCaseDep,
    DeleteImagesUseCaseDep,
    RegisterSellerDep,
    SellerServiceDep,
    SubmitProductUseCaseDep,
    UpdateDraftUseCaseDep,
    UpdateProductUseCaseDep,
    UploadImagesUseCaseDep,
    VendorProductServiceDep,
)
from src.app.infra.web.handler import (
    CatalogServiceUnavailableResponse,
    DraftAlreadyExistsResponse,
    InvalidDraftDataResponse,
    InvalidIbanResponse,
    InvalidIdentificationNumberResponse,
    KycVerificationRequiredResponse,
    NoImagesResponse,
    NotAuthenticatedResponse,
    SellerAlreadyExistsResponse,
    SellerDataUnchangedResponse,
    SellerNotFoundResponse,
    SellerRegistrationPendingResponse,
    TaskNotDraftResponse,
    TaskNotFoundResponse,
)

sellers_api = APIRouter(prefix="", tags=["Vendor Profiles"])


@sellers_api.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    """Health check endpoint verifying database connectivity.

    Returns:
        Dict with status "ok" if the database is reachable.
    """
    async with engine.connect() as conn:
        await conn.execute(text("SELECT 1"))
    return {"status": "ok"}


@sellers_api.post(
    "/profile",
    status_code=status.HTTP_201_CREATED,
    responses=merge_responses(
        SellerAlreadyExistsResponse,
        SellerRegistrationPendingResponse,
        SellerDataUnchangedResponse,
        InvalidIbanResponse,
        InvalidIdentificationNumberResponse,
        NotAuthenticatedResponse,
        KycVerificationRequiredResponse,
    ),
)
async def register_seller_profile(
    seller_data: PlatformSellerCreate,
    interactor: RegisterSellerDep,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    _: Annotated[None, Depends(require_kyc_verified)],
) -> PlatformSeller:
    """Register a new seller profile for the authenticated user.

    Args:
        seller_data: Seller registration data.
        interactor: Register seller interactor dependency.
        user_id: Authenticated user's UUID.

    Returns:
        The created or updated seller profile.
    """
    seller = PlatformSeller(
        supplier_id=-1,
        user_id=user_id,
        **seller_data.model_dump(),
    )
    return await interactor.execute(seller)


@sellers_api.get(
    "/profile",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
    ),
)
async def get_my_seller_profiles(
    service: SellerServiceDep,
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> PlatformSellersResponse:
    """Get all seller profiles for the authenticated user.

    Args:
        service: Seller service dependency.
        user_id: Authenticated user's UUID.

    Returns:
        Response containing the list of seller profiles.
    """
    return PlatformSellersResponse(sellers=await service.get_seller_profiles(user_id))


@sellers_api.get(
    "/profile/{supplier_id}",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        SellerNotFoundResponse,
        NotAuthenticatedResponse,
    ),
)
async def get_my_seller_profile(
    service: SellerServiceDep,
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> PlatformSeller:
    """Get a specific seller profile by supplier ID.

    Args:
        service: Seller service dependency.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.

    Returns:
        The matching seller profile.
    """
    return await service.get_seller_profile(user_id, supplier_id)


class VerifyIdentificationRequest(BaseModel):
    identification_number: str = Field(..., min_length=9, max_length=11)


@sellers_api.post(
    "/profile/verify-identification",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        InvalidIdentificationNumberResponse,
    ),
)
async def verify_identification_number(
    body: VerifyIdentificationRequest,
    interactor: RegisterSellerDep,
) -> dict[str, Any]:
    """Verify an identification number against the business registry.

    Args:
        body: Request body with identification_number.
        interactor: Register seller interactor (used for its registry validator).

    Returns:
        Dict with valid=True if the identification number is found.
    """
    await interactor.registry_validator.validate(body.identification_number)
    return {"valid": True, "identification_number": body.identification_number}


vendor_products_api = APIRouter(
    prefix="/{supplier_id}/products", tags=["Vendor Products"]
)


@vendor_products_api.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
    ),
)
async def create_product(
    use_case: CreateProductUseCaseDep,
    seller_service: SellerServiceDep,
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_data: ProductCreateRequest,
) -> dict[str, Any]:
    """Create a new product draft for the vendor.

    Args:
        use_case: Create product use case dependency.
        seller_service: Seller service for authorization.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        product_data: Product creation request data.

    Returns:
        Dict with draft status, task ID, and confirmation message.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)

    command = CreateProductCommand(
        supplier_id=supplier_id,
        product_data=product_data,
    )

    return await use_case.execute(command)


@vendor_products_api.patch(
    "/{task_id}/draft",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        TaskNotFoundResponse,
        TaskNotDraftResponse,
    ),
)
async def update_draft(
    use_case: UpdateDraftUseCaseDep,
    seller_service: SellerServiceDep,
    task_id: Annotated[UUID, Path(..., description="The task ID")],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_data: ProductUpdate,
) -> dict[str, Any]:
    """Update product fields in an existing draft task.

    Args:
        use_case: Update draft use case dependency.
        seller_service: Seller service for authorization.
        task_id: UUID of the draft task.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        product_data: Partial product update data.

    Returns:
        Dict with draft status and confirmation message.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)

    command = UpdateDraftCommand(
        supplier_id=supplier_id,
        task_id=task_id,
        product_data=product_data,
    )

    return await use_case.execute(command)


@vendor_products_api.put(
    "/{product_id}",
    status_code=status.HTTP_201_CREATED,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        CatalogServiceUnavailableResponse,
        DraftAlreadyExistsResponse,
    ),
)
async def update_product(
    use_case: UpdateProductUseCaseDep,
    seller_service: SellerServiceDep,
    product_id: Annotated[
        int, Path(..., description="The ID of the product to update")
    ],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    product_data: ProductUpdate,
) -> dict[str, Any]:
    """Create an update draft for an existing product.

    Args:
        use_case: Update product use case dependency.
        seller_service: Seller service for authorization.
        product_id: ID of the product to update.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        product_data: Product update data.

    Returns:
        Dict with draft status, task ID, and confirmation message.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)

    command = UpdateProductCommand(
        supplier_id=supplier_id,
        product_id=product_id,
        product_data=product_data,
    )

    return await use_case.execute(command)


@vendor_products_api.post(
    "/{task_id}/images",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        TaskNotFoundResponse,
        TaskNotDraftResponse,
    ),
)
async def upload_task_images(
    use_case: UploadImagesUseCaseDep,
    seller_service: SellerServiceDep,
    task_id: Annotated[UUID, Path(..., description="The task ID")],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    images: list[UploadFile] = File(...),
) -> dict[str, Any]:
    """Upload images to a product draft task.

    Args:
        use_case: Upload images use case dependency.
        seller_service: Seller service for authorization.
        task_id: UUID of the draft task.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        images: List of uploaded image files.

    Returns:
        Dict with draft status, image URLs, and cover image URL.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)
    await validate_upload_files(images, max_files=5)

    image_files = []
    for file in images:
        if file.filename:
            content = await file.read()
            image_files.append(ImageFile(content=content, filename=file.filename))

    command = UploadImagesCommand(
        supplier_id=supplier_id,
        task_id=task_id,
        image_files=image_files,
    )

    return await use_case.execute(command)


@vendor_products_api.delete(
    "/{task_id}/images",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        TaskNotFoundResponse,
        TaskNotDraftResponse,
    ),
)
async def delete_task_images(
    use_case: DeleteImagesUseCaseDep,
    seller_service: SellerServiceDep,
    task_id: Annotated[UUID, Path(..., description="The task ID")],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    body: DeleteImagesRequest,
) -> dict[str, Any]:
    """Delete images from a product draft task.

    Args:
        use_case: Delete images use case dependency.
        seller_service: Seller service for authorization.
        task_id: UUID of the draft task.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        body: Request body with image URLs to delete.

    Returns:
        Dict with draft status and remaining images.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)

    command = DeleteImagesCommand(
        supplier_id=supplier_id,
        task_id=task_id,
        image_urls=body.image_urls,
    )

    return await use_case.execute(command)


@vendor_products_api.delete(
    "/{task_id}/draft",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        TaskNotFoundResponse,
        TaskNotDraftResponse,
    ),
)
async def delete_draft(
    use_case: DeleteDraftUseCaseDep,
    seller_service: SellerServiceDep,
    task_id: Annotated[UUID, Path(..., description="The task ID")],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    """Delete a product draft task.

    Args:
        use_case: Delete draft use case dependency.
        seller_service: Seller service for authorization.
        task_id: UUID of the draft task to delete.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.

    Returns:
        Dict with deletion confirmation.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)

    command = DeleteDraftCommand(
        supplier_id=supplier_id,
        task_id=task_id,
    )

    return await use_case.execute(command)


@vendor_products_api.post(
    "/{task_id}/submit",
    status_code=status.HTTP_202_ACCEPTED,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        TaskNotFoundResponse,
        TaskNotDraftResponse,
        NoImagesResponse,
        InvalidDraftDataResponse,
    ),
)
async def submit_product(
    use_case: SubmitProductUseCaseDep,
    seller_service: SellerServiceDep,
    task_id: Annotated[UUID, Path(..., description="The task ID")],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, Any]:
    """Submit a product draft for review.

    Args:
        use_case: Submit product use case dependency.
        seller_service: Seller service for authorization.
        task_id: UUID of the draft task to submit.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.

    Returns:
        Dict with pending status and confirmation message.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)

    command = SubmitProductCommand(
        supplier_id=supplier_id,
        task_id=task_id,
    )

    return await use_case.execute(command)


@vendor_products_api.delete(
    "/{product_id}",
    status_code=status.HTTP_202_ACCEPTED,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
    ),
)
async def delete_product(
    service: VendorProductServiceDep,
    seller_service: SellerServiceDep,
    product_id: Annotated[
        int, Path(..., description="The ID of the product to delete")
    ],
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
) -> dict[str, str]:
    """Delete a product by publishing a deletion event.

    Args:
        service: Vendor product service dependency.
        seller_service: Seller service for authorization.
        product_id: ID of the product to delete.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.

    Returns:
        Dict with pending deletion status.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)
    return await service.delete_product(supplier_id, product_id)


@vendor_products_api.get(
    "/",
    status_code=status.HTTP_200_OK,
    responses=merge_responses(
        NotAuthenticatedResponse,
        SellerNotFoundResponse,
        CatalogServiceUnavailableResponse,
    ),
)
async def get_my_products(
    service: VendorProductServiceDep,
    seller_service: SellerServiceDep,
    supplier_id: Annotated[int, Path(..., description="The ID of the vendor/supplier")],
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
) -> dict[str, Any]:
    """Get combined live and draft products for the vendor.

    Args:
        service: Vendor product service dependency.
        seller_service: Seller service for authorization.
        supplier_id: ID of the vendor/supplier.
        user_id: Authenticated user's UUID.
        page: Page number for live product pagination.
        limit: Number of live products per page.

    Returns:
        Dict containing live_products and drafts lists.
    """
    await seller_service.get_seller_profile(user_id, supplier_id)
    return await service.get_my_products(supplier_id, page, limit)
