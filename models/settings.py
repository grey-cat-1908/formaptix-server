from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database: str
    secret: str
    port: int


settings = Settings()
