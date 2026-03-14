from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse, UserOut
from app.utils.jwt import generate_token
from app.utils.password import hash_password, verify_password
from app.utils.response import success
from app.utils.dependencies import get_current_user
from app.utils.sanitize import sanitize

router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/register", summary="Register a new user")
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    clean = sanitize(body.model_dump(mode="json"))

    existing = db.query(User).filter(User.email == clean["email"]).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        name=clean["name"],
        email=clean["email"],
        password=hash_password(clean["password"]),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = generate_token({"id": user.id, "role": user.role})
    return success(
        {"user": UserOut.model_validate(user).model_dump(mode="json"), "token": token},
        message="Registration successful",
        status_code=201,
    )


@router.post("/login", summary="Login and get JWT token")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = generate_token({"id": user.id, "role": user.role})
    return success(
        {"user": UserOut.model_validate(user).model_dump(mode="json"), "token": token},
        message="Login successful",
    )


@router.get("/me", summary="Get current logged-in user")
def get_me(current_user: User = Depends(get_current_user)):
    return success({"user": UserOut.model_validate(current_user).model_dump(mode="json")})
