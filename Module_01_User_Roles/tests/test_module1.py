import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.core.database import Base
from backend.core.security import get_password_hash, verify_password, decode_token
from Module_01_User_Roles.backend.models import User, FPOFarmerMembership, BuyerVerificationDoc
from Module_01_User_Roles.backend.schemas import UserCreate, UserUpdate, FPOAddFarmerRequest, BuyerVerificationRequest
from Module_01_User_Roles.backend import service

TEST_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture
def db():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_password_hashing():
    pwd = "secretFarmer123"
    hashed = get_password_hash(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("wrongPassword", hashed) is False

def test_user_registration(db):
    user_in = UserCreate(
        email="testfarmer@example.com",
        password="testPassword123",
        full_name="Balaram Patil",
        role="Farmer",
        district="Nashik",
        preferred_lang="mr"
    )
    user = service.register_user(db, user_in)
    assert user.id is not None
    assert user.email == "testfarmer@example.com"
    assert user.role == "Farmer"
    assert user.district == "Nashik"
    assert verify_password("testPassword123", user.hashed_password) is True

def test_duplicate_registration_fails(db):
    user_in = UserCreate(
        email="duplicate@example.com",
        password="testPassword123",
        full_name="User One",
        role="Farmer",
        district="Pune"
    )
    service.register_user(db, user_in)

    with pytest.raises(Exception):
        service.register_user(db, user_in)

def test_authentication_and_tokens(db):
    user_in = UserCreate(
        email="authuser@example.com",
        password="mypassword",
        full_name="Auth User",
        role="Buyer",
        district="Pune"
    )
    user = service.register_user(db, user_in)

    # Valid auth
    authed = service.authenticate_user(db, "authuser@example.com", "mypassword")
    assert authed is not None
    assert authed.id == user.id

    # Invalid password auth
    wrong = service.authenticate_user(db, "authuser@example.com", "wrongpwd")
    assert wrong is None

    # Token issuance
    tokens = service.generate_tokens_for_user(authed)
    assert "access_token" in tokens
    assert "refresh_token" in tokens

    payload = decode_token(tokens["access_token"])
    assert payload.get("sub") == str(user.id)
    assert payload.get("role") == "Buyer"
    assert payload.get("type") == "access"

def test_update_profile(db):
    user_in = UserCreate(
        email="profile@example.com",
        password="password123",
        full_name="Initial Name",
        role="Farmer",
        district="Nashik"
    )
    user = service.register_user(db, user_in)

    update_req = UserUpdate(
        full_name="Updated Name Patil",
        district="Kolhapur",
        preferred_lang="mr"
    )
    updated = service.update_user_profile(db, user, update_req)
    assert updated.full_name == "Updated Name Patil"
    assert updated.district == "Kolhapur"
    assert updated.preferred_lang == "mr"

def test_fpo_farmer_membership(db):
    fpo_in = UserCreate(
        email="fpo@producer.org",
        password="fpopassword",
        full_name="Kisan FPO Ltd",
        role="FPO",
        district="Nashik"
    )
    fpo = service.register_user(db, fpo_in)

    farmer_in = UserCreate(
        email="memberfarmer@example.com",
        password="farmerpassword",
        full_name="Member Farmer",
        role="Farmer",
        district="Nashik"
    )
    farmer = service.register_user(db, farmer_in)

    # Link farmer to FPO
    req = FPOAddFarmerRequest(
        farmer_id=farmer.id,
        land_size_acres=5.0,
        primary_crop="Onion"
    )
    mem = service.add_farmer_to_fpo(db, fpo.id, req)
    assert mem.id is not None
    assert mem.fpo_id == fpo.id
    assert mem.farmer_id == farmer.id
    assert mem.land_size_acres == 5.0

    members = service.get_fpo_farmers(db, fpo.id)
    assert len(members) == 1
    assert members[0]["farmer_name"] == "Member Farmer"

def test_buyer_verification(db):
    buyer_in = UserCreate(
        email="buyerkyc@procure.com",
        password="buyerpassword",
        full_name="Agro Procure Corp",
        role="Buyer",
        district="Pune"
    )
    buyer = service.register_user(db, buyer_in)

    req = BuyerVerificationRequest(
        company_name="Agro Procure Corp Ltd",
        gstin="27ABCDE1234F1Z5", # 15 chars
        mandi_license_no="MH-APMC-PUN-001"
    )
    doc = service.submit_buyer_docs(db, buyer.id, req)
    assert doc.id is not None
    assert doc.status == "verified"
    assert doc.buyer_id == buyer.id
