def find_values_from_key(target_key, obj):
    """
    Function to search values of specific key in a JSON object.
    It has 2 parameters: target (string) that we want to search, and obj which is a JSON object.
    Return list of found value.
    """

    results = []

    def _find_values(target_key, obj):
        try:
            for key, value in obj.items():
                if key == target_key and value != "":
                    results.append(value)
                elif not isinstance(value, str):
                    _find_values(target_key, value)
        except AttributeError:
            pass

        try:
            for item in obj:
                if not isinstance(item, str):
                    _find_values(target_key, item)
        except TypeError:
            pass

    if not isinstance(obj, str):
        _find_values(target_key, obj)
    return results


def find_values_containing_substring(target_key, substring, obj):
    """
    Function to search values containing substring in a JSON object.
    It has 3 parameters: target_key (string), substring that we want to search, and obj which is a JSON object.
    Return list of found value.
    """

    results = []

    def _find_values(target_key, obj):
        try:
            for key, value in obj.items():
                if key == target_key and substring in value:
                    results.append(value)
                elif not isinstance(value, str):
                    _find_values(target_key, value)
        except AttributeError:
            pass

        try:
            for item in obj:
                if not isinstance(item, str):
                    _find_values(target_key, item)
        except TypeError:
            pass

    if not isinstance(obj, str):
        _find_values(target_key, obj)
    return results
