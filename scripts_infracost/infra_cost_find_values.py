"""Function to search value of specific key in a JSON object"""

def find_values(target, obj):
    """
    Function to search value of specific key in a JSON object.
    It has 2 parameter: target (string) that we want to search, and obj which is a JSON object.
    Return list of found value.
    """

    results = []

    def _find_values(target, obj):
        try:
            for key, value in obj.items():
                if key == target and value != "":
                    results.append(value)
                elif not isinstance(value, str):
                    _find_values(target, value)
        except AttributeError:
            pass

        try:
            for item in obj:
                if not isinstance(item, str):
                    _find_values(target, item)
        except TypeError:
            pass

    if not isinstance(obj, str):
        _find_values(target, obj)
    return results
