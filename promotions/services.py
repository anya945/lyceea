from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_UP

from django.utils import timezone

from .constants import (
    DISCOUNT_TYPE_FIXED,
    DISCOUNT_TYPE_PERCENT,
    PROMOTION_TYPE_COUPON,
    PROMOTION_TYPE_FREE_SHIPPING,
    PROMOTION_TYPE_MEMBER,
)
from .models import Promotion


MONEY_ZERO = Decimal("0.00")
MONEY_STEP = Decimal("0.01")


@dataclass
class PromotionResult:
    subtotal: Decimal
    shipping_cost: Decimal
    discount_amount: Decimal = MONEY_ZERO
    shipping_discount: Decimal = MONEY_ZERO
    grand_total: Decimal = MONEY_ZERO
    coupon_code: str = ""
    is_valid: bool = True
    message: str = ""
    applied_promotions: list = field(
        default_factory=list,
    )

    def as_snapshot(self):
        return {
            "subtotal": str(
                self.subtotal
            ),
            "shipping_cost": str(
                self.shipping_cost
            ),
            "coupon_code": self.coupon_code,
            "discount_amount": str(
                self.discount_amount
            ),
            "shipping_discount": str(
                self.shipping_discount
            ),
            "grand_total": str(
                self.grand_total
            ),
            "applied_promotions": (
                self.applied_promotions
            ),
        }


class PromotionEngine:
    @classmethod
    def evaluate(
        cls,
        subtotal,
        shipping_cost,
        user=None,
        coupon_code="",
    ):
        subtotal = cls._money(subtotal)
        shipping_cost = cls._money(
            shipping_cost
        )

        coupon_code = (
            coupon_code.strip().upper()
            if coupon_code
            else ""
        )

        result = PromotionResult(
            subtotal=subtotal,
            shipping_cost=shipping_cost,
        )

        now = timezone.now()

        promotions = list(
            Promotion.objects
            .filter(is_active=True)
            .order_by(
                "priority",
                "-created_at",
            )
        )

        eligible_discounts = []
        eligible_shipping = []

        coupon_found = False

        for promotion in promotions:
            if not promotion.is_available(now):
                continue

            if (
                subtotal
                < promotion.minimum_subtotal
            ):
                continue

            if (
                promotion.promotion_type
                == PROMOTION_TYPE_MEMBER
                and not cls._is_authenticated(
                    user
                )
            ):
                continue

            if (
                promotion.promotion_type
                == PROMOTION_TYPE_COUPON
            ):
                if not coupon_code:
                    continue

                promotion_code = (
                    promotion.code or ""
                ).strip().upper()

                if (
                    promotion_code
                    != coupon_code
                ):
                    continue

                coupon_found = True

            if (
                promotion.promotion_type
                == PROMOTION_TYPE_FREE_SHIPPING
            ):
                eligible_shipping.append(
                    promotion
                )
                continue

            discount = cls._calculate_discount(
                promotion=promotion,
                subtotal=subtotal,
            )

            if discount > MONEY_ZERO:
                eligible_discounts.append(
                    (
                        promotion,
                        discount,
                    )
                )

        if coupon_code and not coupon_found:
            result.is_valid = False
            result.message = (
                "ไม่พบคูปอง "
                "คูปองหมดอายุ "
                "หรือไม่ผ่านเงื่อนไข"
            )

        selected_discount = (
            cls._select_discount(
                eligible_discounts
            )
        )

        if selected_discount:
            promotion, discount = (
                selected_discount
            )

            result.discount_amount = (
                discount
            )

            if (
                promotion.promotion_type
                == PROMOTION_TYPE_COUPON
            ):
                result.coupon_code = (
                    promotion.code or ""
                )

            result.applied_promotions.append(
                cls._promotion_snapshot(
                    promotion=promotion,
                    discount_amount=discount,
                    shipping_discount=(
                        MONEY_ZERO
                    ),
                )
            )

        if eligible_shipping:
            shipping_promotion = (
                eligible_shipping[0]
            )

            result.shipping_discount = (
                shipping_cost
            )

            result.applied_promotions.append(
                cls._promotion_snapshot(
                    promotion=(
                        shipping_promotion
                    ),
                    discount_amount=(
                        MONEY_ZERO
                    ),
                    shipping_discount=(
                        shipping_cost
                    ),
                )
            )

        result.grand_total = cls._money(
            subtotal
            + shipping_cost
            - result.discount_amount
            - result.shipping_discount
        )

        if result.grand_total < MONEY_ZERO:
            result.grand_total = (
                MONEY_ZERO
            )

        if (
            result.applied_promotions
            and not result.message
        ):
            result.message = (
                "ใช้โปรโมชั่นเรียบร้อยแล้ว"
            )

        return result

    @classmethod
    def consume(
        cls,
        result,
    ):
        promotion_ids = {
            item.get("id")
            for item
            in result.applied_promotions
            if item.get("id")
        }

        if not promotion_ids:
            return

        promotions = (
            Promotion.objects
            .select_for_update()
            .filter(
                id__in=promotion_ids
            )
        )

        promotions_by_id = {
            promotion.id: promotion
            for promotion in promotions
        }

        for promotion_id in promotion_ids:
            promotion = (
                promotions_by_id.get(
                    promotion_id
                )
            )

            if promotion is None:
                raise ValueError(
                    "ไม่พบข้อมูลโปรโมชั่น"
                )

            if not promotion.is_active:
                raise ValueError(
                    f"โปรโมชั่น "
                    f"{promotion.name} "
                    "ถูกปิดใช้งานแล้ว"
                )

            if (
                promotion.usage_limit
                is not None
                and promotion.used_count
                >= promotion.usage_limit
            ):
                raise ValueError(
                    f"โปรโมชั่น "
                    f"{promotion.name} "
                    "ถูกใช้ครบจำนวนแล้ว"
                )

            promotion.used_count += 1

            promotion.save(
                update_fields=[
                    "used_count",
                    "updated_at",
                ]
            )

    @staticmethod
    def _is_authenticated(user):
        return bool(
            user
            and getattr(
                user,
                "is_authenticated",
                False,
            )
        )

    @classmethod
    def _calculate_discount(
        cls,
        promotion,
        subtotal,
    ):
        if (
            promotion.discount_type
            == DISCOUNT_TYPE_PERCENT
        ):
            discount = (
                subtotal
                * promotion.discount_value
                / Decimal("100")
            )

        elif (
            promotion.discount_type
            == DISCOUNT_TYPE_FIXED
        ):
            discount = (
                promotion.discount_value
            )

        else:
            discount = MONEY_ZERO

        if (
            promotion.maximum_discount
            is not None
            and discount
            > promotion.maximum_discount
        ):
            discount = (
                promotion.maximum_discount
            )

        if discount > subtotal:
            discount = subtotal

        return cls._money(discount)

    @staticmethod
    def _select_discount(candidates):
        if not candidates:
            return None

        return max(
            candidates,
            key=lambda item: (
                item[1],
                -item[0].priority,
            ),
        )

    @staticmethod
    def _promotion_snapshot(
        promotion,
        discount_amount,
        shipping_discount,
    ):
        return {
            "id": promotion.pk,
            "name": promotion.name,
            "type": (
                promotion.promotion_type
            ),
            "code": (
                promotion.code or ""
            ),
            "discount_amount": str(
                discount_amount
            ),
            "shipping_discount": str(
                shipping_discount
            ),
        }

    @staticmethod
    def _money(value):
        return Decimal(
            str(value or 0)
        ).quantize(
            MONEY_STEP,
            rounding=ROUND_HALF_UP,
        )