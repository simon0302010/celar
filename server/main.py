from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import sqlite3
import bcrypt

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
    return {"message": "Login successful"}