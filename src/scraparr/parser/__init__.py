import os
from typing import Optional, Dict, Mapping, Union

ConfigDict = Dict[str, Union[str, bool]]
FullConfig = Dict[str, Optional[ConfigDict]]

class ConfigParser:

    services = [
        'sonarr', 'radarr', 'prowlarr',
        'bazarr', 'readarr', 'jellyseerr', 'overseerr'
    ]

    config: FullConfig = {
        'general': {},
        'ssl': {
            'accept_insecure_certificates': False,
        },
        'auth': None,
    }

    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ConfigParser, cls).__new__(cls)
        return cls.instance

    def _build_config(self, env: Mapping[str, str]) -> FullConfig:
        

        accept_insecure_certificates = env.get('SCRAPARR_ACCEPT_INSECURE_CERTIFICATES')
        if 'ssl' not in self.config or self.config['ssl'] is None:
            self.config['ssl'] = {}

        self.config['ssl']['accept_insecure_certificates'] = (
            accept_insecure_certificates.lower() == 'true' if accept_insecure_certificates else False
        )

        optional_fields = ['alias', 'api_version', 'interval', 'detailed']

        for service in self.services:
            prefix = service.upper()
            url = env.get(f'{prefix}_URL')
            api_key = env.get(f'{prefix}_API_KEY')

            if url and api_key:
                service_config: ConfigDict = {
                    'url': url,
                    'api_key': api_key,
                    **{
                        field: val
                        for field in optional_fields
                        if (val := env.get(f'{prefix}_{field.upper()}')) is not None
                    }
                }
                self.config[service] = service_config
            else:
                self.config[service] = None

        return self.config

    def parse_dotenv_config(self, path: str = "/scraparr/.env") -> FullConfig:
        return self._build_config(dotenv_values(path))  # type: ignore

    def parse_env_config(self) -> FullConfig:
        return self._build_config(os.environ)