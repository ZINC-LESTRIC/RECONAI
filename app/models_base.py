from datetime import datetime,date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String,DateTime,Date,ForeignKey,Numeric,Boolean,Text,UniqueConstraint
from sqlalchemy.orm import DeclarativeBase,Mapped,mapped_column

class Base(DeclarativeBase): pass

class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(255))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class Business(Base):
    __tablename__="businesses"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(255))
    business_type:Mapped[str]=mapped_column(String(100),default="Food Stall")
    currency:Mapped[str]=mapped_column(String(10),default="PKR")
    owner_id:Mapped[int]=mapped_column(ForeignKey("users.id"))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class BusinessUser(Base):
    __tablename__="business_users"
    id:Mapped[int]=mapped_column(primary_key=True)
    business_id:Mapped[int]=mapped_column(ForeignKey("businesses.id"),index=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    role:Mapped[str]=mapped_column(String(30),default="owner")
    __table_args__=(UniqueConstraint("business_id","user_id"),)

class SessionToken(Base):
    __tablename__="session_tokens"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    token_hash:Mapped[str]=mapped_column(String(128),unique=True,index=True)
    expires_at:Mapped[datetime]=mapped_column(DateTime,index=True)
    revoked_at:Mapped[Optional[datetime]]=mapped_column(DateTime,nullable=True)
