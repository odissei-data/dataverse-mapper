import jmespath

SPECIAL_CHARACTERS_LIST = [":", "@", "#"]


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
            if obj.get(path[0]) is None:
                return None
            return obj[path[0]]
    else:
        if obj.get(path[0]) is None:
            return None
        # Take the key given by the first element of path and drill down.
        return drill_down(obj[path[0]], path[1:])


def drill_down_v2(metadata_json, path):
    """
    Returns value found at the end of the path.

    Some metadata formats use special characters in their keys. Because of this
    each step of the path must sit between double quotes.

    :param metadata_json: metadata in json format
    :param path: string
    :return: string, list, or dict
    """
    split_path = path.split(".")

    # current_value = metadata_json
    # for step in split_path:
    #
    #     index = step.find('[')
    #     if index == -1:
    #         current_value = jmespath.search(
    #             f'"{step}"',
    #             current_value
    #         )
    #     else:
    #         current_value = path_with_slice(current_value, step, index)

    print("dit is path", path)
    current_value = jmespath.search(path, metadata_json)
    print("dit is value", current_value)

    return current_value


def path_with_slice(metadata_json, step, index):
    """
    Returns the value of a sliced list.

    Example, the step is "Contextvariabele[1]" this needs to become
    '"Contextvariabele"[1]'.

    :param metadata_json: metadata in json format
    :param step: string, the next object to search for
    :param index: int, location of '['
    :return: string, list, or dict
    """
    print("\n")
    print("slice this step", step)
    # extract 'Contextvariabele' from 'Contextvariabele[1]'
    key = step[:index]

    # extract `[1]` from 'Contextvariabele[1]'
    slice_index = step[index:]

    value = jmespath.search(
        f'"{key}"{slice_index}',
        metadata_json
    )
    print("sliced value", value)
    print("\n")

    return value


def clean_mapping(mapping):
    """
    Special characters need to be escaped for jmespath to work properly.

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
    Escape special characters for jmespath by placing them between double
    quotes.

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

    return new_path[1:]
