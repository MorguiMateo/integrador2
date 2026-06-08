## ⏺ - config.py — lee las variables de entorno (.env) y las expone como un objeto settings tipado con Pydantic, accesible desde cualquier parte de la app.
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30 

    model_config = SettingsConfigDict(
        env_file=".env",
        ##extra ignora las variables en .env no declaradas
        extra="ignore",
    )

##se sintancia una vez y se importa en todos lados
settings = Settings()
