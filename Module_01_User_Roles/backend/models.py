from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    phone = Column(String(20), index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    role = Column(String(20), nullable=False, default="Farmer") # Farmer, FPO, Buyer, Admin
    district = Column(String(60), default="Nashik", nullable=False)
    state = Column(String(60), default="Maharashtra", nullable=False)
    taluka = Column(String(60), nullable=True)
    preferred_lang = Column(String(10), default="en", nullable=False) # en, hi, mr
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    fpo_memberships = relationship(
        "FPOFarmerMembership",
        foreign_keys="FPOFarmerMembership.fpo_id",
        back_populates="fpo"
    )
    farmer_memberships = relationship(
        "FPOFarmerMembership",
        foreign_keys="FPOFarmerMembership.farmer_id",
        back_populates="farmer"
    )
    buyer_verification = relationship("BuyerVerificationDoc", back_populates="buyer", uselist=False)

class FPOFarmerMembership(Base):
    __tablename__ = "fpo_farmer_memberships"

    id = Column(Integer, primary_key=True, index=True)
    fpo_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    land_size_acres = Column(Float, default=2.5)
    primary_crop = Column(String(50), default="Onion")
    status = Column(String(20), default="active") # active, inactive
    joined_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    fpo = relationship("User", foreign_keys=[fpo_id], back_populates="fpo_memberships")
    farmer = relationship("User", foreign_keys=[farmer_id], back_populates="farmer_memberships")

class BuyerVerificationDoc(Base):
    __tablename__ = "buyer_verification_docs"

    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    company_name = Column(String(120), nullable=False)
    gstin = Column(String(20), nullable=False)
    mandi_license_no = Column(String(50), nullable=False)
    status = Column(String(20), default="pending") # pending, verified, rejected
    verification_remarks = Column(Text, default="Document submitted for administrative audit")
    verified_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    buyer = relationship("User", back_populates="buyer_verification")
