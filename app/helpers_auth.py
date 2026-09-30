import os,hashlib,hmac,secrets
from datetime import datetime,timedelta
from decimal import Decimal,ROUND_HALF_UP
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
import jwt
from app.models_base import Base,SessionToken

_db="sqlite:////tmp/reconai.db" if (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")) else "sqlite:///./reconai.db"
DB=os.getenv("DATABASE_URL",_db)
eng=create_engine(DB,connect_args={"check_same_thread":False} if DB.startswith("sqlite") else {})
SEC=os.getenv("RECONAI_JWT_SECRET","dev-demo-secret-change-me-in-production-12345678")
MONEY=Decimal("0.01")

def money(x):
    return Decimal(str(x)).quantize(MONEY,rounding=ROUND_HALF_UP)

def hp(p):
    s=secrets.token_bytes(16)
    return s.hex()+":"+hashlib.pbkdf2_hmac("sha256",p.encode(),s,120000).hex()

def vp(p,h):
    try:
        s,d=h.split(":")
        return hmac.compare_digest(hashlib.pbkdf2_hmac("sha256",p.encode(),bytes.fromhex(s),120000).hex(),d)
    except: return False

def th(t): return hashlib.sha256(t.encode()).hexdigest()

def issue(db,uid,email=None):
    exp=datetime.utcnow()+timedelta(hours=24)
    st=SessionToken(user_id=uid,token_hash="x",expires_at=exp); db.add(st); db.flush()
    claims={"sub":str(uid),"sid":st.id,"exp":exp}
    if email: claims["email"]=email
    tok=jwt.encode(claims,SEC,algorithm="HS256")
    st.token_hash=th(tok); return tok,exp
