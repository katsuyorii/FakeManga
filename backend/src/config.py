from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str
    
    REDIS_HOST: str
    REDIS_PORT: str

    RABBITMQ_DEFAULT_USER: str
    RABBITMQ_DEFAULT_PASS: str
    RABBITMQ_HOST: str
    RABBITMQ_PORT: int

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    REFRESH_TOKEN_EXPIRE_DAYS: int

    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASSWORD: str
    
    @property
    def DATABASE_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'
    
    @property
    def REDIS_URL(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"
    
    @property
    def RABBIT_MQ_URL(self) -> str:
        return f"amqp://{self.RABBITMQ_DEFAULT_USER}:{self.RABBITMQ_DEFAULT_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}//"

    model_config = SettingsConfigDict(env_file='../.env', extra='allow')

settings = Settings()