import os

from jinja2 import Environment, FileSystemLoader


class HandlerException(Exception):
    pass


class BaseHandler:
    template_file = None
    out_file = None

    def __init__(self, config):
        self.config = config

        assert self.template_file, 'No template configured'
        assert self.out_file, 'No out file configured'
        self.template_root = self._get_template_root()

    def _get_template_root(self):
        current_path = os.path.dirname(os.path.abspath(__file__))
        relative_template_path = '../templates'
        return os.path.join(current_path, relative_template_path)

    def build_template(self, data):
        jinja_env = Environment(loader=FileSystemLoader(self.template_root),
                                trim_blocks=True)
        return jinja_env.get_template(self.template_file).render(**data)

    def write_template(self, data, executable=False):
        file_path = os.path.join(self.config.base_dir, self.out_file)
        print(file_path)
        write_data = self.build_template(data)
        with open(file_path, 'w+') as file:
            file.write(write_data)

    def handle(self):
        raise NotImplementedError
