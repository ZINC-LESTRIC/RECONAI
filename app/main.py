import os, zlib, base64, pathlib
# Writable DB path on Vercel (read-only FS except /tmp)
if not os.getenv("DATABASE_URL") and (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")):
    os.environ["DATABASE_URL"] = "sqlite:////tmp/reconai.db"
# Load full app body from compressed payload files (avoids huge single-file push limits)
_dir = pathlib.Path(__file__).parent
_z0 = _dir / "_z0.txt"
_z1 = _dir / "_z1.txt"
if _z0.exists() and _z1.exists():
    _code = zlib.decompress(base64.b64decode(_z0.read_text() + _z1.read_text()))
    exec(compile(_code, str(_dir / "main_impl.py"), "exec"), globals())
else:
    raise RuntimeError("Missing app/_z0.txt or app/_z1.txt — restore compressed app payload")
