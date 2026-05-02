"""FastAPI dependency injection configuration for the cart service.

Provides factory functions and typed dependency aliases for injecting
interactors, services, and infrastructure components into route handlers.
"""

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from aiokafka import AIOKafkaProducer

from src.app.core.cart.service import CartService
from src.app.core.facades.catalog_facade import CatalogFacade
from src.app.core.interactors.add_to_cart import AddToCartInteractor
from src.app.core.interactors.checkout import CheckoutInteractor
from src.app.core.interactors.clear_cart import ClearCartInteractor
from src.app.core.interactors.get_cart import GetCartInteractor
from src.app.core.interactors.remove_from_cart import RemoveFromCartInteractor
from src.app.core.interactors.update_cart_item import UpdateCartItemInteractor
from src.app.infra.database.config import session_factory
from src.app.infra.database.repositories import SqlAlchemyCartRepository

_producer: AIOKafkaProducer | None = None
_catalog_facade: CatalogFacade | None = None


def init_cart_deps(producer: AIOKafkaProducer, catalog_facade: CatalogFacade) -> None:
    global _producer, _catalog_facade
    _producer = producer
    _catalog_facade = catalog_facade


def _get_producer() -> AIOKafkaProducer:
    if _producer is None:
        raise RuntimeError("Kafka producer not initialized")
    return _producer


def _get_catalog_facade() -> CatalogFacade:
    """Retrieve the initialized catalog facade singleton.

    Returns:
        The CatalogFacade instance.

    Raises:
        RuntimeError: If the catalog facade has not been initialized.
    """
    if _catalog_facade is None:
        raise RuntimeError("CatalogFacade not initialized")
    return _catalog_facade


async def get_db() -> AsyncSession:
    """Provide a transactional database session as a FastAPI dependency.

    Yields:
        An async SQLAlchemy session that commits on success and rolls back on error.
    """
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _build_cart_service(session: AsyncSession) -> CartService:
    """Build a CartService instance with a repository bound to the given session.

    Args:
        session: The async database session.

    Returns:
        A configured CartService instance.
    """
    repo = SqlAlchemyCartRepository(session)
    return CartService(cart_repository=repo)


async def get_get_cart_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
    catalog_facade: Annotated[CatalogFacade, Depends(_get_catalog_facade)],
) -> GetCartInteractor:
    """FastAPI dependency that provides a GetCartInteractor.

    Args:
        session: Injected database session.
        catalog_facade: Injected catalog facade.

    Returns:
        A configured GetCartInteractor instance.
    """
    return GetCartInteractor(
        cart_service=_build_cart_service(session),
        catalog_facade=catalog_facade,
    )


async def get_add_to_cart_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
    catalog_facade: Annotated[CatalogFacade, Depends(_get_catalog_facade)],
) -> AddToCartInteractor:
    """FastAPI dependency that provides an AddToCartInteractor.

    Args:
        session: Injected database session.
        catalog_facade: Injected catalog facade.

    Returns:
        A configured AddToCartInteractor instance.
    """
    return AddToCartInteractor(
        cart_service=_build_cart_service(session),
        catalog_facade=catalog_facade,
    )


async def get_update_cart_item_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
    catalog_facade: Annotated[CatalogFacade, Depends(_get_catalog_facade)],
) -> UpdateCartItemInteractor:
    """FastAPI dependency that provides an UpdateCartItemInteractor.

    Args:
        session: Injected database session.
        catalog_facade: Injected catalog facade.

    Returns:
        A configured UpdateCartItemInteractor instance.
    """
    return UpdateCartItemInteractor(
        cart_service=_build_cart_service(session),
        catalog_facade=catalog_facade,
    )


async def get_clear_cart_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ClearCartInteractor:
    """FastAPI dependency that provides a ClearCartInteractor.

    Args:
        session: Injected database session.

    Returns:
        A configured ClearCartInteractor instance.
    """
    return ClearCartInteractor(cart_service=_build_cart_service(session))


async def get_remove_from_cart_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> RemoveFromCartInteractor:
    """FastAPI dependency that provides a RemoveFromCartInteractor.

    Args:
        session: Injected database session.

    Returns:
        A configured RemoveFromCartInteractor instance.
    """
    return RemoveFromCartInteractor(cart_service=_build_cart_service(session))


async def get_checkout_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
    producer: Annotated[AIOKafkaProducer, Depends(_get_producer)],
) -> CheckoutInteractor:
    return CheckoutInteractor(
        cart_service=_build_cart_service(session),
        producer=producer,
    )


GetCartDep = Annotated[GetCartInteractor, Depends(get_get_cart_interactor)]
AddToCartDep = Annotated[AddToCartInteractor, Depends(get_add_to_cart_interactor)]
UpdateCartItemDep = Annotated[
    UpdateCartItemInteractor, Depends(get_update_cart_item_interactor)
]
ClearCartDep = Annotated[ClearCartInteractor, Depends(get_clear_cart_interactor)]
RemoveFromCartDep = Annotated[
    RemoveFromCartInteractor, Depends(get_remove_from_cart_interactor)
]
CheckoutDep = Annotated[CheckoutInteractor, Depends(get_checkout_interactor)]
