from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.dependencies import get_current_user, require_role
from Module_01_User_Roles.backend.schemas import (
    UserCreate,
    UserLogin,
    UserResponse,
    TokenResponse,
    RefreshTokenRequest,
    UserUpdate,
    FPOAddFarmerRequest,
    FPOMembershipResponse,
    BuyerVerificationRequest,
    BuyerVerificationResponse,
    AdminVerifyBuyerAction
)
from Module_01_User_Roles.backend import service

router = APIRouter(prefix="/api/users", tags=["Module 01: User & Role Management"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new platform user (Farmer, FPO, Buyer, Admin)."""
    return service.register_user(db, user_in)

@router.post("/login", response_model=TokenResponse)
def login(login_data: UserLogin, db: Session = Depends(get_db)):
    """Authenticate with email or phone and receive JWT access & refresh tokens."""
    user = service.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password."
        )
    return service.generate_tokens_for_user(user)

@router.post("/refresh", response_model=TokenResponse)
def refresh_token(req: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Exchange a valid refresh token for a new access token."""
    return service.refresh_tokens(db, req.refresh_token)

@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user = Depends(get_current_user)):
    """Get the active user's profile details."""
    return current_user

@router.put("/me", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update preferred language, district, taluka, or phone number."""
    return service.update_user_profile(db, current_user, update_data)

@router.get("/fpo/farmers", response_model=List[FPOMembershipResponse])
def get_fpo_member_farmers(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("FPO", "Admin"))
):
    """List member farmers enrolled in the authenticated FPO."""
    return service.get_fpo_farmers(db, current_user.id)

@router.post("/fpo/farmers", response_model=FPOMembershipResponse)
def enroll_farmer_to_fpo(
    req: FPOAddFarmerRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("FPO", "Admin"))
):
    """Enroll an individual farmer into this FPO cluster."""
    mem = service.add_farmer_to_fpo(db, current_user.id, req)
    return {
        "id": mem.id,
        "fpo_id": mem.fpo_id,
        "farmer_id": mem.farmer_id,
        "farmer_name": mem.farmer.full_name if mem.farmer else "Farmer",
        "farmer_email": mem.farmer.email if mem.farmer else "",
        "farmer_district": mem.farmer.district if mem.farmer else "Maharashtra",
        "land_size_acres": mem.land_size_acres,
        "primary_crop": mem.primary_crop,
        "status": mem.status,
        "joined_at": mem.joined_at
    }

@router.get("/buyers/verification", response_model=Optional[BuyerVerificationResponse])
def get_buyer_verification_status(
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Buyer", "Admin"))
):
    """Fetch current buyer's KYC and license verification state."""
    doc = current_user.buyer_verification
    return doc

@router.post("/buyers/verification", response_model=BuyerVerificationResponse)
def submit_buyer_credentials(
    req: BuyerVerificationRequest,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Buyer", "Admin"))
):
    """Submit GSTIN and APMC mandi trading license for verification."""
    return service.submit_buyer_docs(db, current_user.id, req)

@router.post("/admin/verify-buyer/{doc_id}", response_model=BuyerVerificationResponse)
def admin_verify_buyer(
    doc_id: int,
    action: AdminVerifyBuyerAction,
    db: Session = Depends(get_db),
    current_user = Depends(require_role("Admin"))
):
    """Admin action to approve or reject submitted buyer verification documents."""
    return service.verify_buyer_admin(db, doc_id, action.status, action.remarks)

@router.get("/directory", response_model=List[UserResponse])
def get_directory(
    role: Optional[str] = None,
    district: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Search registered users across Maharashtra districts and roles."""
    return service.list_all_users(db, role, district)
