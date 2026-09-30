from datetime import datetime,date
from decimal import Decimal
from typing import Optional
from sqlalchemy import String,DateTime,Date,ForeignKey,Numeric,Boolean,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column
from app.models_base import Base

class Account(Base):
    __tablename__="accounts"
    id:Mapped[int]=mapped_column(primary_key=True)
    business_id:Mapped[int]=mapped_column(ForeignKey("businesses.id"),index=True)
    code:Mapped[str]=mapped_column(String(30))
    name:Mapped[str]=mapped_column(String(120))
    type:Mapped[str]=mapped_column(String(30))
    normal_balance:Mapped[str]=mapped_column(String(6))
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    __table_args__=(UniqueConstraint("business_id","code"),UniqueConstraint("business_id","name"))

class JournalEntry(Base):
    __tablename__="journal_entries"
    id:Mapped[int]=mapped_column(primary_key=True)
    business_id:Mapped[int]=mapped_column(ForeignKey("businesses.id"),index=True)
    txn_date:Mapped[date]=mapped_column(Date)
    source_type:Mapped[str]=mapped_column(String(50))
    source_id:Mapped[Optional[int]]=mapped_column(nullable=True)
    description:Mapped[str]=mapped_column(Text)
    status:Mapped[str]=mapped_column(String(20),default="posted")
    created_by:Mapped[int]=mapped_column(ForeignKey("users.id"))
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)

class JournalLine(Base):
    __tablename__="journal_entry_lines"
    id:Mapped[int]=mapped_column(primary_key=True)
    journal_entry_id:Mapped[int]=mapped_column(ForeignKey("journal_entries.id"),index=True)
    account_id:Mapped[int]=mapped_column(ForeignKey("accounts.id"))
    debit:Mapped[Decimal]=mapped_column(Numeric(18,2),default=0)
    credit:Mapped[Decimal]=mapped_column(Numeric(18,2),default=0)
    description:Mapped[str]=mapped_column(Text,default="")
