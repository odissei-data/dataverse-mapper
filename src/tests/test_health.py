import asyncio

from main import app, health
from version import get_image, get_version


def test_health():
    assert "/health" in {route.path for route in app.routes}
    assert asyncio.run(health()) == {
        "status": "ok", "version": get_version(), "image": get_image()}
