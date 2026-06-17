import cloudinary
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    SECRET_KEY: str

    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    CLOUDINARY_CLOUD_NAME: str = ""
    CLOUDINARY_API_KEY: str = ""
    CLOUDINARY_API_SECRET: str = ""

    MP_ACCESS_TOKEN: str = ""
    MP_PUBLIC_KEY: str = ""
    MP_WEBHOOK_SECRET: str = ""
    MP_NOTIFICATION_URL: str = ""

    ##url del front, la usa mercado pago para volver despues de pagar
    FRONTEND_URL: str = "http://localhost:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        ##extra ignora las variables en .env no declaradas
        extra="ignore",
    )

##se sintancia una vez y se importa en todos lados
settings = Settings()

cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True,
)
