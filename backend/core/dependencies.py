from typing import Optional, List, Callable
from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.core.security import decode_token

def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """Extract and validate the current user from Bearer token, returning None if absent or invalid."""
    if not authorization:
        return None
    
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    
    token = parts[1]
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        return None
    
    user_id = payload.get("sub")
    if not user_id:
        return None
    
    # Lazy import to avoid circular dependency
    from Module_01_User_Roles.backend.models import User
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user or not user.is_active:
        return None
    return user

def get_current_user(
    current_user = Depends(get_current_user_optional)
):
    """Enforce authentication, raising 401 Unauthorized if missing/invalid."""
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return current_user

def require_role(*allowed_roles: str) -> Callable:
    """Dependency factory ensuring current user possesses one of the allowed roles."""
    def role_checker(current_user = Depends(get_current_user)):
        if current_user.role.lower() not in [r.lower() for r in allowed_roles]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access forbidden: requires one of {allowed_roles}"
            )
        return current_user
    return role_checker
