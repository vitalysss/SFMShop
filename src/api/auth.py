from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from src.config import SECRET_KEY

security = HTTPBearer()
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
)


ALGORITHM = "HS256"


class TokenData(BaseModel):
    user_id: int
    email: str


def create_access_token(user_id: int, email: str, expires_minutes: int = 15) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=expires_minutes,
    )

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expires,
    }

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenData:
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
        )

    user_id = payload.get("sub")
    email = payload.get("email")

    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Некорректные данные токена",
        )

    return TokenData(
        user_id=int(user_id),
        email=email,
    )


def verify_password(plain_pass: str, hashed_pass: str) -> bool:
    return pwd_context.verify(plain_pass, hashed_pass)
