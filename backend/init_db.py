"""Database Initialization Script for MandiSetu.
Imports all module models and ensures tables are synchronized.
"""
from backend.core.database import Base, engine
from backend.utils.notifications import Notification

def init_db():
    print("[DB Init] Registering models for table creation...")
    _ = Notification

    # Module 01: User & Roles
    try:
        import Module_01_User_Roles.backend.models
        print("  ✓ Module 01 models loaded")
    except ImportError as e:
        print(f"  - Module 01 skipped ({e})")

    # Module 02: Price Discovery
    try:
        import Module_02_Price_Discovery.backend.models
        print("  ✓ Module 02 models loaded")
    except ImportError:
        pass

    # Module 03: Net Realization
    try:
        import Module_03_Net_Realization.backend.models
        print("  ✓ Module 03 models loaded")
    except ImportError:
        pass

    # Module 04: Produce Listing
    try:
        import Module_04_Produce_Listing.backend.models
        print("  ✓ Module 04 models loaded")
    except ImportError:
        pass

    # Module 05: Matching Offers
    try:
        import Module_05_Matching_Offers.backend.models
        print("  ✓ Module 05 models loaded")
    except ImportError:
        pass

    # Module 06: Transactions
    try:
        import Module_06_Transactions.backend.models
        print("  ✓ Module 06 models loaded")
    except ImportError:
        pass

    # Module 07: Sale Window
    try:
        import Module_07_Sale_Window.backend.models
        print("  ✓ Module 07 models loaded")
    except ImportError:
        pass

    # Module 08: Buyer Trust
    try:
        import Module_08_Buyer_Trust.backend.models
        print("  ✓ Module 08 models loaded")
    except ImportError:
        pass

    # Module 09: Logistics
    try:
        import Module_09_Logistics.backend.models
        print("  ✓ Module 09 models loaded")
    except ImportError:
        pass

    # Module 10: Disputes
    try:
        import Module_10_Disputes.backend.models
        print("  ✓ Module 10 models loaded")
    except ImportError:
        pass

    # Module 11: Quality Grading
    try:
        import Module_11_Quality_Grading.backend.models
        print("  ✓ Module 11 models loaded")
    except ImportError:
        pass

    # Module 12: Weather Risk
    try:
        import Module_12_Weather_Risk.backend.models
        print("  ✓ Module 12 models loaded")
    except ImportError:
        pass

    # Module 13: Admin Analytics
    try:
        import Module_13_Admin_Analytics.backend.models
        print("  ✓ Module 13 models loaded")
    except ImportError:
        pass

    Base.metadata.create_all(bind=engine)
    print("[DB Init] All database tables created or confirmed.")

if __name__ == "__main__":
    init_db()
