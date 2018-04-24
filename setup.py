import setuptools

if __name__ == '__main__':
    setuptools.setup(
        setup_requires=['setuptools>=34.0'],
        scripts=['djocker/bin/manage_with_compose.py',
                 'djocker/bin/dockerize.py'],
    )
