import os
import sys

import json

from java_class_writer import *
from pojocreator_optparse import pojo_creator_argparse
from json2java_mapper import map_json_name, map_json_type


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


def get_class_by_name(classes, alt_names, name):
    # print(alt_names.keys())
    # print(f"Looking for class {name}->", end='')
    if name.count('<') > 0 and name.count('>') > 0:
        name = name[name.index('<')+1:name.index('>')]
    # print(f"{name} ->", end='')
    if name in alt_names:
        _name = alt_names[name]
    else:
        _name = map_json_name(name, isclass=True)
    # print(f"{_name} ")
    for jclass in classes:
        if jclass.name == _name:
            return jclass


def get_field_value(_json, alt_names, name):
    if type(_json) != dict:
        return None
    for k, v in _json.items():
        value = get_field_value(v, alt_names, name)
        if map_json_name(k) == name or (k in alt_names.keys() and alt_names[k] == name):
            return v
        elif value is not None:
            return value


def get_class_instance(pojo, classes, alt_names, values):
    statements = list()
    for field in pojo.fields:
        if is_lang_type(field.type):
            if field.type == 'String':
                stm = f"{field.type} {field.name} = \"{get_field_value(values, alt_names, field.name)}\";"
            else:
                stm = f"{field.type} {field.name} = {get_field_value(values, alt_names, field.name)};"
            if statements.count(stm) == 0:
                statements.append(stm)
        else:
            fieldclass = get_class_by_name(classes, alt_names, field.type)
            instance_statements = get_class_instance(fieldclass, classes, alt_names, values)
            for stm in instance_statements:
                if statements.count(stm) == 0:
                    statements.append(stm)
            instance = f"{fieldclass.name} {field.name} = {fieldclass.all_args_constructor.strcall([stm.split()[1] for stm in instance_statements])}"
            statements.append(instance)
    # print("=" * len(f"Instance for {pojo.name}"))
    # print(f"Instance for {pojo.name}")
    # print('\n\t'.join(statements))
    # print("=" * len(f"Instance for {pojo.name}"))
    return statements


def main_class(pojo, classes, **kwargs):
    package = kwargs['package']
    _json = kwargs['json']
    alt_names = kwargs['alt_names']
    jclass = JavaClass('IfYouDontTrustMe', package)
    main_method = StaticMethod(jclass, 'main', 'void', [JavaField('String[]', 'args')])
    main_method.statements.extend(get_class_instance(pojo, classes, alt_names, _json))
    jclass.methods.append(main_method)
    jclass.default_constructor = None
    jclass.all_args_constructor = None
    jclass.builder = None
    return jclass


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
    print(id(additional_options))
    classes = []

    for k, v in [(k1, v1) for k1, v1 in _json.items() if v1 not in ignore]:
        jtype = map_json_type(type(v), primitive)
        if jtype is not None:
            jclass.add_field(map_json_name(k), jtype, jsonproperty=k, jsonignore=jsonignore)
        elif type(v) == dict:
            existent_class = new_class_structure(v, structures)
            fieldclassname = map_json_name(k, isclass=True) if k not in additional_options['alternativeNames'] \
                else additional_options['alternativeNames'][k]
            if existent_class is None:
                structures[fieldclassname] = v
                other_class = json2class(v, structures, classname=fieldclassname, primitive=primitive,
                                         package=package, ignore=ignore,
                                         jsonproperty=jsonproperty, jsonignore=jsonignore,
                                         additionalOptions=additional_options)
                classes.extend(other_class)
                jclass.add_field(map_json_name(k), fieldclassname, jsonproperty=k,
                                 jsonignore=jsonignore)
            else:
                additional_options['alternativeNames'][map_json_name(k)] = fieldclassname
                jclass.add_field(map_json_name(k), fieldclassname, jsonproperty=k,
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
                                         jsonproperty=jsonproperty, jsonignore=jsonignore,
                                         additionalOptions=additional_options)
                classes.extend(other_class)
                jclass.add_field(map_json_name(k), f'List<{fieldclassname}>', jsonproperty=k, jsonignore=jsonignore)
            else:
                additional_options['alternativeNames'][map_json_name(k)] = existent_class
                jclass.add_field(map_json_name(k), f'List<{existent_class}>', jsonproperty=k, jsonignore=jsonignore)

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

    if args.additionalOptions['superclass'] is not None:
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

    mainclass = main_class(classes[-1], classes, package=args.package, json=json_dict,
                            alt_names=args.additionalOptions['alternativeNames'])
    JavaClassWriter([mainclass], path=args.path).write()


if __name__ == '__main__':
    main()
