from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from src.api.auth import create_access_token, verify_password
from src.api.dependencies import get_db

router = APIRouter(tags=["auth"])


class LoginRequest(BaseModel):
    email: str = Field(min_length=3, max_length=255)
    password: str = Field(min_length=1, max_length=128)


@router.post("/login")
async def login(
    data: LoginRequest,
    db=Depends(get_db),
):
    user = await db.fetchrow(
        """
        SELECT id, email, password_hash
        FROM users
        WHERE email = $1
        """,
        data.email,
    )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    if not user["password_hash"] or not verify_password(
        data.password,
        user["password_hash"],
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль",
        )

    access_token = create_access_token(
        user_id=user["id"],
        email=user["email"],
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
