from os import getenv
from dotenv import load_dotenv
from dataclasses import dataclass

assert load_dotenv(), '.env not found'

@dataclass(frozen=True)
class Settings:
    host: str
    port: int

settings = Settings(host=getenv('HOST'), port=int(getenv('PORT')))

