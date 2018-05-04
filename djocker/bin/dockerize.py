import os
import re
import sys
from collections import OrderedDict
from pathlib import Path

from djocker.dockerize.config import DockerizeConfig
from djocker.dockerize.handlers.compose import ComposeHandler
from djocker.dockerize.handlers.entrypoint import EntrypointHandler
from djocker.dockerize.handlers.ubuntu import UbuntuHandler
from djocker.utils import cli
from djocker.utils.ask import ValidationError, ask
from djocker.utils.colors import Colors, color
from djocker.utils.docker_index import DockerIndex
from djocker.utils.file import find_filename


class FakeDjangoSettings:
    pass


OS_IMAGE_HANDLERS = {
    'ubuntu': UbuntuHandler,
}

verbose_name_db_mapping = OrderedDict([
    ('postgres', 'PostgreSQL'),
    ('mariadb', 'MariaDB'),
    ('mysql', 'MySQL'),
])

verbose_name_cache_mapping = OrderedDict([
    ('redis', 'Redis'),
    ('memcached', 'Memcached'),
])


def get_database_type(django_settings):
    database_mapping = {
        'postgresql_psycopg2': 'postgres',
        'mysql': 'mysql',
    }

    django_databases = getattr(django_settings, 'DATABASES', [])
    if not django_databases:
        return None

    num_databases = len(django_databases)
    print("\nChecking for databases in settings... ", end="", flush=True)

    if num_databases > 1:
        print(color("mutiple database setups", Colors.WARNING))
        return None

    default_database = django_databases['default']['ENGINE']
    database_engine = default_database.split('.')[-1]
    database_type = database_mapping.get(database_engine)
    if not database_type:
        print(color("no auto setup support for {}".format(database_engine), Colors.WARNING))
        return None

    print(color("found {}".format(database_type), Colors.OKGREEN))
    return database_type


def get_cache_type(django_settings):
    supported_caches = ['memcached', 'redis']
    caches_setting = getattr(django_settings, 'CACHES', {})

    if not caches_setting:
        return None

    num_caches = len(caches_setting)
    print("\nChecking for caches in settings... ", end="", flush=True)

    cache_type = None
    if num_caches > 1:
        print(color("mutiple cache setups found", Colors.WARNING))
        return None

    default_cache = caches_setting['default']['BACKEND']
    for supported_cache in supported_caches:
        if supported_cache in default_cache:
            cache_type = supported_cache

    if not cache_type:
        print(color("no auto setup support for {}".format(default_cache), Colors.WARNING))
        return None

    return cache_type


class DockerImageValidator:
    def validate(self, value):
        client = DockerIndex()

        image_info = value.split(':')
        if len(image_info) != 2:
            raise ValidationError('The image must include both a repo and a tag')
        repo, tag = image_info

        tags = client.repo_tags(repo)
        if not tags:
            raise ValidationError('No such repo')
        if tag not in tags:
            raise ValidationError('No such tag for "{}"'.format(repo))


class DockerImageVersionValidator(DockerImageValidator):
    def __init__(self, repo_name):
        self.repo_name = repo_name

    def validate(self, value):
        image_with_version = "{}:{}".format(self.repo_name, value)
        super().validate(image_with_version)


class Dockerize(cli.Command):
    def __init__(self):
        self.print_logo()
        super().__init__()
        self.setup_paths()
        self.django_available = False
        self.django_settings_path = None
        self.django_settings = FakeDjangoSettings()
        self.setup_django()

    def print_logo(self):
        print("""
        ___           _             _
       /   \___   ___| | _____ _ __(_)_______
      / /\ / _ \ / __| |/ / _ \ '__| |_  / _ \\
     / /_// (_) | (__|   <  __/ |  | |/ /  __/
    /___,' \___/ \___|_|\_\___|_|  |_/___\___|
        """)

    def setup_paths(self):
        sys.path.append(os.getcwd())

    def setup_django(self):
        django_settings_path = getattr(self.args, 'djangosettings', None)
        if django_settings_path:
            os.environ.setdefault("DJANGO_SETTINGS_MODULE", django_settings_path)
            try:
                from django.conf import settings as django_settings
                self.django_available = True
                self.django_settings = django_settings
                self.django_settings_path = django_settings_path
                print("Using Django settings: ", end="", flush=True)
                print(color("{}\n".format(django_settings_path), Colors.OKGREEN))
            except ImportError as e:
                print(e)
                self.django_available = None
                self.django_settings = None
                self.django_settings_path = None
                pass

    def add_arguments(self, parser):
        parser.add_argument('--djangosettings', nargs="?", default=None)

    def _get_basedir(self):
        current_work_dir = os.getcwd()
        base_dir = os.getcwd()
        if self.django_available:
            base_dir = getattr(self.django_settings, 'BASE_DIR', None)
        if not base_dir:
            print(
                color('Could not find BASE_DIR in Django settings, some features might not be enabled.', Colors.WARNING)
            )
            base_dir = current_work_dir
        else:
            if not isinstance(base_dir, str):
                print(
                    color('The BASE_DIR variable must be a string, some features might not be enabled.', Colors.WARNING)
                )
                base_dir = current_work_dir

        print(
            color('Will be using {} for storing Docker files'.format(base_dir), Colors.HEADER)
        )
        return base_dir

    def _get_base_image(self):
        docker_image = ask(
            question='What docker image be based on?',
            default='ubuntu:16.04',
            validator=DockerImageValidator(),
            newline=False
        )
        print('Using docker image: {}'.format(color(docker_image, Colors.HEADER)))
        operating_system = docker_image.split(':')[0]

        return docker_image, operating_system

    def _get_database_image(self):
        database_type = get_database_type(self.django_settings)
        verbose_db_type = verbose_name_db_mapping.get(database_type)

        use_settings_db = False
        if database_type:
            use_settings_db_response = ask(
                question='Do you want to use {} as your database?'.format(verbose_db_type),
                default='Yes',
                choices=['Yes', 'No']
            )
            use_settings_db = use_settings_db_response == 'Yes'

        if not database_type or not use_settings_db:
            database_type = ask(
                question='What database are you using in production?',
                default='PostgreSQL',
                choices=verbose_name_db_mapping,
                newline=False
            )
            verbose_db_type = verbose_name_db_mapping.get(database_type)

        database_docker_image = self._get_docker_image_version(database_type, verbose_db_type)

        return database_docker_image, database_type

    def _get_cache_image(self):
        cache_type = get_cache_type(self.django_settings)
        verbose_cache_type = verbose_name_cache_mapping.get(cache_type)

        use_settings_cache = False
        if cache_type:
            use_settings_db_response = ask(
                question='Do you want to use {} as your database?'.format(verbose_cache_type),
                default='Yes',
                choices=['Yes', 'No']
            )
            use_settings_cache = use_settings_db_response == 'Yes'

        if not cache_type or not use_settings_cache:
            cache_choices = verbose_name_cache_mapping
            cache_choices[None] = 'None'  # TODO: Don't do this
            cache_type = ask(
                question='What cache are you using in production?',
                default='None',
                choices=cache_choices,
                newline=False
            )
            if cache_type is None:
                return None, None
            verbose_cache_type = verbose_name_cache_mapping.get(cache_type)

        cache_docker_image = self._get_docker_image_version(cache_type, verbose_cache_type)

        return cache_docker_image, cache_type

    def _get_docker_image_version(self, docker_image, verbose_name):
        client = DockerIndex()
        available_versions = client.get_latest_version_tags(docker_image)
        cache_version = ask(
            question='Which {} version do you want to use?'.format(verbose_name),
            choices=list(available_versions.keys()) + ['custom']
        )

        if cache_version == 'custom':
            cache_version = ask(
                question='Specify {} version'.format(verbose_name),
                validator=DockerImageVersionValidator(docker_image),
            )

        cache_image_flavor = False
        if len(available_versions.get(cache_version, [])) != 0:
            default_choices = 'alpine' if 'alpine' in available_versions[cache_version] else 'No'
            flavor_response = ask(
                question='Do you want to use a separate flavor?'.format(verbose_name),
                choices=available_versions[cache_version] + ['No'],
                default=default_choices,
            )
            cache_image_flavor = flavor_response if flavor_response != 'No' else False

        versioned_docker_image = "{}:{}".format(docker_image, cache_version)
        if cache_image_flavor:
            versioned_docker_image = "{}-{}".format(versioned_docker_image, cache_image_flavor)
        print('Using docker image: {}'.format(color(versioned_docker_image, Colors.HEADER)))

        return versioned_docker_image

    def _get_requirements_files(self, base_dir):
        print("\nChecking for requirements files... ", end="", flush=True)
        if not base_dir:
            print(color("skipping due to no base dir", Colors.WARNING))
            return None

        requirements_re = re.compile('requirements.*\.txt')
        root_files = os.listdir(base_dir)
        requirements_files = [root_file for root_file in root_files if requirements_re.match(root_file)]
        requirements_files_string = ', '.join(requirements_files)
        print("{}".format(color(requirements_files_string, Colors.HEADER)))
        return requirements_files

    def _get_python_version(self, supported_python_versions):
        if not supported_python_versions:
            print(
                color("Python is currently not supported by the docker image handler", Colors.WARNING)
            )
            return None
        supported_python_versions = sorted(supported_python_versions)

        version_info = sys.version_info
        running_python_version = "{}.{}".format(version_info[0], version_info[1])
        default_choice = running_python_version

        if running_python_version not in supported_python_versions:
            print(color(
                "Note that the version ({}) you are currently running is not supported by the Dockerize right now".format(
                    running_python_version),
                Colors.WARNING))

            default_choice = supported_python_versions[-1]

        return ask(
            question='Which version of Python is the project using?',
            default=default_choice,
            choices=supported_python_versions,
        )

    def _get_application_server(self):
        application_server_mapping = {
            'uwsgi': 'uWSGI',
            'gunicorn': 'Gunicorn'
        }

        return ask(
            question='Which application server is used in production?',
            default='uWSGI',
            choices=application_server_mapping,
        )

    def _get_wsgi_file(self, base_dir):
        search_dir = base_dir

        # Try to guess in which folder the WSGI file is in if Django is enabled
        if self.django_settings:
            search_dir += '/{}'.format(self.django_settings_path.split('.')[0])

        # Find all wsgi files
        wsgi_settings = find_filename('wsgi.py', search_dir)

        if not wsgi_settings:
            return wsgi_settings

        if len(wsgi_settings) > 1:
            # Handle multiple files
            return ask(
                question='More then one WSGI settings file detected, which should be used?',
                choices=wsgi_settings,
            )
        else:
            # Do not ask if we only found one file
            return wsgi_settings[0]

    def _get_relative_dotted_path(self, path, relative_to_path):
        # Get path relative to the root of the project
        relative_path = Path(path).relative_to(relative_to_path)

        # Create module path
        return str(relative_path).replace('/', '.').replace('.py', '')

    def handle(self, *args, **options):
        config = DockerizeConfig()
        config.base_dir = self._get_basedir()

        config.base_image, config.operating_system = self._get_base_image()

        if config.operating_system not in list(OS_IMAGE_HANDLERS.keys()):
            print(
                color("Sorry, 'dockerize' does not currently support '{}' as a base OS".format(config.operating_system),
                      Colors.FAIL))
            sys.exit(1)
        os_image_handler = OS_IMAGE_HANDLERS[config.operating_system](config)

        config.python_version = self._get_python_version(os_image_handler.supported_python_versions)

        config.database_image, config.database_type = self._get_database_image()

        config.cache_image, config.cache_type = self._get_cache_image()

        config.requirement_files = self._get_requirements_files(config.base_dir)

        config.wsgi_path = self._get_wsgi_file(config.base_dir)
        config.wsgi_dot_path = self._get_relative_dotted_path(config.wsgi_path, config.base_dir)
        config.application_server = self._get_application_server()

        print(color("\nSetting up docker environment", Colors.OKGREEN))
        print(color("--------------------------------\n", Colors.OKGREEN))

        os_image_handler(config).handle()
        EntrypointHandler(config).handle()
        ComposeHandler(config).handle()


if __name__ == "__main__":
    cli.run_command(Dockerize)
