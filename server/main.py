from fastapi import FastAPI, HTTPException, Depends, Header, Query
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import List
import uvicorn
import sqlite3
import bcrypt
import json
import sys
import os

# vars for tokens
TOKEN_KEY = os.environ.get("CELAR_KEY")
TOKEN_ALGORITHM = "HS256"
DEMO_MODE = "demo" in sys.argv
VERSION = "0.1.8"

if not TOKEN_KEY:
    print("Please set CELAR_KEY.")
    sys.exit(1)

app = FastAPI()
DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE, check_same_thread=False)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL,
            software TEXT
       ) 
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT NOT NULL,
            content BLOB NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(author) REFERENCES users(username)
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS post_likes (
            post_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            PRIMARY KEY (post_id, username),
            FOREIGN KEY (post_id) REFERENCES posts(id),
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)
    conn.commit()
    conn.close()
    
init_db()

def get_db():
    conn = sqlite3.connect(DB_FILE)
    try:
        yield conn
    finally:
        conn.close()

def generate_token(data: dict, expires: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, TOKEN_KEY, algorithm=TOKEN_ALGORITHM)

def get_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    token = authorization.split( )[1]
    try:
        payload = jwt.decode(token, TOKEN_KEY, algorithms=[TOKEN_ALGORITHM])
        username = payload.get("sub")
        exp = payload.get("exp")
        if exp:
            exp = datetime.fromtimestamp(payload["exp"], timezone.utc)
            if exp < datetime.now(timezone.utc):
                raise HTTPException(status_code=401, detail="Token expired")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return username
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
def get_user_coins(username: str, db_cursor: sqlite3.Cursor):
    db_cursor.execute("""
        SELECT COUNT(*)
        FROM post_likes
        JOIN posts ON post_likes.post_id = posts.id
        WHERE posts.author = ?
    """, (username,))
    coins = db_cursor.fetchone()[0]
    return coins

# models
class UserCreate(BaseModel):
    username: str
    password: str
    software: List[str]

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    software: List[str]
    
class PostCreate(BaseModel):
    content: bytes
    
class PostOut(BaseModel):
    id: int
    author: str
    content: bytes
    created_at: str

# endpoints
@app.get("/details")
def get_details():
    return {
        "demo_mode": DEMO_MODE,
        "version": VERSION
    }

@app.post("/register")
def register(user: UserCreate, db: sqlite3.Connection = Depends(get_db)):
    if DEMO_MODE:
        raise HTTPException(status_code=401, detail="Can't create user account in demo mode.")
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')
    
    c = db.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (user.username,))
    if c.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")
    c.execute("INSERT INTO users (username, password, software) VALUES (?, ?, ?)",
              (user.username, hashed_pw, json.dumps(user.software)))
    db.commit()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin, db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (user.username,))
    row = c.fetchone()
    if not row or not bcrypt.checkpw(user.password.encode('utf-8'), row[0].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = generate_token(
        data={"sub": user.username},
        expires=timedelta(hours=48)
    )
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
def read_me(current_user: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT username, software FROM users WHERE username=?", (current_user,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    coins = get_user_coins(current_user, c)
    return {"username": row[0], "software": json.loads(row[1]), "coins": coins}

@app.get("/profile/{username}")
def read_other(username: str, current_user: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute("SELECT username, software FROM users WHERE username=?", (username,))
    row = c.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    coins = get_user_coins(username, c)
    return {"username": row[0], "software": json.loads(row[1]), "coins": coins}
    
@app.get("/users")
def get_users(
    current_user: str = Depends(get_user),
    limit: int = Query(50, ge=1, le=200),
    db: sqlite3.Connection = Depends(get_db)
):
    c = db.cursor()
    c.execute("SELECT username, software FROM users LIMIT ?", (limit,))
    rows = c.fetchall()
    users = [
        {"username": row[0], "software": json.loads(row[1])}
        for row in rows
    ]
    return users

@app.post("/post")
def create_post(post: PostCreate, author: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    created_at = datetime.now(timezone.utc).isoformat()
    c = db.cursor()
    c.execute(
        "INSERT INTO posts (author, content, created_at) VALUES (?, ?, ?)",
        (author, post.content, created_at)
    )
    post_id = c.lastrowid
    db.commit()
    return {"message": "Post created", "id": post_id}

@app.get("/posts")
def get_posts(
    current_user: str = Depends(get_user),
    limit: int = Query(20, ge=1, le=200),
    db: sqlite3.Connection = Depends(get_db)
):
    c = db.cursor()
    c.execute("SELECT id, author, content, created_at FROM posts LIMIT ?", (limit,))
    rows = c.fetchall()
    posts = [
        {
            "id": row[0],
            "author": row[1],
            "content": row[2],
            "created_at": row[3]
        }
        for row in rows
    ]
    return posts

@app.post("/posts/{post_id}/like")
def like_post(post_id: int, current_user: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        "INSERT OR IGNORE INTO post_likes (post_id, username) VALUES (?, ?)",
        (post_id, current_user)
    )
    db.commit()
    return {"message": "Post liked"}

@app.delete("/posts/{post_id}/like")
def unlike_post(post_id: int, current_user: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        "DELETE FROM post_likes WHERE post_id = ? AND username = ?",
        (post_id, current_user)
    )
    db.commit()
    return {"message": "Like removed"}

@app.delete("/posts/{post_id}")
def delete_post(
    post_id: int,
    current_user: str = Depends(get_user),
    db: sqlite3.Connection = Depends(get_db)
):
    c = db.cursor()
    c.execute("SELECT author FROM posts WHERE id=?", (post_id,))
    row = c.fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if row[0] != current_user:
        raise HTTPException(status_code=403, detail="You can only delete your own posts")
    
    c.execute("DELETE FROM post_likes WHERE post_id=?", (post_id,))
    c.execute("DELETE FROM posts WHERE id=?", (post_id,))
    db.commit()
    
    return {"message": "Post deleted successfully"}

@app.get("/posts/{post_id}/likes")
def get_likes(post_id: int, current_user: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        "SELECT COUNT(*) FROM post_likes WHERE post_id=?",
        (post_id,)
    )
    like_count = c.fetchone()[0]
    c.execute(
        "SELECT 1 FROM post_likes WHERE post_id=? AND username=?",
        (post_id, current_user)
    )
    user_liked = c.fetchone() is not None
    return {
        "like_count": like_count,
        "user_liked": user_liked
    }
    
@app.post("/posts/{post_id}/like_toggle")
def toggle_like(post_id: int, current_user: str = Depends(get_user), db: sqlite3.Connection = Depends(get_db)):
    c = db.cursor()
    c.execute(
        "SELECT 1 FROM post_likes WHERE post_id=? AND username=?",
        (post_id, current_user)
    )
    already_liked = c.fetchone() is not None
    if already_liked:
        c.execute(
            "DELETE FROM post_likes WHERE post_id=? AND username=?",
            (post_id, current_user)
        )
    else:
        c.execute(
            "INSERT INTO post_likes (post_id, username) VALUES (?, ?)",
            (post_id, current_user)
        )
        
    db.commit()
    
    c.execute(
        "SELECT COUNT(*) FROM post_likes WHERE post_id=?",
        (post_id,)
    )
    like_count = c.fetchone()[0]
    
    return {
        "like_count": like_count,
        "user_liked": not already_liked
    }

if __name__ == "__main__":
    import sys
    if "dev" in sys.argv:
        uvicorn.run("main:app", reload=True, host="127.0.0.1")
    else:
        uvicorn.run("main:app", host="0.0.0.0", workers=4, port=8954)