import os


def get_version():
    return os.getenv('APP_VERSION') or 'v0.0.0-dev'


def get_image():
    """The image name baked in at build time (APP_IMAGE), with the version."""
    image = os.getenv('APP_IMAGE')
    return f'{image}:{get_version()}' if image else None


if __name__ == '__main__':
    print(get_version())
