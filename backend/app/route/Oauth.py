from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from ..oauth import google
from ..models import User
from ..database import SessionLocal

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter()

@router.get("/auth/google")
async def google_login(request: Request):
    redirect_uri = request.url_for("google_callback")  
    return await google.authorize_redirect(request, redirect_uri)


@router.get("/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    token = await google.authorize_access_token(request)
    user_info = token.get("userinfo")

    if not user_info:
        raise HTTPException(status_code=400, detail="Invalid Google login")

    google_email = user_info["email"]
    google_name = user_info.get("name", "")

    # Check if user exists
    user = db.query(User).filter(User.email == google_email).first()

    if not user:
        # Auto register user if first time
        new_user = User(
            username=google_name,
            email=google_email,
            hashed_password=None,  # OAuth users don’t need password
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        user = new_user

    # Here you can generate JWT token or session
    return {"message": f"Google login successful", "user_id": user.id, "email": google_email}
