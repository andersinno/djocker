#!/usr/bin/env python
import sys

import py
from os import path
import django
from django.conf import settings

module_root = path.dirname(path.realpath(__file__))
sys.path.insert(0, path.join(module_root, 'tests'))

# Give feedback on used versions
sys.stderr.write('Using Python version {0} from {1}\n'.format(sys.version[:5], sys.executable))
sys.stderr.write('Using Django version {0} from {1}\n'.format(
    django.get_version(),
    path.dirname(path.abspath(django.__file__)))
)

if not settings.configured:

    template_settings = dict(
        TEMPLATES=[
            {
                'BACKEND': 'django.template.backends.django.DjangoTemplates',
                'DIRS': [],
                'APP_DIRS': True,
                'OPTIONS': {
                    'context_processors': [
                        'django.template.context_processors.debug',
                        'django.template.context_processors.request',
                        'django.contrib.auth.context_processors.auth',
                        'django.contrib.messages.context_processors.messages',
                    ],
                },
            },
        ]
    )

    MIDDLEWARE = [
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
    ]

    settings.configure(
        BASE_DIR=module_root,
        DEBUG=False,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:'
            }
        },
        INSTALLED_APPS=(
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.admin',
            'django.contrib.sessions',
            'djocker',
            'testapp'
        ),
        MIDDLEWARE_CLASSES=MIDDLEWARE,
        MIDDLEWARE=MIDDLEWARE,
        ROOT_URLCONF=[],
        **template_settings
    )

DEFAULT_TEST_APPS = [
    'tests',
]


def runtests():
    other_args = list(filter(lambda arg: arg.startswith('-'), sys.argv[1:]))
    test_apps = list(filter(lambda arg: not arg.startswith('-'), sys.argv[1:])) or DEFAULT_TEST_APPS

    argv = sys.argv[:1] + other_args
    argv += test_apps
    sys.exit(py.test.cmdline.main(argv))


if __name__ == '__main__':
    runtests()
