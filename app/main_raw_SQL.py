from typing import Optional
from fastapi import FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from .config import settings

app = FastAPI()

while True:
    try:
        conn = psycopg2.connect(host=settings.database_hostname, database=settings.database_name, user=settings.database_username,
                                password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Connection to database was successfully!")
        break
    except Exception as error:
        print("Connect to database failed!")
        print("Error: ", error)
        time.sleep(3)


class Post(BaseModel):
    title: str
    content: str
    published: bool = True


my_posts = [
    {"title": "favorite foods", "content": "I love pizza", "id": 1},
    {"title": "favorite car", "content": "I love bmw", "id": 2}
]


def find_post(id):
    for p in my_posts:
        if p["id"] == id:
            return p


def get_post_index(id):
    for i, p in enumerate(my_posts):
        if p["id"] == id:
            return i


@app.get("/")
def root():
    return {"message": "Welcome to my API!"}


@app.get("/posts")
def get_posts():
    # make SQL var to store to string query
    cursor.execute(""" SELECT * FROM posts """)
    posts = cursor.fetchall()
    return {"data": posts}


@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_post(post: Post):
    cursor.execute(
        """ INSERT INTO posts (title, content, published) 
                        VALUES (%s, %s, %s) RETURNING *""",
        (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"message": new_post}


@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute(
        """ SELECT * FROM posts WHERE id = %s """, str(id))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id {id} not found!")
    return {"message": post}


@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute(
        """ DELETE FROM posts WHERE id = %s RETURNING * """, str(id))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post id {id} not exist!")

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute(
        """ UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """,
        (post.title, post.content, post.published, str(id)))
    post = cursor.fetchone()
    conn.commit()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post id {id} not exist!")

    return {"message": post}
