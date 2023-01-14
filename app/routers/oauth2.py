from jose import JWTError, jwt
from datetime import datetime, timedelta
from .. import schemas, database, models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from ..config import settings
oauth2_sheme = OAuth2PasswordBearer("login")

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        id: str = payload.get("user_id")

        if not id:
            raise credentials_exception
        token_data = schemas.TokenData(id=id)
    except JWTError:
        raise credentials_exception
    return token_data


def get_current_user(token: str = Depends(oauth2_sheme), db: Session = Depends(database.get_db)):
    credentials_exceptions = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                           detail="could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    token = verify_access_token(token, credentials_exceptions)
    user = db.query(models.User).filter(models.User.id == token.id).first()

    return user
