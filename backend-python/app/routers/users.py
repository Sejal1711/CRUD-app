from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.models.models import User
from app.schemas.user import UserOut, UpdateProfileRequest, UpdateRoleRequest
from app.utils.dependencies import get_current_user, require_admin
from app.utils.password import hash_password
from app.utils.response import success

router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.get("", summary="Get all users (Admin only)")
def get_all_users(
    page:  int           = Query(1, ge=1),
    limit: int           = Query(10, ge=1, le=100),
    role:  Optional[str] = None,
    db:    Session       = Depends(get_db),
    _:     User          = Depends(require_admin),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)

    total = query.count()
    users = (
        query.order_by(User.createdAt.desc())
        .offset((page - 1) * limit)
        .limit(limit)
        .all()
    )

    return success({
        "users": [UserOut.model_validate(u).model_dump(mode="json") for u in users],
        "pagination": {
            "page": page, "limit": limit, "total": total,
            "pages": -(-total // limit),
        },
    })


@router.get("/{user_id}", summary="Get user by ID (Admin or own profile)")
def get_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role != "ADMIN" and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return success({"user": UserOut.model_validate(user).model_dump(mode="json")})


@router.patch("/{user_id}", summary="Update own profile (name or password)")
def update_profile(
    user_id: str,
    body: UpdateProfileRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id and current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not body.name and not body.password:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    if body.name:
        user.name = body.name
    if body.password:
        UpdateProfileRequest.validate_password(body.password)
        user.password = hash_password(body.password)

    db.commit()
    db.refresh(user)
    return success({"user": UserOut.model_validate(user).model_dump(mode="json")}, message="Profile updated")


@router.patch("/{user_id}/role", summary="Update user role (Admin only)")
def update_role(
    user_id: str,
    body: UpdateRoleRequest,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = body.role
    db.commit()
    db.refresh(user)
    return success({"user": UserOut.model_validate(user).model_dump(mode="json")}, message="Role updated")


@router.delete("/{user_id}", summary="Delete a user (Admin only)")
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    if current_user.id == user_id:
        raise HTTPException(status_code=400, detail="Cannot delete your own account")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return success(message="User deleted")
