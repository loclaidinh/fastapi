from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from . import oauth2

router = APIRouter(tags=["Authentication"])


@router.post("/login", response_model=schemas.Token)
def user_login(user_cretidentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.email == user_cretidentials.username).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid cretidentials!")

    hashed_password = user.password

    if not utils.verify_password(user_cretidentials.password, hashed_password):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Invalid cretidentials!")

    encode_jwt = oauth2.create_access_token({"user_id": user.id})

    return {"access_token": encode_jwt,
            "token_type": "bearer"}
