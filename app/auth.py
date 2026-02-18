from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
import hashlib
import jwt
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import bcrypt

from app.models.users import User as UserModel
from app.config import SECRET_KEY, ALGORITHM
from app.db_depends import get_async_db


ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def _prehash_password(password: str) -> bytes:
    """
    Bcrypt in `bcrypt>=5` rejects passwords longer than 72 bytes.
    Pre-hash the UTF-8 password to a fixed length to avoid that limit.
    """
    return hashlib.sha256(password.encode("utf-8")).digest()


def hash_password(password: str) -> str:
    """
    Преобразует пароль в хеш с использованием bcrypt.
    """
    hashed = bcrypt.hashpw(_prehash_password(password), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли введённый пароль сохранённому хешу.
    """
    hashed_bytes = hashed_password.encode("utf-8")

    try:
        # Preferred path (new hashes): bcrypt(sha256(password))
        if bcrypt.checkpw(_prehash_password(plain_password), hashed_bytes):
            return True

        # Backward-compat (legacy hashes): bcrypt(password)
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_bytes)
    except ValueError:
        return False


async def get_current_user(token: str = Depends(oauth2_scheme),
                           db: AsyncSession = Depends(get_async_db)):
    """
    Проверяет JWT и возвращает пользователя из базы.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise credentials_exception
    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active == True))
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_seller(current_user: UserModel = Depends(get_current_user)):
    """
    Проверяет, что пользователь имеет роль 'seller'.
    """
    if current_user.role != "seller":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only sellers can perform this action")
    return current_user

         
def create_access_token(data: dict):
    """
    Создаёт access-токен.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({
        "exp": expire,
        "token_type": "access",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict):
    """
    Создаёт refresh-токен с длительным сроком действия и token_type="refresh".
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


