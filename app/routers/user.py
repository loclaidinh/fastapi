from fastapi import status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from . import oauth2

router = APIRouter(
    prefix="/users",
    tags=["User"]
)


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.UserOut)
def create_user(user: schemas.CreateUser, db: Session = Depends(get_db)):
    user_query = db.query(models.User).filter(
        models.User.email == user.email).first()
    if user_query:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"email {user.email} already registered!")

    hashed_password = utils.hash_password(user.password)
    user.password = hashed_password

    new_user = models.User(**user.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.get("/{id}", response_model=schemas.UserOut)
def get_user(id: int, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):

    user = db.query(models.User).filter(models.User.id == id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"user id {id} not found!")

    return user
