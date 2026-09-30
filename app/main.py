import pathlib
from fastapi import FastAPI
from fastapi.responses import FileResponse,HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.models_base import Base
from app.models_acct import Account,JournalEntry,JournalLine  # register tables on Base.metadata
from app.helpers_auth import eng

Base.metadata.create_all(eng)
app=FastAPI(title="ReconAI",version="4.0.0-demo")
app.add_middleware(CORSMiddleware,allow_origins=["*"],allow_credentials=True,allow_methods=["*"],allow_headers=["*"])

from app.routes_auth import register_auth
from app.routes_biz import register_biz
register_auth(app)
register_biz(app)

@app.get("/health")
def health(): return {"status":"ok","service":"reconai","version":"4.0.0-demo"}

@app.get("/")
def root():
    p=pathlib.Path(__file__).resolve().parent.parent/"static"/"index.html"
    if p.is_file(): return FileResponse(str(p))
    return HTMLResponse("<h1>ReconAI Demo</h1>")
