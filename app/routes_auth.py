from datetime import datetime
from typing import Optional
from fastapi import Depends,HTTPException,Header
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
import jwt
from app.models_base import User,SessionToken
from app.helpers_auth import eng,hp,vp,issue,th,SEC

def dbdep():
    with Session(eng) as db: yield db

def current_user(authorization:Optional[str]=Header(None),x_business_id:Optional[str]=Header(None),db:Session=Depends(dbdep)):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(401,"Authentication required")
    token=authorization.split(" ",1)[1].strip()
    try:
        payload=jwt.decode(token,SEC,algorithms=["HS256"])
        sid=payload.get("sid"); uid=payload.get("sub")
        st=db.scalar(select(SessionToken).where(SessionToken.id==int(sid),SessionToken.token_hash==th(token)))
        if not st or st.revoked_at or st.expires_at<datetime.utcnow() or st.user_id!=int(uid): raise ValueError()
        u=db.get(User,int(uid))
        if not u: raise ValueError()
        setattr(u,"_active_business_id",int(x_business_id) if x_business_id and str(x_business_id).isdigit() else None)
        return u
    except Exception:
        raise HTTPException(401,"Authentication required")

class AuthIn(BaseModel):
    email:str
    password:str=Field(min_length=8)

def register_auth(app):
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
