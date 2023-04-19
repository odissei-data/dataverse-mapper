import json
import pytest
from fastapi import HTTPException
from ..mapper import MetadataMapper


def open_json_file(json_path):
    with open(json_path) as f:
        return json.load(f)


def create_mapper(
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


def test_cbs_mapper():
    """Test CBS mapping."""
    mapper = create_mapper(
        "test-data/input-data/cbs-test-metadata.json",
        "test-data/mappings/cbs-mapping.json",
        "test-data/template-data/cbs_dataverse_template.json"
    )

    # Test if the mapper generates the expected result
    expected_result = open_json_file(
        "test-data/expected-result-data/cbs-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result


def test_easy_mapper():
    """Test Easy mapping."""
    mapper = create_mapper(
        "test-data/input-data/easy-test-metadata.json",
        "test-data/mappings/easy-mapping.json",
        "test-data/template-data/easy_dataverse_template.json"
    )

    expected_result = open_json_file(
        "test-data/expected-result-data/easy-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result

    # Test if the mapper assigned the PID correctly
    expected_pid = 'doi:10.17026/dans-xnh-wt5n'
    mapped_pid = mapper.get_persistent_identifier()
    assert mapped_pid == expected_pid


def test_liss_mapper():
    """Test Liss mapping."""
    mapper = create_mapper(
        "test-data/input-data/liss-test-metadata.json",
        "test-data/mappings/liss-mapping.json",
        "test-data/template-data/liss_dataverse_template.json"
    )

    expected_result = open_json_file(
        "test-data/expected-result-data/liss-result.json"
    )
    mapped_result = mapper.map_metadata()
    assert mapped_result == expected_result


# def test_simple_mapper():
#     """A"""
#     mapped_result = create_mapped_result(
#         "test-data/input-data/simple-test-input-metadata.json",
#         "test-data/mappings/simple-test-mapping.json",
#         "test-data/template-data/simple-test-template.json",
#
#     )
#
#     expected_result = open_json_file(
#         "test-data/expected-result-data/simple-result.json"
#     )
#     assert mapped_result == expected_result

