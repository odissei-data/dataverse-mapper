from typing import Any

from pydantic import BaseModel


class JSONInput(BaseModel):
    metadata: list | dict | Any
    template: list | dict | Any
    mapping: list | dict | Any

