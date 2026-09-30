import os, zlib, base64, pathlib
from fastapi import FastAPI

# Writable DB on Vercel (read-only FS except /tmp)
if not os.getenv("DATABASE_URL") and (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")):
    os.environ["DATABASE_URL"] = "sqlite:////tmp/reconai.db"

# Placeholder so Vercel static analysis finds a top-level FastAPI app
app = FastAPI(title="ReconAI", version="4.0.0")

_dir = pathlib.Path(__file__).parent
_b64 = "".join((_dir / f"_zb{i}.txt").read_text().strip() for i in range(4))
_ns = {"__name__": "app.main_impl"}
exec(compile(zlib.decompress(base64.b64decode(_b64)), str(_dir / "main_impl.py"), "exec"), _ns)

# Replace with the real application (routes, models, everything)
app = _ns["app"]
