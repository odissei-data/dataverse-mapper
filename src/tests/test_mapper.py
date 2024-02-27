import json
import pytest
from ..mapper import MetadataMapper


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


def _create_mapper(
        metadata_path, mapping_path, template_path
):
    """
    Returns mapper for the test.

    :param metadata_path: str, path to file
    :param mapping_path: str, path to file
    :param template_path: str, path to file
    """
    metadata = open_json_file(metadata_path)
    mapping = open_json_file(mapping_path)
    template = open_json_file(template_path)

    mapper = MetadataMapper(metadata, template, mapping)
    return mapper


def test_liss_json_mapper():
    """Test LISS JSON metadata mapping."""
    mapper_child = _create_mapper(
        "test-data/input-data/liss-child-metadata.json",
        "resources/mappings/liss-mapping.json",
        "resources/templates/liss_dataverse_template.json"
    )
    mapper_parent = _create_mapper(
        "test-data/input-data/liss-parent-metadata.json",
        "resources/mappings/liss-mapping.json",
        "resources/templates/liss_dataverse_template.json"
    )

    mapped_child_result = mapper_child.map_metadata()
    mapped_parent_result = mapper_parent.map_metadata()

    expected_child_result = open_json_file(
        "test-data/expected-result-data/liss-child-result.json"
    )

    expected_parent_result = open_json_file(
        "test-data/expected-result-data/liss-parent-result.json")

    assert mapped_child_result == expected_child_result
    assert mapped_parent_result == expected_parent_result


def test_cbs_mapper():
    """Test CBS mapping."""
    mapper = _create_mapper(
        "test-data/input-data/cbs-test-metadata.json",
        "resources/mappings/cbs-mapping.json",
        "resources/templates/cbs_dataverse_template.json"
    )

    # Test if the mapper generates the expected result
    expected_result = open_json_file(
        "test-data/expected-result-data/cbs-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result


def test_cid_mapper():
    """Test CBS mapping."""
    mapper = _create_mapper(
        "test-data/input-data/cid-test-metadata.json",
        "resources/mappings/cid-mapping.json",
        "resources/templates/cid_dataverse_template.json"
    )

    # Test if the mapper generates the expected result
    expected_result = open_json_file(
        "test-data/expected-result-data/cid-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result

    # Test if the mapper cleans empty fields correctly
    expected_clean_result = open_json_file(
        "test-data/expected-result-data/cid-clean-result.json"
    )
    mapper.remove_empty_fields()
    assert mapper.template == expected_clean_result

    # Test cleaner with different data

    mapped_result = open_json_file(
        "test-data/expected-result-data/cid-result-2.json"
    )
    expected_clean_result = open_json_file(
        "test-data/expected-result-data/cid-clean-result-2.json"
    )
    mapper.template = mapped_result
    mapper.remove_empty_fields()
    assert mapper.template == expected_clean_result


def test_easy_mapper():
    """Test Easy mapping."""
    mapper = _create_mapper(
        "test-data/input-data/easy-test-metadata.json",
        "test-data/test-mappings/easy-mapping.json",
        "test-data/test-templates/easy_dataverse_template.json"
    )

    expected_result = open_json_file(
        "test-data/expected-result-data/easy-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result

    # Test if the mapper cleans empty fields correctly
    expected_clean_result = open_json_file(
        "test-data/expected-result-data/easy-clean-result.json"
    )
    mapper.remove_empty_fields()
    assert mapper.template == expected_clean_result


def test_ssh_mapper():
    """Test SSH mapping."""
    mapper = _create_mapper(
        "test-data/input-data/ssh-test-metadata.json",
        "resources/mappings/ssh-mapping.json",
        "resources/templates/ssh_dataverse_template.json"
    )

    expected_clean_result = open_json_file(
        "test-data/expected-result-data/ssh-clean-result.json"
    )
    mapper.map_metadata()
    mapper.remove_empty_fields()
    assert mapper.template == expected_clean_result


def test_liss_mapper():
    """Test Liss mapping."""
    mapper = _create_mapper(
        "test-data/input-data/liss-test-metadata.json",
        "test-data/test-mappings/liss-old-mapping.json",
        "test-data/test-templates/liss_old_dataverse_template.json"
    )

    expected_result = open_json_file(
        "test-data/expected-result-data/liss-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result


@pytest.fixture()
def simple_test_mapper():
    mapper = _create_mapper(
        "test-data/input-data/simple-test-input-metadata.json",
        "test-data/test-mappings/simple-test-mapping.json",
        "test-data/test-templates/simple-test-template.json",
    )
    return mapper


def test_simple_mapper(simple_test_mapper):
    """Test retrival of data."""
    # Test single value mapping
    map_value_result = simple_test_mapper.map_value("singleValue")
    assert map_value_result == [
        "single_value"
    ]

    # Test multi value mapping
    map_value_result = simple_test_mapper.map_value("multipleValues")
    assert map_value_result == [
        "multiple_value_1",
        "multiple_value_2",
        "multiple_value_3"
    ]

    # Test deeply nested value mapping
    map_value_result = simple_test_mapper.map_value("deeplyNestedValue")
    assert map_value_result == [
        "deeply_nested_value"
    ]


def test_default_value_guard_clause(simple_test_mapper):
    """Test default value guard."""
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


def test_map_object_onto_compound_multiple_objects_with_missing_values():
    mapper = _create_mapper(
        "test-data/input-data/object-compound-test-metadata.json",
        "resources/mappings/cbs-mapping.json",
        "test-data/test-templates/object-compound-template.json"
    )

    variable_compound = mapper.template['datasetVersion']['metadataBlocks'][
        'variableInformation']['fields'][0]

    expected_result = [
        {
            "odisseiVariableName": {
                "typeName": "odisseiVariableName",
                "typeClass": "primitive",
                "multiple": False,
                "value": "Variable1"},
            "odisseiVariableLabel": {
                "typeName": "odisseiVariableLabel",
                "typeClass": "primitive",
                "multiple": False,
                "value": "Label1"},
            "odisseiConceptVariableDefinition": {
                "typeName": "odisseiConceptVariableDefinition",
                "typeClass": "primitive",
                "multiple": False,
                "value": "Definition1"},
            "odisseiConceptVariableValidFrom": {
                "typeName": "odisseiConceptVariableValidFrom",
                "typeClass": "primitive",
                "multiple": False,
                "value": ""}
        },
        {
            "odisseiVariableName": {
                "typeName": "odisseiVariableName",
                "typeClass": "primitive",
                "multiple": False,
                "value": "Variable2"},
            "odisseiVariableLabel": {
                "typeName": "odisseiVariableLabel",
                "typeClass": "primitive",
                "multiple": False,
                "value": "Label2"},
            "odisseiConceptVariableDefinition": {
                "typeName": "odisseiConceptVariableDefinition",
                "typeClass": "primitive",
                "multiple": False,
                "value": "Definition2"},
            "odisseiConceptVariableValidFrom": {
                "typeName": "odisseiConceptVariableValidFrom",
                "typeClass": "primitive",
                "multiple": False,
                "value": "2023-01-01"}
        }
    ]

    result = mapper.map_object_onto_compound(variable_compound)
    assert result == expected_result
