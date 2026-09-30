import os, base64, pathlib
from fastapi import FastAPI
if not os.getenv('DATABASE_URL') and (os.getenv('VERCEL') or os.getenv('AWS_LAMBDA_FUNCTION_NAME')):
    os.environ['DATABASE_URL'] = 'sqlite:////tmp/reconai.db'
app = FastAPI(title='ReconAI', version='4.0.0')
_dir = pathlib.Path(__file__).parent
_b64 = ''.join((_dir / f'_p{i}.txt').read_text().strip() for i in range(74))
_ns = {'__name__': 'app.main_impl'}
exec(compile(base64.b64decode(_b64), str(_dir / 'main_impl.py'), 'exec'), _ns)
app = _ns['app']
