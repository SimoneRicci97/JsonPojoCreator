import re


def url2javaname(url, isclass=False):
    if url.count('#') > 0:
        print(url, url[url.index('#') + 1:])
        return url[url.index('#') + 1:]
    if re.fullmatch('http://.*', url):
        url = url[len('http://'):]
    elif re.fullmatch('https://.*', url):
        url = url[len('https://'):]
    if url[-1] == '/':
        url = url[:-1]
    return map_json_name(url.split('/')[-1], isclass)


def map_json_name(name, isclass=False):
    if re.fullmatch(
            "^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$",
            name):
        name = url2javaname(name, isclass)
    java_name = name.replace('_', ' ')
    java_name = java_name.replace('-', ' ')
    parts = java_name.split(' ')
    java_name = parts[0] if not isclass else parts[0].capitalize()
    for part in parts[1:]:
        java_name += part.capitalize()
    return java_name


def map_json_type(jstype, primitive):
    if jstype == str:
        return 'String'
    elif jstype == int:
        return 'int' if primitive else 'Integer'
    elif jstype == float:
        return 'float' if primitive else 'BigDecimal'
    elif jstype == bool:
        return 'boolean' if primitive else 'Boolean'
