from pwdlib import PasswordHash
import hashlib

password_hash = PasswordHash.recommended()



def hash_password(password: str):
    return password_hash.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return password_hash.verify(plain_password, hashed_password)


def hash_refresh_token(token: str):
    return hashlib.sha256(token.encode()).hexdigest()