from datetime import date
from decimal import Decimal
from fastapi import Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models_base import Business,BusinessUser
from app.helpers_acct import seed_accounts,acct,post_journal,money
from app.routes_auth import dbdep,current_user

class BusinessIn(BaseModel):
    name:str
    business_type:str="Food Stall"
    currency:str="PKR"
    opening_cash:Decimal=Decimal(0)

def register_biz(app):
    @app.post("/api/business")
    def create_business(x:BusinessIn,user=Depends(current_user),db:Session=Depends(dbdep)):
        b=Business(name=x.name.strip(),business_type=x.business_type or "Food Stall",currency=x.currency or "PKR",owner_id=user.id)
        db.add(b); db.flush()
        db.add(BusinessUser(business_id=b.id,user_id=user.id,role="owner"))
        seed_accounts(db,b.id)
        cash=money(x.opening_cash or 0)
        if cash>0:
            post_journal(db,b.id,user.id,date.today(),"opening_cash",b.id,f"Opening cash: {b.name}",[
                (acct(db,b.id,"Cash").id,cash,0,"Opening cash"),
                (acct(db,b.id,"Owner Capital").id,0,cash,"Opening capital"),
            ])
        db.commit()
        return {"id":b.id,"name":b.name,"business_type":b.business_type,"currency":b.currency}

    @app.get("/api/business")
    def get_business(user=Depends(current_user),db:Session=Depends(dbdep)):
        bid=getattr(user,"_active_business_id",None)
        if bid:
            b=db.get(Business,bid)
            if b and db.scalar(select(BusinessUser).where(BusinessUser.business_id==b.id,BusinessUser.user_id==user.id)):
                return {"id":b.id,"name":b.name,"business_type":b.business_type,"currency":b.currency}
        bu=db.scalar(select(BusinessUser).where(BusinessUser.user_id==user.id))
        if not bu: raise HTTPException(400,"Business setup required")
        b=db.get(Business,bu.business_id)
        return {"id":b.id,"name":b.name,"business_type":b.business_type,"currency":b.currency}

    @app.get("/api/businesses")
    def list_businesses(user=Depends(current_user),db:Session=Depends(dbdep)):
        rows=db.scalars(select(BusinessUser).where(BusinessUser.user_id==user.id)).all()
        out=[]
        for r in rows:
            b=db.get(Business,r.business_id)
            if b: out.append({"id":b.id,"name":b.name,"business_type":b.business_type,"currency":b.currency,"role":r.role})
        return out
