import json
import pytest
from fastapi import HTTPException
from ..mapper import MetadataMapper


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


def test_cbs_data():
    metadata = open_json_file("test-data/input-data/cbs-test-metadata.json")
    mapping = open_json_file("test-data/mappings/cbs-mapping.json")
    template = open_json_file(
        "test-data/template-data/cbs_dataverse_template.json"
    )
    MetadataMapper(metadata, template, mapping)

    assert 1 == 1
