import os
import sys

import json

from java_class_writer import *
from pojocreator_optparse import pojo_creator_argparse
from json2java_mapper import map_json_name, map_json_type
from pojoc_proof import build_proof


def forall(__foo, __list):
    for item in __list:
        __foo(item)


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


def json_skeleton(json_dict):
    d = dict()
    for k, v in json_dict.items():
        d[k] = type(v)
    return d


def new_class_structure(dict_class, found):
    for classname, structure in found.items():
        existent = json_skeleton(structure)
        newclass = json_skeleton(dict_class)
        if set(existent.keys()) == set(newclass.keys()):
            flag = True
            for k in dict_class.keys():
                flag = flag and existent[k] == newclass[k]
            if flag:
                return classname
    return None


def json2class(_json, structures, **kwargs):
    extclass = kwargs['extclass'] if 'extclass' in kwargs else None
    classname = kwargs['classname']
    package = kwargs['package']
    primitive = kwargs['primitive']
    jsonproperty = kwargs['jsonproperty'] if 'jsonproperty' in kwargs else None
    ignore = kwargs['ignore'] if 'ignore' in kwargs else []
    jsonignore = kwargs['jsonignore'] if 'jsonignore' in kwargs else None
    additional_options = kwargs['additionalOptions']
    if 'alternativeNames' not in additional_options:
        additional_options['alternativeNames'] = dict()
    jclass = JavaClass(classname, package, extclass)
    classes = []

    for k, v in [(k1, v1) for k1, v1 in _json.items() if v1 not in ignore]:
        jtype = map_json_type(type(v), primitive)
        if jtype is not None:
            jclass.add_field(map_json_name(k), jtype, jsonproperty=(k if jsonproperty else None), jsonignore=jsonignore)
        elif type(v) == dict:
            existent_class = new_class_structure(v, structures)
            fieldclassname = map_json_name(k, isclass=True) if k not in additional_options['alternativeNames'] \
                else additional_options['alternativeNames'][k]
            if existent_class is None:
                structures[fieldclassname] = v
                other_class = json2class(v, structures, classname=fieldclassname, primitive=primitive,
                                         package=package, ignore=ignore,
                                         jsonproperty=(k if jsonproperty else None), jsonignore=jsonignore,
                                         additionalOptions=additional_options)
                classes.extend(other_class)
                jclass.add_field(map_json_name(k), fieldclassname, jsonproperty=(k if jsonproperty else None),
                                 jsonignore=jsonignore)
            else:
                additional_options['alternativeNames'][map_json_name(k)] = fieldclassname
                jclass.add_field(map_json_name(k), fieldclassname, jsonproperty=(k if jsonproperty else None),
                                 jsonignore=jsonignore)
        elif type(v) == list and len(v) > 0:
            existent_class = new_class_structure(v[0], structures)
            jclass.add_import('import java.util.List;\n')
            fieldclassname = additional_options['alternativeNames'][k] if k in additional_options['alternativeNames'] \
                else (map_json_name(k, isclass=True) + 'Item')
            if existent_class is None:
                structures[fieldclassname] = v[0]
                other_class = json2class(v[0], structures, classname=fieldclassname,
                                         package=package, ignore=ignore, primitive=primitive,
                                         jsonproperty=(k if jsonproperty else None), jsonignore=jsonignore,
                                         additionalOptions=additional_options)
                classes.extend(other_class)
                jclass.add_field(map_json_name(k), f'{fieldclassname}[]', jsonproperty=(k if jsonproperty else None),
                                 jsonignore=jsonignore)
            else:
                additional_options['alternativeNames'][map_json_name(k)] = existent_class
                jclass.add_field(map_json_name(k), f'{existent_class}[]', jsonproperty=(k if jsonproperty else None),
                                 jsonignore=jsonignore)

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

    classes = json2class(json_dict, {}, classname=args.classname, primitive=args.primitive,
                         package=args.package, jsonproperty=args.jsonproperty, ignore=args.ignore,
                         inner=args.inner, jsonignore=args.jsonignore, additionalOptions=args.additionalOptions)

    if 'superclass' in args.additionalOptions:
        classes[-1].superclass = args.additionalOptions['superclass']

    for jclass in classes:
        jclass.serializable = args.additionalOptions['serializable']

        if args.additionalOptions['hideDefaulConstructor'] and jclass.default_constructor is not None:
            jclass.default_constructor.public = False

        if not args.additionalOptions['builder']:
            jclass.builder = None

        if args.lombock:
            jclass.use_lombock()

    JavaClassWriter(classes, path=args.path, inner=args.inner).write()

    print("*" * len('*Pojo classes created!*'), flush=True)
    print("*Pojo classes created!*", flush=True)
    print("*" * len('*Pojo classes created!*'), flush=True)

    if 'IDontBelieve' in args.additionalOptions and args.additionalOptions['IDontBelieve']:
        build_proof(classes, args, json_dict)


if __name__ == '__main__':
    main()
