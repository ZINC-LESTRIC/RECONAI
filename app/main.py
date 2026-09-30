import pathlib
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core import eng, User, hp, vp, issue

app=FastAPI(title="ReconAI",version="4.0.0-demo")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
def dbdep():
    with Session(eng) as db: yield db

@app.get("/health")
def health(): return {"status":"ok","service":"reconai","version":"4.0.0-demo"}

class AuthIn(BaseModel):
    email:str
    password:str=Field(min_length=8)

@app.post("/api/auth/register")
def register(x:AuthIn,db:Session=Depends(dbdep)):
    e=x.email.lower().strip()
    if db.scalar(select(User).where(User.email==e)): raise HTTPException(409,"User already exists")
    u=User(email=e,password_hash=hp(x.password)); db.add(u); db.commit()
    tok,exp=issue(db,u.id); db.commit()
    return {"email":u.email,"token":tok,"expires_at":exp.isoformat()}

@app.post("/api/auth/login")
def login(x:AuthIn,db:Session=Depends(dbdep)):
    u=db.scalar(select(User).where(User.email==x.email.lower().strip()))
    if not u or not vp(x.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
    tok,exp=issue(db,u.id); db.commit()
    return {"email":u.email,"token":tok,"expires_at":exp.isoformat()}

@app.post("/api/auth/logout")
def logout(): return {"ok":True}

@app.get("/")
def root():
    p=pathlib.Path(__file__).resolve().parent.parent/"static"/"index.html"
    if p.is_file(): return FileResponse(str(p))
    return HTMLResponse("<h1>ReconAI Demo</h1><p>API up. Use /api/auth/register</p>")
