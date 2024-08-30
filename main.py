from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3
import os

app = FastAPI()

# 確保數據庫文件存在
if not os.path.exists("./test.db"):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT NOT NULL,
                  email TEXT UNIQUE NOT NULL)''')
    conn.commit()
    conn.close()

class User(BaseModel):
    name: str
    email: str

@app.get("/")
async def read_root():
    return {"message": "歡迎來到我的簡單API！"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"你好，{name}！"}

@app.post("/users")
async def create_user(user: User):
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (name, email) VALUES (?, ?)", (user.name, user.email))
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()
    return {"message": "User created successfully"}

@app.get("/users")
async def get_users():
    conn = sqlite3.connect("test.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    users = c.fetchall()
    conn.close()
    return {"users": [{"id": user[0], "name": user[1], "email": user[2]} for user in users]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)