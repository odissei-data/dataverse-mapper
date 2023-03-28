import jmespath


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
    value = jmespath.search(
        path,
        metadata_json
    )
    return value
