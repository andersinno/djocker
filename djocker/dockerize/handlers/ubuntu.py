import os

from djocker.dockerize.handlers.base import (
    BaseHandler, HandlerException
)

apt_package_requirements = {
    'mysqlclient': ['libmysqlclient-dev'],
    'cffi': ['libffi-dev'],
    'pyopenssl': ['libssl-dev'],
    'pysaml2': ['xmlsec1', 'libxmlsec1']
}

supported_ubuntu_versions = [
    '16.04',
]

python_version_support = {
    '16.04': {
        '2.7': {
            'default': True,
            'packages': ['python-dev', 'python-pip'],
            'interpreter': 'python',
            'pip': 'pip',
        },
        '3.4': {
            'default': False,
            'deb_sources': [
                'deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu xenial main',
                'deb-src http://ppa.launchpad.net/deadsnakes/ppa/ubuntu xenial main',
            ],
            'deb_sign_keys': ['F23C5A6CF475977595C89F51BA6932366A755776'],
            'packages': ['python3.4'],
            'interpreter': 'python3.4',
            'pip': 'pip',
        },
        '3.5': {
            'default': False,
            'packages': ['python3.5', 'python3-dev', 'python3-pip'],
            'interpreter': 'python3.5',
            'pip': 'pip',
        },
        '3.6': {
            'default': False,
            'deb_sources': [
                'deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu xenial main',
                'deb-src http://ppa.launchpad.net/deadsnakes/ppa/ubuntu xenial main',
            ],
            'deb_sign_keys': ['F23C5A6CF475977595C89F51BA6932366A755776'],
            'packages': ['python3.6'],
            'interpreter': 'python3.6',
            'pip': 'pip',
        }
    },
}


class UbuntuHandler(BaseHandler):
    template_file = 'ubuntu/Dockerfile.j2'
    out_file = 'Dockerfile'

    @property
    def ubuntu_version(self):
        return self.config.base_image.split(':')[1].split('-')[0]

    @property
    def python_info(self):
        return python_version_support[self.ubuntu_version][self.config.python_version]

    def _validate(self):
        ubuntu_version = self.ubuntu_version
        if ubuntu_version not in supported_ubuntu_versions:
            raise HandlerException('Version {} for Ubuntu is not currently supported'.format(ubuntu_version))

        if self.config.python_version not in python_version_support[ubuntu_version]:
            raise HandlerException('Version {} of Python is currently not supported by Ubuntu {}'
                                   .format(self.config.python_version, ubuntu_version))

    def _get_apt_data(self):
        if not self.config.requirement_files:
            return None

        apt_requirements = ['build-essential',
                            'locales',
                            'netcat',  # For checking if a network service is up or not
                            ]
        base_dir = self.config.base_dir

        # Get apt package requirements from requirements files
        for requirements_file in self.config.requirement_files:
            requirement_path = os.path.join(base_dir, requirements_file)
            with open(requirement_path, 'r') as file:
                requirements_content = file.read()
                for package, requirements in apt_package_requirements.items():
                    if package in requirements_content:
                        apt_requirements += requirements

        # Get python requirement
        python_info = self.python_info

        apt_requirements += python_info.get('packages', [])

        deb_sources = python_info.get('deb_sources', [])
        deb_sign_keys = python_info.get('deb_sign_keys', [])

        apt_data = {
            'requirements': apt_requirements,
            'sources': deb_sources,
            'deb_keys': deb_sign_keys,
        }
        return apt_data

    def handle(self):
        self._validate()

        data = {
            'base_image': self.config.base_image,
            'apt_data': self._get_apt_data(),
            'python': self.python_info,
            'requirement_files': self.config.requirement_files,
            'wsgi_dot_path': self.config.wsgi_dot_path,
            'application_server': self.config.application_server
        }

        self.write_template(data)
