import optparse
import os
import sys

import json
import re

from java_class_writer import *

ERR_BAD_ARGS = 2


def set_parse_option():
    parser = optparse.OptionParser(description='Copy/paste tool')
    parser.add_option('-j', '--json', default=None, dest='json', help='json to transform in java class')
    parser.add_option('-c', '--classname', default=None, dest='classname', help='Name of java class')
    parser.add_option('-l', '--lombock', default=False, action='store_true', dest='lombock',
                      help='generate lombock annotations')
    parser.add_option('-q', '--json_property', default=False, action='store_true', dest='jsonproperty',
                      help='Add @JsonProperty annotations')
    parser.add_option('-e', '--exclude', default=None, dest='exclude', help='Exclude json fields from java class')
    parser.add_option('-i', '--jsonignore', default=None, dest='jsonignore',
                      help='Comma separeted list. Add @JsonIgnore annotations over specified fields')
    parser.add_option('-p', '--package', default='.', dest='package',
                      help='Package to write java class.')
    parser.add_option('-I', '--inner', default=False, action='store_true', dest='inner', help='Use inner classes')
    parser.add_option('--ignore', default=None, dest='ignore',
                      help='Comma separated list. json fields in list will be ignored building java class')

    return parser


def usage(parser=None, excode=0):
    if parser is None:
        parser = set_parse_option()
    parser.print_help()
    sys.exit(excode)


def bad_args_error(errtext):
    print(errtext, end='\n\n')
    usage(excode=ERR_BAD_ARGS)


def json2java_argparse():
    parser = set_parse_option()
    options, args = parser.parse_args()

    if options.json is None:
        bad_args_error("json (-j, --json) arg is required")

    if options.classname is None:
        bad_args_error("json (-c, --classname) arg is required")

    options.classname = options.classname.capitalize()

    if options.exclude is not None:
        options.exclude = options.exclude.split(',')

    if options.jsonignore is not None:
        options.jsonignore = options.jsonignore.split(',')

    if options.package[-1] == '/':
        options.package = options.package[:-1]


    options.ignore = options.ignore.split(',') if options.ignore is not None else []

    return options


def read_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines


def write_field(writer, fieldname, type, jsonproperty=False, jsonignore=False):
    field_info = []

    if jsonproperty:
        field_info.append(f'@JsonProperty(\"{fieldname}\")')

    if jsonignore:
        field_info.append('@JsonIgnore')

    field_info.append(f'private {type} {fieldname};')

    for info in field_info:
        writer.write(info)


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
    url = None
    if re.fullmatch(
            "^(?:http(s)?:\/\/)?[\w.-]+(?:\.[\w\.-]+)+[\w\-\._~:/?#[\]@!\$&'\(\)\*\+,;=.]+$",
            name):
        url = name
        name = url2javaname(name, isclass)
    java_name = name.replace('_', ' ')
    java_name = java_name.replace('-', ' ')
    parts = java_name.split(' ')
    java_name = parts[0] if not isclass else parts[0].capitalize()
    for part in parts[1:]:
        java_name += part.capitalize()
    return java_name


def map_json_type(jstype):
    if jstype == str:
        return 'String'
    elif jstype == int:
        return 'int'
    elif jstype == float:
        return 'BigDecimal'
    elif jstype == bool:
        return 'boolean'


def new_class_structure(dict_class, found):
    for classname, structure in found.items():
        for k, v in dict_class.items():
            for k1, v1 in structure.items():
                if k == k1 and type(v) == type(v1):
                    return classname
    return None


def json2class(json, structures, **kwargs):
    extclass = kwargs['extclass'] if 'extclass' in kwargs else None
    classname = kwargs['classname']
    package = kwargs['package']
    jsonproperty = kwargs['jsonproperty'] if 'jsonproperty' in kwargs else None
    ignore = kwargs['ignore'] if 'ignore' in kwargs else []
    jsonignore = kwargs['jsonignore'] if 'jsonignore' in kwargs else None
    lombock = kwargs['lombock']

    jclass = JavaClass(classname, package, extclass)

    classes = []

    if lombock:
        jclass.imports.extend(read_file('resource/imports.txt'))
        jclass.add_annotations(read_file('resource/lombock.txt'))

    for k, v in [(k1, v1) for k1, v1 in json.items() if v1 not in ignore]:
        jtype = map_json_type(type(v))
        if jtype is not None:
            jclass.add_field(map_json_name(k), jtype,
                             jsonproperty=k, jsonignore=jsonignore, getter=not lombock, setter=not lombock)
        elif type(v) == dict:
            existent_class = new_class_structure(v, structures)
            if existent_class is None:
                structures[k] = v
                other_class = json2class(v, structures, classname=map_json_name(k, isclass=True),
                                         lombock=lombock, package=package, ignore=ignore,
                                         jsonproperty=jsonproperty, jsonignore=jsonignore)
                classes.extend(other_class)
                jclass.add_field(map_json_name(k), map_json_name(k, isclass=True), jsonproperty=k,
                                 jsonignore=jsonignore, getter=not lombock, setter=not lombock)
            else:
                jclass.add_field(map_json_name(k), map_json_name(existent_class, isclass=True), jsonproperty=k,
                                 jsonignore=jsonignore, getter=not lombock, setter=not lombock)
        elif type(v) == list and len(v) > 0:
            existent_class = new_class_structure(v[0], structures)
            if existent_class is None:
                structures[k] = v[0]
                other_class = json2class(v[0], structures, classname=map_json_name(k, isclass=True) + 'Item',
                                         lombock=lombock, package=package, ignore=ignore,
                                         jsonproperty=jsonproperty, jsonignore=jsonignore)
                classes.extend(other_class)
                jclass.add_import('import java.util.List;\n')
                jclass.add_field(map_json_name(k), f'List<{map_json_name(k, isclass=True)}>', jsonproperty=k,
                                jsonignore=jsonignore, getter=not lombock, setter=not lombock)
            else:
                jclass.add_field(map_json_name(k), f'List<{map_json_name(existent_class, isclass=True)}>',
                                 jsonproperty=k, jsonignore=jsonignore, getter=not lombock, setter=not lombock)


    classes.append(jclass)
    return classes


def main():
    args = json2java_argparse()
    print(args.package[len('src/main/java/'):].replace('/', '.'))
    if os.path.isfile(args.json):
        args.json = ' '.join(read_file(args.json))

    json_dict = json.loads(args.json)
    if type(json_dict) == list:
        json_dict = json_dict[0]

    classes = json2class(json_dict, {}, classname=args.classname, lombock=args.lombock,
                        package=args.package[len('src/main/java/'):].replace('/', '.'),
                        jsonproperty=args.jsonproperty, ignore=args.ignore, inner=args.inner,
                         jsonignore=args.jsonignore)

    JavaClassWriter(classes, inner=args.inner).write()


if __name__ == '__main__':
    main()
