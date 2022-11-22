import json

import pytest
from ..mapper import MetadataMapper


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


@pytest.fixture()
def cbs_metadata():
    return open_json_file("test-data/input-data/cbs-filtered-true.json")


@pytest.fixture()
def cbs_mapping():
    return open_json_file("test-data/mappings/cbs-mapping.json")


@pytest.fixture()
def cbs_template():
    return open_json_file(
        "test-data/template-data/cbs_dataverse_template.json")


@pytest.fixture()
def cbs_result():
    return open_json_file("test-data/result-data/cbs-result.json")


@pytest.fixture()
def simple_test_input_metadata():
    return open_json_file(
        "test-data/input-data/simple-test-input-metadata.json")


@pytest.fixture()
def simple_test_mapping():
    return open_json_file("test-data/mappings/simple-test-mapping.json")


@pytest.fixture()
def simple_test_template():
    return open_json_file(
        "test-data/template-data/simple-test-template.json")


@pytest.fixture()
def cbs_mapper(cbs_metadata, cbs_template, cbs_mapping):
    return MetadataMapper(cbs_metadata, cbs_template, cbs_mapping)


@pytest.fixture()
def simple_test_mapper(simple_test_input_metadata, simple_test_template,
                       simple_test_mapping):
    return MetadataMapper(simple_test_input_metadata, simple_test_template,
                          simple_test_mapping)


def test_cbs_mapper(cbs_mapper, cbs_result):
    mapped_result = cbs_mapper.map_metadata()
    test_output_filename = "test-data/test-output/test_output.json"
    with open(test_output_filename, 'w') as outfile:
        json.dump(mapped_result, outfile)
    assert mapped_result == cbs_result


def test_map_value_single_value(simple_test_mapper):
    map_value_result = simple_test_mapper.map_value("singleValue")
    assert map_value_result == [
        "single_value"
    ]


def test_map_value_multiple_values(simple_test_mapper):
    map_value_result = simple_test_mapper.map_value("multipleValues")
    assert map_value_result == [
        "multiple_value_1",
        "multiple_value_2",
        "multiple_value_3"
    ]


def test_map_value_deeply_nested_value(simple_test_mapper):
    map_value_result = simple_test_mapper.map_value("deeplyNestedValue")
    assert map_value_result == [
        "deeply_nested_value"
    ]


def test_default_value_guard_clause(simple_test_mapper):
    mapped_result = simple_test_mapper.map_metadata()
    default_value_object = {
        "typeName": "defaultPrimitiveValue",
        "multiple": False,
        "typeClass": "primitive",
        "value": "default_value"
    }
    assert default_value_object in mapped_result["datasetVersion"]["metadataBlocks"]["citation"][
        "fields"]
