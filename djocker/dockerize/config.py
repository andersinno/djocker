class DockerizeConfig:
    def __init__(self, **kwargs):
        self.base_image = kwargs.get('base_image', None)
        self.operating_system = kwargs.get('operating_system', None)
        self.database_image = kwargs.get('database_image', None)
        self.database_type = kwargs.get('database_type', None)
        self.cache_image = kwargs.get('cache_image', None)
        self.cache_type = kwargs.get('cache_type', None)
        self.requirement_files = kwargs.get('requirement_files', None)
        self.base_dir = kwargs.get('base_dir', None)
        self.python_version = kwargs.get('python_version', None)
        self.application_server = kwargs.get('application_server', None)
        self.wsgi_dot_path = kwargs.get('uwsgi_dot_path', None)
        self.wsgi_path = kwargs.get('uwsgi_path', None)
