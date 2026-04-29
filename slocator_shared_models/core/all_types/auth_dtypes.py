from typing import Dict, List, TypeVar, Generic, Optional, Any
from pydantic import BaseModel
from .internal_types import UserId

class EmailBase(BaseModel):
    email: str

class UsernameBase(BaseModel):
    username: str

class ReqAuth(EmailBase):
    password: str


class IntelligencePurchase(BaseModel):
    purchase_date: str
    price_paid_usd: float
    expiration_days: int


class MakerData(BaseModel):
    dataset: Dict[str, Any] = {}
    layers: Dict[str, Any] = {}
    catalogs: Dict[str, Any] = {}
    draft_catalogs: Dict[str, Any] = {}
    purchased_reports: Dict[str, Any] = {}
    intelligence_purchases: Dict[str, IntelligencePurchase] = {}


class UserProfilemakerData(UserId):
    maker: MakerData = MakerData()


class MarketingCampaigns(BaseModel):
    source: Optional[str] = ""
    has_purchases: bool = False

class UserSettings(BaseModel):
    account_type: str = "admin"  # default to admin
    admin_id: Optional[str] = None  # Only required for member accounts
    show_price_on_purchase: bool = False
    phone: Optional[str] = ""
    has_payment_method: bool = False

class UserProfileMeta(UserId, UsernameBase, EmailBase, MarketingCampaigns, UserSettings):
    pass

class ReqUpdateUserProfileSettings(UserId, UserSettings):
    pass


class ResUserProfile(UserProfileMeta):
    maker: MakerData



# Derived classes
class ReqCreateFirebaseUser(ReqAuth, UsernameBase):
    pass


class ReqCreateUserProfile(ReqAuth, UserProfileMeta):
    pass

class ReqUserLogin(ReqAuth):
    source: Optional[str] = None


class ReqUserProfile(UserId):
    pass


class ReqResetPassword(BaseModel):
    email: str


class ReqConfirmReset(BaseModel):
    oob_code: str
    new_password: str


class ReqChangePassword(UserId, ReqAuth):
    new_password: str


class ReqChangeEmail(UserId):
    current_email: str
    new_email: str
    password: str


class ReqRefreshToken(BaseModel):
    grant_type: str
    refresh_token: str

class ReqSendOTP(BaseModel):
    phone_number: str
    channel: str = "sms"  # default to SMS

class ReqVerifyOTP(BaseModel):
    phone_number: str
    code: str


class ReqGoogleLogin(BaseModel):
    """Request model for Google OAuth login."""
    credential: str  # Google OAuth JWT credential token
    source: Optional[str] = None  # Marketing attribution source/campaign identifier
