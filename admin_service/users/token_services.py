import time
from typing import Optional

import jwt


def decode_token(token: str) -> Optional[dict]:
    try:
        decoded_token = jwt.decode(token, options={"verify_signature": False})
        return decoded_token if decoded_token["exp"] >= time.time() else None
    except Exception:
        return None
