import os
from pathlib import Path
from typing import Tuple, Type

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict, YamlConfigSettingsSource


class GitlabSettings(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True, extra='ignore')

    host: str = Field(alias='CI_SERVER_HOST')
    private_token: SecretStr = Field(alias='GITLAB_BOT_PAT')

    @property
    def url(self) -> str:
        return f'https://{self.host}'


class ProjectSettings(BaseSettings):
    model_config = SettingsConfigDict(populate_by_name=True, extra='ignore')

    project_id: int = Field(alias='CI_PROJECT_ID')
    merge_request_iid: int = Field(alias='CI_MERGE_REQUEST_IID')


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        yaml_file=os.getenv('CONFIG_FILE', '.config.yaml' if Path('.config.yaml').exists() else None))

    gitlab: GitlabSettings
    project: ProjectSettings

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: Type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
            ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)
