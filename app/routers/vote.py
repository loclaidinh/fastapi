from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from . import oauth2

router = APIRouter(prefix="/vote",
                   tags=["Vote"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def vote(vote: schemas.Vote, db: Session = Depends(get_db), current_user=Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == vote.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="post not found!")
    else:
        vote_query = db.query(models.Vote).filter(
            models.Vote.post_id == vote.post_id, models.Vote.user_id == current_user.id)
        found_vote = vote_query.first()
        if found_vote:
            if vote.dir == 1:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail=f"already voted!")
            else:
                # new_vote = models.Vote(
                #     post_id=vote.post_id, user_id=current_user.id)
                vote_query.delete(synchronize_session=False)
                db.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)

        else:
            if vote.dir == 1:
                new_vote = models.Vote(
                    post_id=vote.post_id, user_id=current_user.id)
                db.add(new_vote)
                db.commit()
                return {"message": "voted successfully"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="no vote found to unvote!")
