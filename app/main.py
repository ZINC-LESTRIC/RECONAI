import os, zlib, base64, pathlib

_dir = pathlib.Path(__file__).parent
_b64 = "".join((_dir / f"_z{i}.txt").read_text().strip() for i in range(8))
exec(compile(zlib.decompress(base64.b64decode(_b64)), str(_dir / "main_impl.py"), "exec"), globals())
