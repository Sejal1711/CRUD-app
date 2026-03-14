import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from enum import Enum


class UserRole(str, Enum):
    USER  = "USER"
    ADMIN = "ADMIN"


class UserOut(BaseModel):
    id:        str
    name:      str
    email:     str
    role:      str
    createdAt: datetime
    updatedAt: datetime
    model_config = {"from_attributes": True}


class UpdateProfileRequest(BaseModel):
    name:     Optional[str] = None
    password: Optional[str] = None

    @staticmethod
    def validate_password(v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        return v


class UpdateRoleRequest(BaseModel):
    role: UserRole
