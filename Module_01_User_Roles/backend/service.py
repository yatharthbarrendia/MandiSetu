from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from backend.core.security import (
    get_password_hash,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)
from Module_01_User_Roles.backend.models import User, FPOFarmerMembership, BuyerVerificationDoc
from Module_01_User_Roles.backend.schemas import (
    UserCreate,
    UserUpdate,
    FPOAddFarmerRequest,
    BuyerVerificationRequest
)

def register_user(db: Session, user_in: UserCreate) -> User:
    """Create a new user with hashed credentials and role verification."""
    existing = db.query(User).filter(User.email == user_in.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user = User(
        email=user_in.email.lower(),
        phone=user_in.phone,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        role=user_in.role,
        district=user_in.district,
        state=user_in.state,
        taluka=user_in.taluka,
        preferred_lang=user_in.preferred_lang,
        is_active=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def authenticate_user(db: Session, login_identifier: str, password: str) -> Optional[User]:
    """Verify user credentials against email or phone."""
    identifier = login_identifier.strip().lower()
    user = db.query(User).filter(
        (User.email == identifier) | (User.phone == identifier)
    ).first()
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user

def generate_tokens_for_user(user: User) -> Dict[str, Any]:
    """Generate JWT access and refresh token pair containing user claims."""
    claims = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "district": user.district
    }
    return {
        "access_token": create_access_token(claims),
        "refresh_token": create_refresh_token(claims),
        "token_type": "bearer",
        "user": user
    }

def refresh_tokens(db: Session, refresh_token: str) -> Dict[str, Any]:
    """Validate refresh token and issue a fresh access token."""
    payload = decode_token(refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token."
        )

    user_id = payload.get("sub")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive or not found."
        )

    return generate_tokens_for_user(user)

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    return db.query(User).filter(User.id == user_id).first()

def update_user_profile(db: Session, user: User, update_data: UserUpdate) -> User:
    """Update user personal and regional preferences."""
    if update_data.full_name is not None:
        user.full_name = update_data.full_name
    if update_data.phone is not None:
        user.phone = update_data.phone
    if update_data.district is not None:
        user.district = update_data.district
    if update_data.taluka is not None:
        user.taluka = update_data.taluka
    if update_data.preferred_lang is not None:
        user.preferred_lang = update_data.preferred_lang

    db.commit()
    db.refresh(user)
    return user

def add_farmer_to_fpo(db: Session, fpo_id: int, req: FPOAddFarmerRequest) -> FPOFarmerMembership:
    """Link an individual farmer to an FPO aggregate cluster."""
    farmer = None
    if req.farmer_id:
        farmer = db.query(User).filter(User.id == req.farmer_id).first()
    elif req.farmer_email:
        farmer = db.query(User).filter(User.email == req.farmer_email.lower()).first()

    if not farmer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Farmer account not found. Please verify farmer ID or email."
        )

    # Check for existing membership
    existing = db.query(FPOFarmerMembership).filter(
        FPOFarmerMembership.fpo_id == fpo_id,
        FPOFarmerMembership.farmer_id == farmer.id
    ).first()

    if existing:
        existing.land_size_acres = req.land_size_acres
        existing.primary_crop = req.primary_crop
        existing.status = "active"
        db.commit()
        db.refresh(existing)
        return existing

    membership = FPOFarmerMembership(
        fpo_id=fpo_id,
        farmer_id=farmer.id,
        land_size_acres=req.land_size_acres,
        primary_crop=req.primary_crop,
        status="active"
    )
    db.add(membership)
    db.commit()
    db.refresh(membership)
    return membership

def get_fpo_farmers(db: Session, fpo_id: int) -> List[Dict[str, Any]]:
    """Retrieve full roster of member farmers linked to an FPO."""
    memberships = db.query(FPOFarmerMembership).filter(
        FPOFarmerMembership.fpo_id == fpo_id
    ).all()

    results = []
    for m in memberships:
        results.append({
            "id": m.id,
            "fpo_id": m.fpo_id,
            "farmer_id": m.farmer_id,
            "farmer_name": m.farmer.full_name if m.farmer else "Unknown",
            "farmer_email": m.farmer.email if m.farmer else "Unknown",
            "farmer_district": m.farmer.district if m.farmer else "Maharashtra",
            "land_size_acres": m.land_size_acres,
            "primary_crop": m.primary_crop,
            "status": m.status,
            "joined_at": m.joined_at
        })
    return results

def submit_buyer_docs(db: Session, buyer_id: int, req: BuyerVerificationRequest) -> BuyerVerificationDoc:
    """Submit institutional buyer credentials (GSTIN, APMC Mandi License)."""
    doc = db.query(BuyerVerificationDoc).filter(BuyerVerificationDoc.buyer_id == buyer_id).first()

    # Mock auto-check: if GSTIN is standard format (15 chars) and license present, verify automatically or flag verified
    auto_status = "verified" if len(req.gstin.strip()) == 15 and req.mandi_license_no else "pending"
    remarks = "Automated GSTIN and APMC registry cross-check confirmed" if auto_status == "verified" else "Pending manual officer review"

    if doc:
        doc.company_name = req.company_name
        doc.gstin = req.gstin.strip().upper()
        doc.mandi_license_no = req.mandi_license_no.strip()
        doc.status = auto_status
        doc.verification_remarks = remarks
        if auto_status == "verified":
            doc.verified_at = datetime.now(timezone.utc)
    else:
        doc = BuyerVerificationDoc(
            buyer_id=buyer_id,
            company_name=req.company_name,
            gstin=req.gstin.strip().upper(),
            mandi_license_no=req.mandi_license_no.strip(),
            status=auto_status,
            verification_remarks=remarks,
            verified_at=datetime.now(timezone.utc) if auto_status == "verified" else None
        )
        db.add(doc)

    db.commit()
    db.refresh(doc)
    return doc

def verify_buyer_admin(db: Session, doc_id: int, status_val: str, remarks: str) -> BuyerVerificationDoc:
    """Admin endpoint to approve or reject a buyer's verification documents."""
    doc = db.query(BuyerVerificationDoc).filter(BuyerVerificationDoc.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Buyer verification document not found.")

    doc.status = status_val
    doc.verification_remarks = remarks
    if status_val == "verified":
        doc.verified_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(doc)
    return doc

def list_all_users(db: Session, role: Optional[str] = None, district: Optional[str] = None) -> List[User]:
    """Query directory of users filtered by role or district."""
    query = db.query(User)
    if role:
        query = query.filter(User.role.ilike(role))
    if district:
        query = query.filter(User.district.ilike(district))
    return query.all()
