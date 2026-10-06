import os


def get_version():
    return os.getenv('APP_VERSION') or 'v0.0.0-dev'


if __name__ == '__main__':
    print(get_version())
