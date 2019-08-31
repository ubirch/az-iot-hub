from binascii import b2a_base64, a2b_base64
from hashlib import sha256
from time import time
from hmac import HMAC
from urllib.parse import quote_plus, urlencode, quote

def generate_sas_token(uri, key, policy_name="iothubowner", expiry=None):
    # uri = quote(uri, safe='').lower()
    encoded_uri = quote(uri, safe='')

    if expiry is None:
        expiry = time() + 3600
    ttl = int(expiry)

    sign_key = '%s\n%d' % (encoded_uri, ttl)
    signature = b2a_base64(HMAC(a2b_base64(key), sign_key.encode('utf-8'), sha256).digest())
    
    result = 'SharedAccessSignature ' + urlencode({
        'sr': uri,
        'sig': signature[:-1],
        'se': str(ttl),
        'skn': policy_name
    })

    return result