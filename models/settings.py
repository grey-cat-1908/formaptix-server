from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database: str
    secret: str
    port: int
    admin_password: str
    disable_admin: bool


settings = Settings()
