import copy
from typing import Any
from fastapi import HTTPException

import utils


class MetadataMapper:
    """ A class used to map the input metadata to the Dataverse JSON template

    The MetadataMapper fills out the Dataverse JSON template using the mapping
    to retrieve the corresponding values from the input metadata.

    Attributes
    ----------
    metadata:
        The input metadata represented as a JSON object.
    template:
        JSON template that uses the format the Dataverse Native API expects
        when importing metadata. Every field is a dictionary of values:
            typeName  - the name of the field.
            typeClass - determines what the value can be, options are:
                        primitive/controlledVocabulary (a single value or list)
                        compound (the value contains one or more nested fields)
            multiple  - a boolean that states if the value is a list or not
            value     - the actual value of the field
    mapping:
        A dictionary that has the typeName of a field in the template as a key,
        and a list of paths to corresponding values in the input metadata
        as the value. For example: "title": "path/to/the/value/in/metadata".
    """

    def __init__(self, metadata: list | dict | Any,
                 template: list | dict | Any,
                 mapping: list | dict | Any):
        self.metadata = metadata
        self.mapping = utils.clean_mapping(mapping)
        self.template = template

    def map_metadata(self):
        """ Maps the values in the metadata on to the template

        The map_metadata method loops over the fields in the Dataverse JSON
        template. For every field in the template it determines the type and
        maps the value accordingly.

        :return: the template with the mapped values.
        """
        metadata_blocks = self.template["datasetVersion"]["metadataBlocks"]
        for template_fields in metadata_blocks.values():
            for field in template_fields["fields"]:
                # guard clause for singular default values
                if field['value'] and field['typeClass'] != 'compound' and \
                        not field['multiple']:
                    continue
                elif field['typeClass'] == 'compound':
                    self.map_compound(field)
                # guard clause to skip unmappable primitives
                elif not self.map_value(field['typeName']):
                    continue
                elif field['multiple']:
                    field['value'].extend(self.map_value(field['typeName']))
                else:
                    field['value'] = self.map_value(field['typeName'])[0]
        return self.template

    def map_value(self, type_name: str, mapping: dict = None,
                  metadata: dict = None):
        """ Retrieves all values from the metadata for a field in the template.

        map_value creates a list of values retrieved from the input metadata.
        It uses the list of paths given by the mapping given by the field's
        name. The retrieved value is handled depending on if it is a list
        or single object.
        :param mapping: The mapping from the source value to template field.
        :param metadata: The source metadata which contains the source value.
        :param type_name: the name of the field in the template.
        :return: a list of values belonging to the given field in the template.
        """

        if mapping is None:
            mapping = self.mapping

        if metadata is None:
            metadata = self.metadata

        if type_name not in mapping:
            return []

        mapped_values = []
        for path in mapping[type_name]:
            mapped_value = utils.drill_down(metadata, path)
            if not mapped_value:
                continue
            if isinstance(mapped_value, list):
                mapped_values.extend(mapped_value)
            else:
                mapped_values.append(mapped_value)
        return mapped_values

    def map_compound(self, field: dict):
        if not field['multiple']:
            field['value'] = self.map_compound_field(field)
        elif field['typeName'] in self.mapping:
            field['value'] = self.map_object_onto_compound(field)
        else:
            field['value'] = self.map_compound_multiple_field(field)

    def map_object_onto_compound(self, field: dict):
        compound_mapping = self.mapping[field['typeName']]
        compound_objects = utils.drill_down(
            self.metadata,
            compound_mapping['mapping']
        )
        child_mappings = compound_mapping['children']
        result_dict_list = []
        for compound_object in compound_objects:
            # Make a copy of the template object to use for mapping to.
            compound_template_children = copy.deepcopy(field['value'][0])
            for _, child in compound_template_children.items():
                type_name = child['typeName']
                mapped_values = self.map_value(type_name, child_mappings,
                                               compound_object)
                self.set_child_value(child, mapped_values)
            dict_copy = copy.deepcopy(compound_template_children)
            result_dict_list.append(dict_copy)
        return result_dict_list

    def set_child_value(self, child, mapped_values):
        if child['multiple']:
            child['value'].extend(mapped_values)
        elif mapped_values:
            child['value'] = mapped_values[0]

    def map_compound_field(self, compound_template_field: dict):
        """ Maps compound field where only a single nested object is expected.

        A compound field that is not a multiple will have a single dictionary
        as the value. For every nested field we find the first value in the
        metadata using the mapping. Those fields are then joined in the
        result_dict.

        This method checks and adds default values to the compound.
        It also checks if the mapped value exists before adding it as a value.

        :param compound_template_field: the field containing the nested fields.
        :return: a dictionary containing the nested fields with mapped values.
        """
        result_dict = {}
        for k, v in compound_template_field['value'].items():
            if v['value']:
                result_dict[k] = v
                continue
            mapped_value = self.map_value(v['typeName'])
            if mapped_value:
                v['value'] = mapped_value[0]
                result_dict[k] = v
        return result_dict

    def map_compound_multiple_field(self, compound_template_field: dict):
        """ Maps compound field where the value of the field can have a list of
        dictionaries that contain nested fields.

        First this method creates a dictionary of lists of values.
        This contains all the values per possible nested field.

        This list dictionary is used to create the result dictionary list.
        This list contains all dictionaries with sets of nested fields.

        TODO: Handle empty nested field values by removing them.
        :param compound_template_field: a compound field from the template.
        :return: a list of dictionaries with sets of nested fields.
        """
        compound_dict = compound_template_field['value'][0]
        list_dict = self.create_mapped_value_list_dict(compound_dict)
        template_dict_copy = copy.deepcopy(compound_dict)
        result_dict_list = self.create_result_dict_list(list_dict,
                                                        template_dict_copy)
        return result_dict_list

    def create_mapped_value_list_dict(self, compound_dict: dict):
        """ Creates a dictionary to use for filling the nested fields.

        Loops through all nested fields in the compound. For a field name
        it finds all values in the metadata and places them in to a list.
        If there is already a default value in place, the value is added to the
        list.

        :param compound_dict: The nested fields for mapping values to.
        :return: a dictionary where the key is the name of a nested field
        and the value is a list of all values belonging to that nested field.
        """
        list_dict = {}
        for k, v in compound_dict.items():
            list_dict[k] = []
            if v['value']:
                list_dict[k].append(v['value'])
                continue
            mapped_value = self.map_value(v['typeName'])
            if mapped_value:
                list_dict[k].extend(mapped_value)
        return list_dict

    @staticmethod
    def create_result_dict_list(list_dict: dict, template_dict):
        """ Creates the nested field dictionaries to be used as the compound
        field value.

        TODO: Merging the dicts could made to be more efficient.
        :param list_dict: a dictionary where the key is the name of a nested field
        and the value is a list of all values belonging to that nested field.
        :param template_dict: The nested fields for mapping values to.
        :return:
        """
        result_dict_list = []
        longest_list_length = max(len(item) for item in list_dict.values())
        for index in range(longest_list_length):
            result_dict = {}
            for k, v in list_dict.items():
                if 0 <= index < len(v):
                    template_dict[k]['value'] = v[index]
                    result_dict[k] = template_dict[k]
            dict_copy = copy.deepcopy(result_dict)
            result_dict_list.append(dict_copy)
        return result_dict_list

    def get_persistent_identifier(self):
        """ Maps the dataset's doi to a specific field in the template.

        TODO: Needs exception handling
        Uses a mapping to retrieve the dataset's doi from the metadata.
        Because there can be multiple persistent identifier, this method checks
        if the id is an actual doi. It also formats the doi to the expected
        format if needed.
        """
        persistent_ids = self.map_value("datasetPersistentId")
        for pid in persistent_ids:
            if "https://doi.org/" in pid:
                doi = 'doi:' + pid.split("/", 3)[3]
                return doi
            elif "doi:" in pid:
                return pid
        raise HTTPException(
            status_code=422,
            detail="No usable DOI in mapped persistent identifiers"
        )
