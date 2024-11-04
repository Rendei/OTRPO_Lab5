from fastapi import HTTPException, Security, Header
from config import load_config

config = load_config()
auth_token = config["auth_token"]

def verify_token(token: str = Header(...)):
    if token != auth_token:
        raise HTTPException(status_code=403, detail="Недействительный токен")
