from datetime import date
from decimal import Decimal
from sqlalchemy import select
from app.models_acct import Account,JournalEntry,JournalLine
from app.helpers_auth import money

CHART=[
 ("1000","Cash","asset","debit"),("1100","Bank","asset","debit"),("1200","Accounts Receivable","asset","debit"),
 ("1300","Inventory","asset","debit"),("2000","Accounts Payable","liability","credit"),
 ("3000","Owner Capital","equity","credit"),("3100","Owner Drawings","equity","debit"),
 ("4000","Sales Revenue","income","credit"),("5000","Cost of Goods Sold","expense","debit"),
 ("5100","Other Expenses","expense","debit"),("5200","Rent Expense","expense","debit"),
 ("5300","Utilities Expense","expense","debit"),("5400","Inventory Adjustment","expense","debit"),
]

def seed_accounts(db,bid):
    for code,name,typ,nb in CHART:
        if not db.scalar(select(Account).where(Account.business_id==bid,Account.code==code)):
            db.add(Account(business_id=bid,code=code,name=name,type=typ,normal_balance=nb))

def acct(db,bid,name):
    a=db.scalar(select(Account).where(Account.business_id==bid,Account.name==name))
    if not a: raise Exception(f"Missing account: {name}")
    return a

def post_journal(db,bid,uid,txn_date,source_type,source_id,description,lines):
    clean=[]; debit=Decimal(0); credit=Decimal(0)
    for aid,d,c,desc in lines:
        d=money(d); c=money(c)
        if d<0 or c<0 or (d>0 and c>0): raise Exception("Invalid journal line")
        debit+=d; credit+=c; clean.append((aid,d,c,desc))
    if debit<=0 or debit!=credit: raise Exception(f"Unbalanced: {debit} vs {credit}")
    je=JournalEntry(business_id=bid,txn_date=txn_date,source_type=source_type,source_id=source_id,description=description,created_by=uid)
    db.add(je); db.flush()
    for aid,d,c,desc in clean:
        db.add(JournalLine(journal_entry_id=je.id,account_id=aid,debit=d,credit=c,description=desc))
    return je
