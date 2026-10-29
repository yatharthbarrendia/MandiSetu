"""MandiSetu Platform Launcher
Starts the unified FastAPI backend server which simultaneously serves the frontend shell and all modules.
"""
import uvicorn
from backend.core.config import settings
from backend.init_db import init_db
from backend.seed import seed_all

def main():
    print("=" * 60)
    print(" 🌾 MandiSetu 2.0 - Govt. of Maharashtra (SIH26132)")
    print(" Strengthening Market Linkages & Price Discovery for Farmers")
    print("=" * 60)
    print(f"Server starting on http://{settings.HOST}:{settings.PORT}")
    print(f"API Docs available at http://{settings.HOST}:{settings.PORT}/api/docs")
    print(f"Unified Portal: http://{settings.HOST}:{settings.PORT}/")
    print("=" * 60)

    # Initialize DB & Seed Demo Data
    init_db()
    seed_all()

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False
    )

if __name__ == "__main__":
    main()
