DATABASE_DEFAULT_CREDENTIALS = {
    'username': 'root',
    'password': 'root',
}

DATABASE_ENV_VARS = {
    "mysql": {
        "MYSQL_ROOT_PASSWORD": DATABASE_DEFAULT_CREDENTIALS['password'],
        "MYSQL_DATABASE": "application",
        "MYSQL_ROOT_HOST": "172.17.%.% # Allow all hosts in the default docker subnet to connect",
    },
    "postgres": {
        "POSTGRES_USER": DATABASE_DEFAULT_CREDENTIALS['username'],
        "POSTGRES_PASSWORD": DATABASE_DEFAULT_CREDENTIALS['password'],
        "POSTGRES_DB": "application",
    }
}

DATABASE_DEFAULT_PORT = {
    "mysql": "3306",
    "postgres": "5432",
}

CACHE_DEFAULT_PORT = {
    "redis": "6379",
    "memcached": "11211",
}

DATABASE_VOLUME_PATH = {
    "mysql": "/var/lib/mysql",
    "postgres": "/var/lib/postgresql",
}
