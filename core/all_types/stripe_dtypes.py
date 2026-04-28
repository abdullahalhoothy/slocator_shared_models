from datetime import datetime, timedelta
from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator
from typing import Dict, List, TypeVar, Generic, Literal, Any, Optional, Union
from all_types.request_dtypes import ReqCityCountry
from all_types.internal_types import UserId
from preloaded_constants import ALL_POI_CATEGORIES, REPORTS_PACKAGES, AREA_INTELLIGENCE_CATEGORIES


class PriceReq(BaseModel):
    currency: str
    product_id: Optional[str] = None
    unit_amount: Optional[int] = None  # For flat fee
    pricing_type: Literal["flat", "tier"]  # "flat" or "tier"
    base_amount: Optional[int] = None  # For tier-based pricing
    included_seats: Optional[int] = None  # For tier-based pricing
    additional_seat_price: Optional[int] = None  # For tier-based pricing
    tiers: Optional[List[Dict[str, Any]]] = None  # tiers for seats
    recurring_interval: str
    recurring_interval_count: int


class PriceRes(BaseModel):
    price_id: str
    product_id: str
    currency: str
    unit_amount: Optional[int] = None
    base_amount: Optional[int] = None
    included_seats: Optional[int] = None
    additional_seat_price: Optional[int] = None
    recurring_interval: str
    recurring_interval_count: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(arbitrary_types_allowed=True)


class ProductRes(BaseModel):
    id: str
    object: str
    active: bool
    created: int
    price_id: Optional[str] = None
    description: Optional[str] = None
    images: List[str] = []
    marketing_features: List[str] = []
    livemode: bool
    metadata: Dict[str, Any] = {}
    name: str
    package_dimensions: Optional[Any] = None
    shippable: Optional[bool] = None
    statement_descriptor: Optional[str] = None
    tax_code: Optional[str] = None
    unit_label: Optional[str] = None
    updated: int
    url: Optional[str] = None
    price: Optional[PriceRes] = None  # Add the price field and make it optional


class ProductReq(BaseModel):
    class Metadata(BaseModel):
        seats: int = 1
        free_trial: bool = True
        free_trial_days: int = 7
        can_extend_seats: bool = False

    name: str
    price: Optional[PriceReq]
    active: Optional[bool] = None
    caption: Optional[str] = None
    description: Optional[str] = None
    images: Optional[List[str]] = []
    metadata: Metadata = Metadata()
    package_dimensions: Optional[Any] = None
    shippable: Optional[bool] = None
    statement_descriptor: Optional[str] = None
    tax_code: Optional[str] = None
    unit_label: Optional[str] = None
    url: Optional[str] = None
    price_id: Optional[str] = None
    id: Optional[str] = None

class Address(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None
    line1: Optional[str] = None
    line2: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None

# Customer
class CustomerReq(BaseModel):
    user_id: str
    phone: str
    address: Optional[Address] = None
    balance: Optional[int] = None
    currency: Optional[str] = None
    default_source: Optional[str] = None
    delinquent: Optional[bool] = None
    description: Optional[str] = None
    discount: Optional[Any] = None
    name: str = None
    email: str = None

    invoice_prefix: Optional[str] = None
    invoice_settings: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None



class CustomerRes(BaseModel):
    id: str
    object: str = "customer"
    address: Optional[Address] = None
    balance: Optional[int] = None
    created: int
    currency: Optional[str] = None
    default_source: Optional[str] = None
    delinquent: Optional[bool] = None
    description: Optional[str] = None
    discount: Optional[Any] = None
    email: Optional[str] = None
    invoice_prefix: Optional[str] = None
    invoice_settings: Optional[Dict[str, Any]] = None
    livemode: Optional[bool] = None
    metadata: Optional[Dict[str, Any]] = None
    name: Optional[str] = None
    next_invoice_sequence: Optional[int] = None
    phone: Optional[str] = None
    preferred_locales: Optional[List[str]] = None
    shipping: Optional[Any] = None
    tax_exempt: Optional[str] = None
    test_clock: Optional[str] = None


class SubscriptionCreateReq(BaseModel):
    user_id: str
    product_id: str
    seats: int = 1
    payment_method_id: Optional[str] = None


class SubscriptionUpdateReq(BaseModel):
    seats: int


class SubscriptionRes(BaseModel):
    subscription: dict
    subscription_id: str
    status: str
    seats: Optional[int] = None
    product_id: Optional[str] = ''
    customer_id: Optional[str] = ''

class BillingDetails(BaseModel):
    address: Optional[Address] = None
    email: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None

class Card(BaseModel):
    number: int
    exp_month: str
    exp_year: str
    cvc: str


# Pydantic model for payment method creation
class PaymentMethodReq(BaseModel):
    type: str = "card"
    card: Card  # Card
    billing_details: Optional[BillingDetails] = {}



# Pydantic model for payment method response
class PaymentMethodRes(BaseModel):
    id: str
    type: str
    customer: str
    billing_details: Optional[BillingDetails] = {}


class PaymentMethodUpdateReq(BaseModel):
    billing_details: Optional[BillingDetails]


class PaymentMethodAttachReq(BaseModel):
    user_id: str
    payment_method_id: str

class TopUpWalletReq(BaseModel):
    user_id: str
    amount: Union[int, float]

class DeductWalletReq(BaseModel):
    user_id: str
    amount: Union[int, float]


class PurchaseCartReq(ReqCityCountry, UserId):
    datasets: Optional[List[str]] = []
    intelligences: Optional[List[str]] = []
    report: Optional[str] = ""
    report_potential_business_type: Optional[str] = ""
    promotion_code: Optional[str] = ""
    _promotion_object: Optional[Dict[str, Any]] = None  # internal use only

    @field_validator('datasets')
    @classmethod
    def validate_datasets(cls, v):
        for ds in v:
            if "@" in ds:
                continue  # skip validation for keyword_search datasets
            if ds not in ALL_POI_CATEGORIES:
                raise ValueError(f"Invalid dataset: {ds}")
        return v

    @field_validator('intelligences')
    @classmethod
    def validate_intelligences(cls, v):
        valid_intels = [key.replace(" Area Intelligence", "") for key in AREA_INTELLIGENCE_CATEGORIES.keys()]
        for intel in v:
            if intel not in valid_intels:
                raise ValueError(f"Invalid intelligence: {intel}")
        return v

    @field_validator('report')
    @classmethod
    def validate_report(cls, v):
        if v:
            if v not in REPORTS_PACKAGES:
                raise ValueError(f"Invalid report: {v}")
        return v

    @model_validator(mode='after')
    def validate_report_business_type(self):
        if self.report and not self.report_potential_business_type:
            raise ValueError("report_potential_business_type is required when report is provided")
        return self


class PromotionCodeDiscount(BaseModel):
    include: Optional[List[str]] = []
    discount_percentage: int = 0
    # in the future record number of usage


class PromotionCodeReq(BaseModel):
    code: str
    datasets: Optional[PromotionCodeDiscount] = Field(default_factory=PromotionCodeDiscount)
    intelligences: Optional[PromotionCodeDiscount] = Field(default_factory=PromotionCodeDiscount)
    report: Optional[PromotionCodeDiscount] = Field(default_factory=PromotionCodeDiscount)
    description: Optional[str] = ""
    target_user: Optional[str] = "all"  # "all" or "new_users_only"
    expire_at: Optional[str] = Field(
        default_factory=lambda: (datetime.now() + timedelta(days=30)).isoformat(),
        description="Expiration date in ISO format. Defaults to 1 month from today if not provided.",
        example="2026-02-24T12:00:00"
    )
    start_at: Optional[str] = Field(
        default_factory=lambda: datetime.now().isoformat(),
        description="Start date in ISO format. Defaults to today if not provided.",
        example="2026-01-24T12:00:00"
    )
    created_by: str = Field(description="Admin user ID who created the code (required)")


class PromotionCodeRes(BaseModel):
    code: str
    datasets: Optional[PromotionCodeDiscount] = Field(default_factory=PromotionCodeDiscount)
    intelligences: Optional[PromotionCodeDiscount] = Field(default_factory=PromotionCodeDiscount)
    report: Optional[PromotionCodeDiscount] = Field(default_factory=PromotionCodeDiscount)
    description: Optional[str] = ""
    expire_at: Optional[str] = None  # ISO format date string
    start_at: Optional[str] = None  # ISO format date string
    created_by: Optional[str] = None  # admin user id who created the code
