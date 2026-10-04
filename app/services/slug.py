import secrets
import string

ALPHABET=string.ascii_letters + string.digits

def generate_slug(length:int=7)->str:
    return "".join(secrets.choice(ALPHABET) for _ in range(length))