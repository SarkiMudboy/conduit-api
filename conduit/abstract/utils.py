from collections import defaultdict

def parse_querydict(querydict: dict):

    result = defaultdict(list)

    for key in querydict.keys():
        normalized_value = querydict[key].rstrip("[]")
        result[key] = normalized_value

    return result