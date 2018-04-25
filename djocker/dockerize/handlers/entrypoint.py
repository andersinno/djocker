from djocker.dockerize.handlers.base import BaseHandler
from djocker.dockerize.utils.constants import DATABASE_DEFAULT_PORT


class EntrypointHandler(BaseHandler):
    template_file = 'docker-entrypoint.j2'
    out_file = 'docker-entrypoint.sh'

    def handle(self):
        data = {
            'db_port': DATABASE_DEFAULT_PORT.get(self.config.database_type),
            'python_version': self.config.python_version
        }

        self.write_template(data, executable=True)
