import pathlib as _p
_code = "".join((_p.Path(__file__).parent / f"_c{i}.txt").read_text() for i in range(5))
exec(compile(_code, str(_p.Path(__file__).parent / "main_impl.py"), "exec"), globals())
