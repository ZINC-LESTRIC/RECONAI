import os, pathlib, importlib
from fastapi import FastAPI
if not os.getenv("DATABASE_URL") and (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")):
    os.environ["DATABASE_URL"] = "sqlite:////tmp/reconai.db"
app = FastAPI(title="ReconAI", version="4.0.0")
_dir = pathlib.Path(__file__).parent
parts = []
for i in range(37):
    mod = importlib.import_module(f"app.part_{i}")
    parts.append(mod.PART)
code = "".join(parts)
_ns = {"__name__": "app.main_impl"}
exec(compile(code, str(_dir / "main_impl.py"), "exec"), _ns)
app = _ns["app"]
