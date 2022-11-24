import json
import pytest
from fastapi import HTTPException
from ..mapper import MetadataMapper


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


@pytest.fixture()
def cbs_metadata():
    return open_json_file("test-data/input-data/cbs-test-metadata.json")


@pytest.fixture()
def cbs_mapping():
    return open_json_file("test-data/mappings/cbs-mapping.json")


@pytest.fixture()
def cbs_template():
    return open_json_file(
        "test-data/template-data/cbs_dataverse_template.json")


@pytest.fixture()
def cbs_result():
    return open_json_file("test-data/expected-result-data/cbs-result.json")


@pytest.fixture()
def easy_metadata():
    return open_json_file("test-data/input-data/easy-test-metadata.json")


@pytest.fixture()
def easy_mapping():
    return open_json_file("test-data/mappings/easy-mapping.json")


@pytest.fixture()
def easy_template():
    return open_json_file(
        "test-data/template-data/easy_dataverse_template.json")


@pytest.fixture()
def easy_result():
    return open_json_file("test-data/expected-result-data/easy-result.json")


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
def easy_mapper(easy_metadata, easy_template, easy_mapping):
    return MetadataMapper(easy_metadata, easy_template, easy_mapping)


@pytest.fixture()
def simple_test_mapper(simple_test_input_metadata, simple_test_template,
                       simple_test_mapping):
    return MetadataMapper(simple_test_input_metadata, simple_test_template,
                          simple_test_mapping)


def test_cbs_mapper(cbs_mapper, cbs_result):
    mapped_result = cbs_mapper.map_metadata()
    test_output_filename = "test-data/test-output/cbs-test-output.json"
    with open(test_output_filename, 'w') as outfile:
        json.dump(mapped_result, outfile)
    assert mapped_result == cbs_result


def test_easy_mapper(easy_mapper, easy_result):
    mapped_result = easy_mapper.map_metadata()
    test_output_filename = "test-data/test-output/easy-test-output.json"
    with open(test_output_filename, 'w') as outfile:
        json.dump(mapped_result, outfile)
    assert mapped_result == easy_result


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
    assert default_value_object in mapped_result["datasetVersion"][
        "metadataBlocks"]["citation"]["fields"]


def test_map_single_object_compound_object(simple_test_mapper):
    expected_compound = {
        "firstObject": {
            "typeName": "firstObject",
            "multiple": False,
            "typeClass": "primitive",
            "value": "default"
        },
        "secondObject": {
            "typeName": "secondObject",
            "multiple": False,
            "typeClass": "primitive",
            "value": "deeply_nested_value"
        }
    }

    fields = simple_test_mapper.template["datasetVersion"]["metadataBlocks"][
        "citation"]["fields"]
    compound_single_object = next((field for field in fields if field.get(
        "typeName") == "compoundSingleObject"), None)
    map_value_result = simple_test_mapper.map_compound_field(
        compound_single_object)
    assert expected_compound == map_value_result


def test_map_multiple_objects_compound_object(simple_test_mapper):
    expected_compound = [
        {
            'firstMultipleObject':
                {
                    'multiple': False,
                    'typeClass': 'primitive',
                    'typeName': 'firstMultipleObject',
                    'value': 'multiple_value_1'
                },
            'secondMultipleObject':
                {
                    'multiple': False,
                    'typeClass': 'primitive',
                    'typeName': 'secondMultipleObject',
                    'value': 'deeply_nested_value'
                }
        },
        {
            'firstMultipleObject':
                {
                    'multiple': False,
                    'typeClass': 'primitive',
                    'typeName': 'firstMultipleObject',
                    'value': 'multiple_value_2'
                }
        },
        {
            'firstMultipleObject':
                {
                    'multiple': False,
                    'typeClass': 'primitive',
                    'typeName': 'firstMultipleObject',
                    'value': 'multiple_value_3'
                }
        }
    ]
    fields = simple_test_mapper.template["datasetVersion"]["metadataBlocks"][
        "citation"]["fields"]
    compound_multiple_objects = next((field for field in fields if field.get(
        "typeName") == "compoundMultipleObject"), None)

    map_value_result = simple_test_mapper.map_compound_multiple_field(
        compound_multiple_objects)

    assert expected_compound == map_value_result


# Mapped pid is formatted as https://doi.org/10.17026/dans-xnh-wt5n
def test_easy_persistent_identifier_mapping(easy_mapper):
    expected_pid = 'doi:10.17026/dans-xnh-wt5n'
    mapped_pid = easy_mapper.get_persistent_identifier()
    assert mapped_pid == expected_pid


# Mapped pid is formatted as doi:10.5072/FK2/APTZLV
def test_persistent_identifier_mapping(simple_test_mapper):
    expected_pid = 'doi:10.5072/FK2/APTZLV'
    mapped_pid = simple_test_mapper.get_persistent_identifier()
    assert mapped_pid == expected_pid


def test_nonexistent_persistent_identifier_mapping(cbs_mapper):
    with pytest.raises(HTTPException):
        cbs_mapper.get_persistent_identifier()

