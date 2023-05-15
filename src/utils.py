import jmespath

SPECIAL_CHARACTERS_LIST = [":", "@", "#"]


def drill_down(metadata_json, path):
    """
    Returns value found at the end of the path.

    This method assumes that the paths have been cleaned.

    :param metadata_json: metadata in json format
    :param path: string
    :return: string or list
    """
    value = jmespath.search(path, metadata_json)
    return value


def clean_mapping(mapping):
    """
    Returns cleaned mapping.

    :param mapping: json
    :return: json
    """
    for key in mapping.keys():
        path_list = mapping[key]

        for counter, path in enumerate(path_list):
            if any(character in path for character in SPECIAL_CHARACTERS_LIST):
                cleaned_path = clean_path(path)
                path_list[counter] = cleaned_path

    return mapping


def clean_path(path):
    """
    Returns cleaned path.

    Some mappings contain special characters in their keys. This breaks
    jmespath, so they must be escaped by placing the key between double quotes.
    While cleaning slicing must also be handles properly.

    Examples:
    - The key 'hello:world' needs to become '"hello:world"'
    - The key 'foo:bar[2]' needs to become '"foo:bar"[2]'

    :param path: string
    :return: string
    """
    new_path = ''

    split_path = path.split(".")
    for step in split_path:
        index = step.find('[')
        if index == -1:
            new_step = f'."{step}"'
        else:
            key = step[:index]
            slice_index = step[index:]
            new_step = f'."{key}"{slice_index}'

        new_path += new_step

    # remove the leading '.' from the path
    cleaned_path = new_path[1:]

    return cleaned_path
