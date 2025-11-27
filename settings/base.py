from pydantic_settings import SettingsConfigDict


def create_config_dict(**kwargs):
    return SettingsConfigDict(
        env_file_encoding="utf8",
        env_file=".env",
        extra="ignore",
        frozen=False,
        **kwargs,
    )