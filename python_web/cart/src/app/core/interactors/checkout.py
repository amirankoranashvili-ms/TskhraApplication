import logging
from uuid import UUID

from aiokafka import AIOKafkaProducer

from src.app.core.cart.service import CartService
from src.app.core.schemas.responses import CheckoutResponse

logger = logging.getLogger(__name__)

CHECKOUT_TOPIC = "cart-events"


class CheckoutInteractor:
    def __init__(
        self,
        cart_service: CartService,
        producer: AIOKafkaProducer,
    ) -> None:
        self.cart_service = cart_service
        self.producer = producer

    async def execute(self, user_id: UUID) -> CheckoutResponse:
        cart = await self.cart_service.get_or_create_cart(user_id)
        total = self.cart_service.calculate_total(cart)

        checked_out_cart = await self.cart_service.checkout_cart(cart)

        order_items = [
            {
                "product_id": item.product_id,
                "quantity": item.quantity,
                "unit_price": item.unit_price,
                "product_title": item.product_title,
            }
            for item in checked_out_cart.items
        ]

        payload = {
            "event_type": "cart.checkout",
            "cart_id": str(checked_out_cart.id),
            "user_id": str(user_id),
            "items": order_items,
            "total_amount": total,
        }

        await self.producer.send_and_wait(
            CHECKOUT_TOPIC,
            value=payload,
            key=b"cart.checkout",
        )
        logger.info("Checkout event published for cart %s", cart.id)

        return CheckoutResponse(
            cart_id=checked_out_cart.id,
            status=checked_out_cart.status.value,
            total=total,
            item_count=len(checked_out_cart.items),
            message="Checkout successful. Order is being processed.",
        )
