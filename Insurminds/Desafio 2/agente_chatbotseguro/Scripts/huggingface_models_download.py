import os
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
os.environ['HF_HUB_DISABLE_SSL_VERIFICATION'] = '1'

# Monkey-patch na sessão do requests ANTES de importar huggingface_hub
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import urllib3
urllib3.disable_warnings()

_original_send = requests.Session.send
def _patched_send(self, *args, **kwargs):
    kwargs['verify'] = False
    return _original_send(self, *args, **kwargs)
requests.Session.send = _patched_send

from sentence_transformers import SentenceTransformer

print('Fazendo download do modelo de embeddings...')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
model.save('./cache/all-MiniLM-L6-v2')
print("Modelo salvo com sucesso!")