import copy
from typing import Any


def drill_down(obj, path: list[str]):
    """ Drills down to a value in the metadata hierarchy using a path.

    Recursively goes through the metadata, using the keys in path list to
    descent to the value at the end of the path.

    TODO: Deal with path finding a list before it reaches the final key
    :param obj: the object, can be nested or not depending on how far down
                We've drilled.
    :param path: A list containing the keys of the path through the object.
    :return: The value or list of values retrieved at the end of the path.
    """

    if len(path) == 1:
        # if path has a single element, return that key of the dict
        if isinstance(obj, list):
            value_list = []
            for value in obj:
                if value.get(path[0]) is None:
                    continue
                value_list.append(value[path[0]])
            return value_list
        else:
            return obj[path[0]]
    else:
        if obj.get(path[0]) is None:
            return None
        # Take the key given by the first element of path and drill down.
        return drill_down(obj[path[0]], path[1:])


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
        self.mapping = mapping
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
                if field['value'] and field['typeClass'] != 'compound':
                    continue
                if field['typeClass'] == 'compound' and field['multiple']:
                    field['value'] = self.map_compound_multiple_field(field)
                elif field['typeClass'] == 'compound' and not field[
                    'multiple']:
                    field['value'] = self.map_compound_field(field)
                elif field['multiple']:
                    field['value'] = self.map_value(field['typeName'])
                else:
                    field['value'] = self.map_value(field['typeName'])[0]
        return self.template

    def map_value(self, type_name: str):
        """ Retrieves all values from the metadata for a field in the template.

        map_value creates a list of values retrieved from the input metadata.
        It uses the list of paths given by the mapping given by the field's
        name. The retrieved value is handled depending on if it is a list
        or single object.
        :param type_name: the name of the field in the template.
        :return: a list of values belonging to the given field in the template.
        """
        if type_name not in self.mapping:
            return None
        value_list = []
        for path in self.mapping[type_name]:
            split_path = path.split('/')
            value = drill_down(self.metadata, split_path)
            if isinstance(value, list):
                value_list.extend(value)
            else:
                value_list.append(value)
        return value_list

    def map_compound_field(self, compound_template_field: dict):
        """ Maps compound field where only a single nested object is expected.

        A compound field that is not a multiple will have a single dictionary
        as the value. For every nested field we find the first value in the
        metadata using the mapping. Those fields are then joined in the
        result_dict.

        :param compound_template_field: the field containing the nested fields.
        :return: a dictionary containing the nested fields with mapped values.
        """
        result_dict = {}
        for k, v in compound_template_field.items():
            mapped_value = self.map_value(v['typeName'])
            if isinstance(mapped_value, list):
                v['value'] = mapped_value[0]
            else:
                v['value'] = mapped_value
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
        template_dict = compound_template_field['value'][0]
        list_dict = self.create_mapped_value_list_dict(template_dict)
        result_dict_list = self.create_result_dict_list(list_dict,
                                                        template_dict)
        return result_dict_list

    def create_mapped_value_list_dict(self, template_dict: dict):
        """ Creates a dictionary where the key is the name of a nested field
        and the value is a list of all values belonging to that nested field.



        :param template_dict:
        :return:
        """
        list_dict = {}
        for k, v in template_dict.items():
            list_dict[k] = []
            if v['value']:
                list_dict[k].append(v)
            mapped_value = self.map_value(v['typeName'])
            if isinstance(mapped_value, list):
                list_dict[k].extend(mapped_value)
            else:
                list_dict[k].append(mapped_value)
        return list_dict

    @staticmethod
    def create_result_dict_list(list_dict: dict, template_dict):
        """

        TODO: Merging the dicts could made to be more efficient.
        :param list_dict:
        :param template_dict:
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
