from djocker.dockerize.handlers.base import (
    BaseHandler
)
from djocker.dockerize.utils.constants import DATABASE_ENV_VARS, DATABASE_DEFAULT_PORT, DATABASE_VOLUME_PATH, \
    CACHE_DEFAULT_PORT, DATABASE_DEFAULT_CREDENTIALS


class ComposeHandler(BaseHandler):
    template_file = 'docker-compose.j2'
    out_file = 'docker-compose.yml'

    def handle(self):
        data = {
            'db_image': self.config.database_image,
            'db_type': self.config.database_type,
            'db_env_vars': DATABASE_ENV_VARS.get(self.config.database_type),
            'db_port': DATABASE_DEFAULT_PORT.get(self.config.database_type),
            'db_credentials': DATABASE_DEFAULT_CREDENTIALS,
            'db_volume_path': DATABASE_VOLUME_PATH.get(self.config.database_type),
            'cache_image': self.config.cache_image,
            'cache_port': CACHE_DEFAULT_PORT.get(self.config.cache_type),
            'python_version': self.config.python_version,
        }

        return self.write_template(data)
