from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, ConfigDict

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone: Optional[str] = None
    role: str = "Farmer" # Farmer, FPO, Buyer, Admin
    district: str = "Nashik"
    state: str = "Maharashtra"
    taluka: Optional[str] = None
    preferred_lang: str = "en"

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    phone: Optional[str] = None
    role: str
    district: str
    state: str
    taluka: Optional[str] = None
    preferred_lang: str
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    district: Optional[str] = None
    taluka: Optional[str] = None
    preferred_lang: Optional[str] = None

class FPOAddFarmerRequest(BaseModel):
    farmer_id: Optional[int] = None
    farmer_email: Optional[str] = None
    land_size_acres: float = 2.0
    primary_crop: str = "Onion"

class FPOMembershipResponse(BaseModel):
    id: int
    fpo_id: int
    farmer_id: int
    farmer_name: Optional[str] = None
    farmer_email: Optional[str] = None
    farmer_district: Optional[str] = None
    land_size_acres: float
    primary_crop: str
    status: str
    joined_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class BuyerVerificationRequest(BaseModel):
    company_name: str
    gstin: str
    mandi_license_no: str

class BuyerVerificationResponse(BaseModel):
    id: int
    buyer_id: int
    company_name: str
    gstin: str
    mandi_license_no: str
    status: str
    verification_remarks: Optional[str] = None
    verified_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class AdminVerifyBuyerAction(BaseModel):
    status: str # "verified" or "rejected"
    remarks: Optional[str] = "Verified through APMC trader registry"
