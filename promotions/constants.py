PROMOTION_TYPE_COUPON = "COUPON"
PROMOTION_TYPE_STOREWIDE = "STOREWIDE"
PROMOTION_TYPE_THRESHOLD = "THRESHOLD"
PROMOTION_TYPE_FREE_SHIPPING = "FREE_SHIPPING"
PROMOTION_TYPE_SEASONAL = "SEASONAL"
PROMOTION_TYPE_MEMBER = "MEMBER"


PROMOTION_TYPE_CHOICES = [
    (
        PROMOTION_TYPE_COUPON,
        "คูปองส่วนลด",
    ),
    (
        PROMOTION_TYPE_STOREWIDE,
        "ลดทั้งร้าน",
    ),
    (
        PROMOTION_TYPE_THRESHOLD,
        "ซื้อครบรับส่วนลด",
    ),
    (
        PROMOTION_TYPE_FREE_SHIPPING,
        "ส่งฟรี",
    ),
    (
        PROMOTION_TYPE_SEASONAL,
        "โปรโมชั่นตามเทศกาล",
    ),
    (
        PROMOTION_TYPE_MEMBER,
        "โปรโมชั่นสำหรับสมาชิก",
    ),
]


DISCOUNT_TYPE_PERCENT = "PERCENT"
DISCOUNT_TYPE_FIXED = "FIXED"
DISCOUNT_TYPE_NONE = "NONE"


DISCOUNT_TYPE_CHOICES = [
    (
        DISCOUNT_TYPE_PERCENT,
        "เปอร์เซ็นต์",
    ),
    (
        DISCOUNT_TYPE_FIXED,
        "จำนวนเงิน",
    ),
    (
        DISCOUNT_TYPE_NONE,
        "ไม่มีส่วนลดสินค้า",
    ),
]