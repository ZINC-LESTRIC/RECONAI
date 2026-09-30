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
        raise HTTPException(401,"Authentication required — please Log out and Sign in again")
    token=authorization.split(" ",1)[1].strip()
    try:
        payload=jwt.decode(token,SEC,algorithms=["HS256"])
        uid=int(payload["sub"])
        email=(payload.get("email") or f"user{uid}@demo.local").lower().strip()
        # Optional session check (warm instances)
        sid=payload.get("sid")
        if sid is not None:
            st=db.scalar(select(SessionToken).where(SessionToken.id==int(sid),SessionToken.token_hash==th(token)))
            if st and st.revoked_at:
                raise HTTPException(401,"Session revoked — please Sign in again")
        u=db.get(User,uid)
        if not u:
            # /tmp DB wiped on Vercel cold start — restore shell user with same id
            by_email=db.scalar(select(User).where(User.email==email))
            if by_email:
                u=by_email
            else:
                u=User(id=uid,email=email,password_hash="!")
                db.add(u); db.commit()
                u=db.get(User,uid) or db.scalar(select(User).where(User.email==email))
        if not u:
            raise HTTPException(401,"Authentication required — please Log out and Sign in again")
        setattr(u,"_active_business_id",int(x_business_id) if x_business_id and str(x_business_id).isdigit() else None)
        return u
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(401,"Authentication required — please Log out and Sign in again")

class AuthIn(BaseModel):
    email:str
    password:str=Field(min_length=8)

def register_auth(app):
    @app.post("/api/auth/register")
    def register(x:AuthIn,db:Session=Depends(dbdep)):
        e=x.email.lower().strip()
        if db.scalar(select(User).where(User.email==e)): raise HTTPException(409,"User already exists")
        u=User(email=e,password_hash=hp(x.password)); db.add(u); db.commit()
        tok,exp=issue(db,u.id,email=e); db.commit()
        return {"email":u.email,"token":tok,"expires_at":exp.isoformat()}

    @app.post("/api/auth/login")
    def login(x:AuthIn,db:Session=Depends(dbdep)):
        u=db.scalar(select(User).where(User.email==x.email.lower().strip()))
        if not u or not vp(x.password,u.password_hash): raise HTTPException(401,"Invalid credentials")
        tok,exp=issue(db,u.id,email=u.email); db.commit()
        return {"email":u.email,"token":tok,"expires_at":exp.isoformat()}

    @app.post("/api/auth/logout")
    def logout(): return {"ok":True}
