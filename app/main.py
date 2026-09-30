from datetime import datetime, date, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional
import os, pathlib, hashlib, hmac, secrets, json, csv, io, re, urllib.request

from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import create_engine, String, DateTime, Date, ForeignKey, Numeric, Boolean, Text, UniqueConstraint, select, func, and_
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session
import jwt

# On Vercel/serverless the filesystem is read-only except /tmp
_default_sqlite = 'sqlite:////tmp/reconai.db' if (os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME')) else 'sqlite:///./reconai.db'
DB_URL = os.getenv('DATABASE_URL', _default_sqlite)
AUTO_CREATE = os.getenv('RECONAI_AUTO_CREATE_SCHEMA', 'true').lower() == 'true'
DEV_HEADER_AUTH = os.getenv('RECONAI_DEV_HEADER_AUTH', 'false').lower() == 'true'
engine = create_engine(DB_URL, connect_args={'check_same_thread': False} if DB_URL.startswith('sqlite') else {})
JWT_SECRET = os.getenv('RECONAI_JWT_SECRET', 'dev-only-change-this-secret-key-please-set-a-strong-production-secret-123456')
JWT_ALG = 'HS256'
TOKEN_HOURS = 24

class Base(DeclarativeBase): pass

# TEMPORARY_MINIMAL_STUB - will replace with full content
app = FastAPI(title='ReconAI', version='4.0.0')

@app.get('/health')
def health():
    return {'status': 'ok', 'service': 'reconai', 'version': '4.0.0'}

@app.get('/')
def root():
    return {'message': 'ReconAI demo - full app loading next commit'}
