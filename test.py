from fastapi import FastAPI
from src.core.setting import settings
from src.util.auth import get_password_hash

print(get_password_hash("Nik@123"))

