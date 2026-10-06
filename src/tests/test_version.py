from version import get_image, get_version


def test_version_comes_from_the_build(monkeypatch):
    monkeypatch.setenv("APP_VERSION", "v1.2.3")
    assert get_version() == "v1.2.3"


def test_version_without_a_build(monkeypatch):
    monkeypatch.delenv("APP_VERSION", raising=False)
    assert get_version() == "v0.0.0-dev"
    monkeypatch.setenv("APP_VERSION", "")
    assert get_version() == "v0.0.0-dev"


def test_image_comes_from_the_build(monkeypatch):
    monkeypatch.setenv("APP_IMAGE", "ghcr.io/odissei-data/example")
    monkeypatch.setenv("APP_VERSION", "v1.2.3")
    assert get_image() == "ghcr.io/odissei-data/example:v1.2.3"


def test_no_image_without_a_build(monkeypatch):
    monkeypatch.delenv("APP_IMAGE", raising=False)
    assert get_image() is None
