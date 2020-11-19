from .crypto import generate_salt, generate_random_str

def create_jwt_id():
    return f"_{generate_salt(15)}__{generate_random_str(30)}_"

