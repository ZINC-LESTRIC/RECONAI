import os, zlib, base64, pathlib
if not os.getenv("DATABASE_URL") and (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")):
    os.environ["DATABASE_URL"] = "sqlite:////tmp/reconai.db"
_dir = pathlib.Path(__file__).parent
def _b64(name):
    return "".join((_dir / name).read_text().split())
_code = zlib.decompress(base64.b64decode(_b64("_z0.txt") + _b64("_z1.txt")))
exec(compile(_code, str(_dir / "main_impl.py"), "exec"), globals())
