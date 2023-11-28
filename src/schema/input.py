from typing import Any

from pydantic import BaseModel


class Input(BaseModel):
    metadata: list | dict | Any
    template: list | dict | Any
    mapping: list | dict | Any

