from jose import JWTError, jwt
from app import schemas
from app.config import settings


def verify_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key,
                             algorithms=settings.algorithm)
        id: str = payload.get("user_id")

        if not id:
            raise Exception("User not found!")
    except JWTError:
        raise Exception("Invalid jwt token")
    return id
