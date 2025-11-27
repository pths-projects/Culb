from pydantic import Field
from pydantic_settings import BaseSettings
from sqlalchemy import URL

from settings.base import create_config_dict


class DatabaseSettings(BaseSettings):
    host: str = Field(..., description="хост где размещена БД")
    port: int = Field(5432, description="порт подключения, дефолтный для Postgres")
    name: str = Field(..., description="имя БД")
    user: str = Field(..., description="имя пользователя")
    password: str = Field(..., description="пароль пользователя")
    driver: str = Field("postgresql+psycopg2", description="Драйвер подключения к БД")

    model_config = create_config_dict(
        env_prefix="DATABASE_",
    )

    @property
    def full_url(self) -> URL:
        return URL.create(
            drivername=self.driver,
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.name,
        )


# Конфигурация из твоего config.py
database_settings = DatabaseSettings(
    host='80b82e2fe4853703fb651141.twc1.net',
    port=5432,
    name='default_db',
    user='gen_user',
    password='gNS<h=d5gmiUXJ',
    driver='postgresql+psycopg2'
)