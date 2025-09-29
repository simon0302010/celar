from fastapi import FastAPI, HTTPException, Depends, Header
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from pydantic import BaseModel
from typing import List
import sqlite3
import bcrypt
import sys
import os
from fastapi import Query

# vars for tokens
TOKEN_KEY = os.environ.get("CELAR_KEY")
TOKEN_ALGORITHM = "HS256"

if not TOKEN_KEY:
    print("Please set CELAR_KEY.")
    sys.exit(1)

app = FastAPI()
DB_FILE = "database.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
       CREATE TABLE IF NOT EXISTS users (
           username TEXT PRIMARY KEY,
           password TEXT,
           age INTEGER,
           interests TEXT
       ) 
    """)
    conn.commit()
    conn.close()
    
init_db()

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

# models
class UserCreate(BaseModel):
    username: str
    password: str
    age: int
    interests: List[str]

class UserLogin(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    username: str
    age: int
    interests: List[str]

# endpoints
@app.post("/register")
def register(user: UserCreate):
    salt = bcrypt.gensalt()
    hashed_pw = bcrypt.hashpw(user.password.encode('utf-8'), salt).decode('utf-8')
    
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username FROM users WHERE username=?", (user.username,))
    if c.fetchone():
        raise HTTPException(status_code=400, detail="Username already exists")
    c.execute("INSERT INTO users (username, password, age, interests) VALUES (?, ?, ?, ?)",
              (user.username, hashed_pw, user.age, ",".join(user.interests)))
    conn.commit()
    conn.close()
    return {"message": "User registered successfully"}

@app.post("/login")
def login(user: UserLogin):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT password FROM users WHERE username=?", (user.username,))
    row = c.fetchone()
    conn.close()
    if not row or not bcrypt.checkpw(user.password.encode('utf-8'), row[0].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = generate_token(
        data={"sub": user.username},
        expires=timedelta(hours=24)
    )
    return {"message": "Login successful", "access_token": access_token, "token_type": "bearer"}

@app.get("/profile")
def read_me(current_user: str = Depends(get_user)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, age, interests FROM users WHERE username=?", (current_user,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": row[0], "age": row[1], "interests": row[2].split(",")}

@app.get("/profile/{username}")
def read_other(username: str, current_user: str = Depends(get_user)):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, age, interests FROM users WHERE username=?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    return {"username": row[0], "age": row[1], "interests": row[2].split(",")}
    
@app.get("/users")
def get_users(
    current_user: str = Depends(get_user),
    limit: int = Query(50, ge=1, le=200)
):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT username, age, interests FROM users LIMIT ?", (limit,))
    rows = c.fetchall()
    conn.close()
    users = [
        {"username": row[0], "age": row[1], "interests": row[2].split(",")}
        for row in rows
    ]
    return users