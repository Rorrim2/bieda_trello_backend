import hmac
import secrets
import hashlib
import string

from django.contrib.auth.hashers import UNUSABLE_PASSWORD_PREFIX


def generate_salt(length: int =16) -> str:
    return secrets.token_hex(length)

def generate_random_alpha_num_str(length: int =16) -> str:
    return "".join([secrets.choice(
            string.digits+string.ascii_letters
        ) for i in range(length)])

def generate_random_str(length: int =16) -> str:
    return "".join([secrets.choice(
            string.digits+string.ascii_letters+string.punctuation
        ) for i in range(length)])

def hash_passwd(salt: str, passwd: str) -> str:
    return hmac.new(salt.encode('utf_8'), 
                    msg=passwd.encode('utf_8'),
                    digestmod=hashlib.sha256
                ).hexdigest() 

def validate_passwd(salt: str, passwd: str, hashed: str) -> bool:
    usr_hash = hash_passwd(salt, passwd)
    return usr_hash == hashed     

def create_jwt_id() -> str:
    return f"_{generate_salt(15)}__{generate_random_str(30)}_"

def create_unusable_password() -> str:
    return UNUSABLE_PASSWORD_PREFIX + generate_random_alpha_num_str(40)