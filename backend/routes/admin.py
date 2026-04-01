from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..limiter import limiter
from ..database import get_db
from ..models import Admin
from ..schemas import AdminLogin, TokenResponse, AdminResponse, AdminCredentialsUpdate
from ..auth import verify_password, hash_password, create_access_token, get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/5minute")
def login(request: Request, data: AdminLogin, db: Session = Depends(get_db)):
    admin = db.query(Admin).filter(Admin.username == data.username).first()
    if not admin or not verify_password(data.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    token = create_access_token(data={"sub": admin.username})
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=AdminResponse)
def get_me(admin: Admin = Depends(get_current_admin)):
    return admin

@router.put("/credentials")
def update_credentials(
    data: AdminCredentialsUpdate,
    db: Session = Depends(get_db),
    admin: Admin = Depends(get_current_admin)
):
    if not verify_password(data.current_password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Incorrect current password")
    
    if data.new_username and data.new_username != admin.username:
        existing = db.query(Admin).filter(Admin.username == data.new_username, Admin.id != admin.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")
        admin.username = data.new_username
        
    if data.new_password:
        admin.password_hash = hash_password(data.new_password)
        
    db.commit()
    return {"message": "Credentials updated successfully"}
