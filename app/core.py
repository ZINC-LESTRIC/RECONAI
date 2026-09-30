import os,hashlib,hmac,secrets
from datetime import datetime,timedelta
from typing import Optional
from sqlalchemy import create_engine,String,DateTime,ForeignKey
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column,Session
import jwt
_db="sqlite:////tmp/reconai.db" if (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")) else "sqlite:///./reconai.db"
DB=os.getenv("DATABASE_URL",_db)
eng=create_engine(DB,connect_args={"check_same_thread":False} if DB.startswith("sqlite") else {})
SEC=os.getenv("RECONAI_JWT_SECRET","dev-demo-secret-change-me-in-production-12345678")
class Base(DeclarativeBase): pass
class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class SessionToken(Base):
    __tablename__="session_tokens"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    token_hash:Mapped[str]=mapped_column(String(128),unique=True,index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime,index=True)
    revoked_at:Mapped[Optional[datetime]]=mapped_column(DateTime,nullable=True)
Base.metadata.create_all(eng)
def hp(p):
    s=secrets.token_bytes(16)
    return s.hex()+":"+hashlib.pbkdf2_hmac("sha256",p.encode(),s,120000).hex()
def vp(p,h):
    try:
        s,d=h.split(":")
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256",p.encode(),bytes.fromhex(s),120000).hex(),d)
    except: return False
def issue(db,uid):
    exp=datetime.utcnow()+timedelta(hours=24)
    st=SessionToken(user_id=uid,token_hash="x",expires_at=exp); db.add(st); db.flush()
    tok=jwt.encode({"sub":str(uid),"sid":st.id,"exp":exp},SEC,algorithm="HS256")
    st.token_hash=hashlib.sha256(tok.encode()).hexdigest(); return tok,exp
