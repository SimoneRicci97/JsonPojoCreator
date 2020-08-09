import os

from java_class_writer import *
from java_methods import StaticMethod
from json2java_mapper import map_json_name


def clear_statement(stm, indentations=0, fromind=0):
    lstm = stm[fromind:]
    stm_len = 80
    if len(lstm) > stm_len:
        ind = stm[:fromind+stm_len].rfind(' ')
        stm = stm[:ind] + '\n' + '\t' * indentations + stm[ind+1:]
        return clear_statement(stm, indentations, ind)
    return stm


def get_class_by_name(classes, alt_names, name):
    if name.count('[]'):
        name = name[:name.index('[]')]
    if name in alt_names:
        _name = alt_names[name]
    else:
        _name = map_json_name(name, isclass=True)
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
    args = list()
    for field in pojo.fields:
        if is_lang_type(field.type):
            if field.type == 'String':
                arg = f"\"{get_field_value(values, alt_names, field.name)}\""
            else:
                arg = f"{get_field_value(values, alt_names, field.name)}"
            args.append(arg)
        elif field.type.endswith('[]'):
            fieldclass = get_class_by_name(classes, alt_names, field.type)
            instance_statement = get_class_instance(fieldclass, classes, alt_names, values)
            args.append(f"new {field.type} " + "{" + f"{instance_statement}" + "}")
        else:
            fieldclass = get_class_by_name(classes, alt_names, field.type)
            instance_statement = get_class_instance(fieldclass, classes, alt_names, values)
            args.append(instance_statement)
    return pojo.all_args_constructor.strcall(args)


def main_class(pojo, classes, **kwargs):
    package = kwargs['package']
    _json = kwargs['json']
    alt_names = kwargs['alt_names']
    jclass = JavaClass('Main', '')
    jclass.add_import(f"import {package}.*;\n")
    jclass.add_import(f"import com.fasterxml.jackson.core.JsonProcessingException;\n")
    main_method = StaticMethod(jclass, 'main', 'void', [JavaField('String[]', 'args')])
    main_method.throwing.append('JsonProcessingException')
    main_method.statements.append(clear_statement(f"{pojo.name} {pojo.name.lower()} = " +
                                                  get_class_instance(pojo, classes, alt_names, _json) + ';\n',
                                                  indentations=2))
    jclass.add_import("import com.fasterxml.jackson.databind.ObjectMapper;\n")
    main_method.statements.append('ObjectMapper om = new ObjectMapper();\n')
    main_method.statements.append(f"String __json_string__ = om.writeValueAsString({pojo.name.lower()});\n")
    main_method.statements.append('System.out.println(__json_string__);\n')

    jclass.methods.append(main_method)
    jclass.default_constructor = None
    jclass.all_args_constructor = None
    jclass.builder = None
    return jclass


def make_user_trust(classpath, package):
    os.chdir(classpath)
    lib_claspath = "jackson-databind-2.11.1.jar;jackson-annotations-2.11.1.jar;jackson-core-2.11.1.jar"
    os.system(f"javac -cp \".;{lib_claspath}\" {package}/*.java")
    print('Compiled classess', flush=True)
    os.system(f"javac -cp \".;{lib_claspath}\" Main.java")
    print('Compiled Main class', flush=True)
    print('*' * 25, flush=True)
    print(flush=True)
    print(flush=True)
    os.system(f"java -cp \".;{lib_claspath}\" Main")


def build_proof(classes, args, json_dict):
    mainclass = main_class(classes[-1], classes, package=args.package, json=json_dict,
                           alt_names=args.additionalOptions['alternativeNames'])
    JavaClassWriter([mainclass], path=args.path[:args.path.index('src/main/java') + len('src/main/java')]).write()
    print('*' * 25, flush=True)
    print('Main class builded', flush=True)
    make_user_trust(args.path[:args.path.index('src/main/java') + len('src/main/java')],
                    args.path[args.path.index('src/main/java') + len('src/main/java') + 1:])
