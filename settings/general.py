from pydantic import Field
from pydantic_settings import BaseSettings

from settings.base import create_config_dict


class GeneralSettings(BaseSettings):
    debug: bool = Field(False, description="Нужно ли включить debug режим приложения")

    model_config = create_config_dict(
        env_prefix="APP_",
    )


general_settings = GeneralSettings()