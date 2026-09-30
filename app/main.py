import os, zlib, base64, pathlib

# Writable DB on Vercel (read-only FS except /tmp)
if not os.getenv("DATABASE_URL") and (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")):
    os.environ["DATABASE_URL"] = "sqlite:////tmp/reconai.db"

_dir = pathlib.Path(__file__).parent
_b64 = "".join((_dir / f"_zb{i}.txt").read_text().strip() for i in range(4))
_ns = {}
exec(compile(zlib.decompress(base64.b64decode(_b64)), str(_dir / "main_impl.py"), "exec"), _ns)

# Required for Vercel FastAPI entrypoint detection
app = _ns["app"]
