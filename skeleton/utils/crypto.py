import hmac
import secrets
import hashlib

def generate_salt(length: int =16) -> str:
    return secrets.token_hex(length)

def hash_passwd(salt: str, passwd: str) -> str:
    return hmac.new(salt.encode('utf_8'), 
                    msg=passwd.encode('utf_8'),
                    digestmod=hashlib.sha256
                ).hexdigest() 

def validate_passwd(salt: str, passwd: str, hashed: str) -> bool:
    usr_hash = hash_passwd(salt, passwd)
    return usr_hash == hashed     