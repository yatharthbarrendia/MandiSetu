"""MandiSetu Master Seed Script
Pre-populates demonstration accounts for all roles (Admin, Farmer, FPO, Buyer) and Maharashtra data.
"""
from backend.core.database import SessionLocal
from backend.core.security import get_password_hash
from Module_01_User_Roles.backend.models import User, FPOFarmerMembership, BuyerVerificationDoc
from datetime import datetime, timezone

def seed_users(db):
    print("[Seed] Checking and seeding users...")
    demo_users = [
        {
            "email": "ramesh@farmer.in",
            "phone": "9822012345",
            "password": "farmer123",
            "full_name": "Ramesh Patil",
            "role": "Farmer",
            "district": "Nashik",
            "state": "Maharashtra",
            "taluka": "Niphad",
            "preferred_lang": "mr"
        },
        {
            "email": "sahyadri@fpo.in",
            "phone": "9823056789",
            "password": "fpo123",
            "full_name": "Sahyadri Kisan Producer Co Ltd",
            "role": "FPO",
            "district": "Nashik",
            "state": "Maharashtra",
            "taluka": "Dindori",
            "preferred_lang": "mr"
        },
        {
            "email": "sourcing@bigbasket.com",
            "phone": "9890011223",
            "password": "buyer123",
            "full_name": "BigBasket Sourcing Hub (West)",
            "role": "Buyer",
            "district": "Pune",
            "state": "Maharashtra",
            "taluka": "Haveli",
            "preferred_lang": "en"
        },
        {
            "email": "reliance@retail.in",
            "phone": "9890033445",
            "password": "buyer123",
            "full_name": "Reliance Fresh Agro Sourcing",
            "role": "Buyer",
            "district": "Nashik",
            "state": "Maharashtra",
            "taluka": "Nashik City",
            "preferred_lang": "en"
        },
        {
            "email": "admin@mandisetu.gov.in",
            "phone": "9800000001",
            "password": "admin123",
            "full_name": "Director of Agricultural Marketing (MH)",
            "role": "Admin",
            "district": "Pune",
            "state": "Maharashtra",
            "taluka": "Central",
            "preferred_lang": "mr"
        },
        {
            "email": "suresh@farmer.in",
            "phone": "9822098765",
            "password": "farmer123",
            "full_name": "Suresh Shinde",
            "role": "Farmer",
            "district": "Pune",
            "state": "Maharashtra",
            "taluka": "Baramati",
            "preferred_lang": "mr"
        }
    ]

    created_users = {}
    for u_data in demo_users:
        existing = db.query(User).filter(User.email == u_data["email"]).first()
        if not existing:
            user = User(
                email=u_data["email"],
                phone=u_data["phone"],
                hashed_password=get_password_hash(u_data["password"]),
                full_name=u_data["full_name"],
                role=u_data["role"],
                district=u_data["district"],
                state=u_data["state"],
                taluka=u_data["taluka"],
                preferred_lang=u_data["preferred_lang"],
                is_active=True
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            created_users[u_data["email"]] = user
            print(f"  ✓ Created {u_data['role']}: {u_data['email']}")
        else:
            created_users[u_data["email"]] = existing

    # Seed FPO Membership
    fpo = created_users.get("sahyadri@fpo.in")
    farmer1 = created_users.get("ramesh@farmer.in")
    farmer2 = created_users.get("suresh@farmer.in")

    if fpo and farmer1:
        mem1 = db.query(FPOFarmerMembership).filter(
            FPOFarmerMembership.fpo_id == fpo.id,
            FPOFarmerMembership.farmer_id == farmer1.id
        ).first()
        if not mem1:
            db.add(FPOFarmerMembership(
                fpo_id=fpo.id,
                farmer_id=farmer1.id,
                land_size_acres=4.5,
                primary_crop="Onion",
                status="active"
            ))

    if fpo and farmer2:
        mem2 = db.query(FPOFarmerMembership).filter(
            FPOFarmerMembership.fpo_id == fpo.id,
            FPOFarmerMembership.farmer_id == farmer2.id
        ).first()
        if not mem2:
            db.add(FPOFarmerMembership(
                fpo_id=fpo.id,
                farmer_id=farmer2.id,
                land_size_acres=3.0,
                primary_crop="Tomato",
                status="active"
            ))
    db.commit()

    # Seed Buyer Verification
    buyer1 = created_users.get("sourcing@bigbasket.com")
    if buyer1:
        doc = db.query(BuyerVerificationDoc).filter(BuyerVerificationDoc.buyer_id == buyer1.id).first()
        if not doc:
            db.add(BuyerVerificationDoc(
                buyer_id=buyer1.id,
                company_name="Supermarket Grocery Supplies Pvt Ltd (BigBasket)",
                gstin="27AABCS1429B1ZB",
                mandi_license_no="MH-APMC-PUN-DIR-2023-412",
                status="verified",
                verification_remarks="Verified via Maharashtra State APMC Central Registry",
                verified_at=datetime.now(timezone.utc)
            ))
            db.commit()

    buyer2 = created_users.get("reliance@retail.in")
    if buyer2:
        doc2 = db.query(BuyerVerificationDoc).filter(BuyerVerificationDoc.buyer_id == buyer2.id).first()
        if not doc2:
            db.add(BuyerVerificationDoc(
                buyer_id=buyer2.id,
                company_name="Reliance Retail Ventures Ltd (Agro Division)",
                gstin="27AAACR4054J1Z8",
                mandi_license_no="MH-APMC-NSK-2022-908",
                status="verified",
                verification_remarks="Direct marketing license verified by Agri Dept",
                verified_at=datetime.now(timezone.utc)
            ))
            db.commit()

def seed_all():
    db = SessionLocal()
    try:
        seed_users(db)
        print("[Seed] Seed process completed successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    seed_all()
