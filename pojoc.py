import os
import sys

import json

from java_class_writer import *
from pojocreator_optparse import pojo_creator_argparse
from json2java_mapper import map_json_name, map_json_type


def print_version():
    with open('resource/info.json') as jsoninfo:
        info = json.load(jsoninfo)
    infostr = f"{info['name']}: {info['version']['major']}.{info['version']['minor']}.{info['version']['patch']}"
    print()
    print(infostr)
    print(len(infostr) * '=')
    print()
    print(f"Keep follow me for new updates at {info['links']['github']['href']}")
    print()


def read_file(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    return lines


def new_class_structure(dict_class, found):
    for classname, structure in found.items():
        for k, v in dict_class.items():
            for k1, v1 in structure.items():
                if k == k1 and type(v) == type(v1):
                    return classname
    return None


def json2class(_json, structures, **kwargs):
    extclass = kwargs['extclass'] if 'extclass' in kwargs else None
    classname = kwargs['classname']
    package = kwargs['package']
    jsonproperty = kwargs['jsonproperty'] if 'jsonproperty' in kwargs else None
    ignore = kwargs['ignore'] if 'ignore' in kwargs else []
    jsonignore = kwargs['jsonignore'] if 'jsonignore' in kwargs else None
    lombock = kwargs['lombock']
    additionalOptions = kwargs['additionalOptions']

    jclass = JavaClass(classname, package, extclass)

    classes = []

    if lombock:
        jclass.imports.extend(read_file('resource/imports.txt'))
        jclass.add_annotations(read_file('resource/lombock.txt'))

    for k, v in [(k1, v1) for k1, v1 in _json.items() if v1 not in ignore]:
        jtype = map_json_type(type(v))
        if jtype is not None:
            jclass.add_field(map_json_name(k), jtype,
                             jsonproperty=k, jsonignore=jsonignore, getter=not lombock, setter=not lombock,
                             constructors=not lombock)
        elif type(v) == dict:
            existent_class = new_class_structure(v, structures)
            if existent_class is None:
                newclassname = map_json_name(k, isclass=True) if k not in additionalOptions else additionalOptions[k]
                structures[newclassname] = v
                other_class = json2class(v, structures, classname=newclassname,
                                         lombock=lombock, package=package, ignore=ignore,
                                         jsonproperty=jsonproperty, jsonignore=jsonignore,
                                         additionalOptions=additionalOptions)
                classes.extend(other_class)
                jclass.add_field(map_json_name(k), map_json_name(k, isclass=True), jsonproperty=k,
                                 jsonignore=jsonignore, getter=not lombock, setter=not lombock,
                                 constructors=not lombock)
            else:
                jclass.add_field(map_json_name(k), map_json_name(existent_class, isclass=True), jsonproperty=k,
                                 jsonignore=jsonignore, getter=not lombock, setter=not lombock,
                                 constructors=not lombock)
        elif type(v) == list and len(v) > 0:
            existent_class = new_class_structure(v[0], structures)
            if existent_class is None:
                structures[k] = v[0]
                other_class = json2class(v[0], structures, classname=map_json_name(k, isclass=True) + 'Item',
                                         lombock=lombock, package=package, ignore=ignore,
                                         jsonproperty=jsonproperty, jsonignore=jsonignore,
                                         additionalOptions=additionalOptions)
                classes.extend(other_class)
                jclass.add_import('import java.util.List;\n')
                jclass.add_field(map_json_name(k), f'List<{map_json_name(k, isclass=True)}>', jsonproperty=k,
                                 jsonignore=jsonignore, getter=not lombock, setter=not lombock,
                                 constructors=not lombock)
            else:
                jclass.add_field(map_json_name(k), f'List<{map_json_name(existent_class, isclass=True)}>',
                                 jsonproperty=k, jsonignore=jsonignore, getter=not lombock, setter=not lombock)

    classes.append(jclass)
    return classes


def main():
    args = pojo_creator_argparse()

    if args.version:
        print_version()
        sys.exit(0)

    if os.path.isfile(args.json):
        args.json = ' '.join(read_file(args.json))

    json_dict = json.loads(args.json)
    if type(json_dict) == list:
        json_dict = json_dict[0]

    classes = json2class(json_dict, {}, classname=args.classname, lombock=args.lombock,
                         package=args.package, jsonproperty=args.jsonproperty, ignore=args.ignore,
                         inner=args.inner, jsonignore=args.jsonignore, additionalOptions=args.additionalOptions)

    JavaClassWriter(classes, path=args.path, inner=args.inner).write()


if __name__ == '__main__':
    main()