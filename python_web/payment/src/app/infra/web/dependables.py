"""FastAPI dependency injection factories for the payment service."""

from typing import Annotated

from backend_common.cache.service import CacheService
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.facades.order_facade import OrderFacade
from src.app.infra.broker.publisher import KafkaEventPublisher
from src.app.core.interactors.create_order_internal import CreateOrderInternalInteractor
from src.app.core.interactors.get_order_history import GetOrderHistoryInteractor
from src.app.core.interactors.handle_webhook import HandleWebhookInteractor
from src.app.core.interactors.process_payment import ProcessPaymentInteractor
from src.app.core.interactors.verify_payment import VerifyPaymentInteractor
from src.app.core.order.service import OrderService
from src.app.core.payment.gateway import IPaymentGateway
from src.app.core.payment.service import PaymentService
from src.app.infra.database.config import session_factory
from src.app.infra.database.repositories import (
    SqlAlchemyOrderRepository,
    SqlAlchemyPaymentRepository,
)

# Set during app startup
_publisher: KafkaEventPublisher | None = None
_payment_gateway: IPaymentGateway | None = None
_cache_service: CacheService | None = None


def init_payment_deps(
    publisher: KafkaEventPublisher,
    payment_gateway: IPaymentGateway,
    cache_service: CacheService,
) -> None:
    global _publisher, _payment_gateway, _cache_service
    _publisher = publisher
    _payment_gateway = payment_gateway
    _cache_service = cache_service


def _get_publisher() -> KafkaEventPublisher:
    """Return the initialized event publisher or raise if not set."""
    if _publisher is None:
        raise RuntimeError("EventPublisher not initialized")
    return _publisher


def _get_payment_gateway() -> IPaymentGateway:
    """Return the initialized payment gateway or raise if not set."""
    if _payment_gateway is None:
        raise RuntimeError("PaymentGateway not initialized")
    return _payment_gateway


def _get_cache_service() -> CacheService:
    if _cache_service is None:
        raise RuntimeError("CacheService not initialized")
    return _cache_service


async def get_db() -> AsyncSession:
    """Yield a database session, committing on success or rolling back on error."""
    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def _build_order_service(session: AsyncSession) -> OrderService:
    """Build an OrderService wired to the given session."""
    repo = SqlAlchemyOrderRepository(session)
    return OrderService(order_repository=repo)


def _build_payment_service(session: AsyncSession) -> PaymentService:
    """Build a PaymentService wired to the given session and gateway."""
    repo = SqlAlchemyPaymentRepository(session)
    return PaymentService(
        payment_repository=repo,
        payment_gateway=_get_payment_gateway(),
        cache=_get_cache_service(),
    )


def _build_order_facade(session: AsyncSession) -> OrderFacade:
    """Build an OrderFacade with all required services for the given session."""
    return OrderFacade(
        order_service=_build_order_service(session),
        payment_service=_build_payment_service(session),
        publisher=_get_publisher(),
    )


async def get_order_history_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> GetOrderHistoryInteractor:
    """FastAPI dependency that provides a GetOrderHistoryInteractor."""
    return GetOrderHistoryInteractor(order_service=_build_order_service(session))


async def get_process_payment_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> ProcessPaymentInteractor:
    """FastAPI dependency that provides a ProcessPaymentInteractor."""
    return ProcessPaymentInteractor(facade=_build_order_facade(session))


async def get_verify_payment_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> VerifyPaymentInteractor:
    """FastAPI dependency that provides a VerifyPaymentInteractor."""
    return VerifyPaymentInteractor(facade=_build_order_facade(session))


async def get_webhook_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> HandleWebhookInteractor:
    """FastAPI dependency that provides a HandleWebhookInteractor."""
    return HandleWebhookInteractor(
        order_service=_build_order_service(session),
        payment_repository=SqlAlchemyPaymentRepository(session),
        publisher=_get_publisher(),
    )


async def get_order_detail_service(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> OrderService:
    """FastAPI dependency that provides an OrderService for detail lookups."""
    return _build_order_service(session)


async def get_create_order_interactor(
    session: Annotated[AsyncSession, Depends(get_db)],
) -> CreateOrderInternalInteractor:
    """FastAPI dependency that provides a CreateOrderInternalInteractor."""
    return CreateOrderInternalInteractor(facade=_build_order_facade(session))


# Typed dependency aliases
CreateOrderDep = Annotated[
    CreateOrderInternalInteractor, Depends(get_create_order_interactor)
]
OrderHistoryDep = Annotated[
    GetOrderHistoryInteractor, Depends(get_order_history_interactor)
]
ProcessPaymentDep = Annotated[
    ProcessPaymentInteractor, Depends(get_process_payment_interactor)
]
VerifyPaymentDep = Annotated[
    VerifyPaymentInteractor, Depends(get_verify_payment_interactor)
]
WebhookDep = Annotated[HandleWebhookInteractor, Depends(get_webhook_interactor)]
OrderServiceDep = Annotated[OrderService, Depends(get_order_detail_service)]
