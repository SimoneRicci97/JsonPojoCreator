import random

def get_getter(field_type, fieldname, indlevel=0):
    return '\t' * indlevel + f'\tpublic {field_type} get{fieldname.capitalize()}()' + '{\n' + \
           '\t' * indlevel + f'\t\treturn this.{fieldname};\n' + \
           '\t' * indlevel + '\t}\n'


def get_setter(field_type, fieldname, classname, indlevel=0):
    return '\t' * indlevel + f"\tpublic {classname} set{fieldname.capitalize()}({field_type} {fieldname}) " + '{\n' + \
           '\t' * indlevel + f"\t\tthis.{fieldname} = {fieldname};\n" + \
           '\t' * indlevel + f"\t\treturn this;\n" + \
           '\t' * indlevel + '\t}\n'


def get_class_header_name(static, classname, indlevel=0, superclass=None, serializable=False):
    return '\t' * indlevel + f"public{static} class {classname}" + \
           (f" extends {superclass}" if superclass is not None else '') + \
           (" implements Serializable" if serializable else '') + \
           ' {\n'


def get_default_constructor(classname, indlevel=0):
    return '\t' * indlevel + f"\tpublic {classname}()" + ' {\n' + \
            '\t' * indlevel + "\t\tsuper();\n" + \
            '\t' * indlevel + "\t}\n\n"


class AllArgsConstructor:
    def __init__(self, classname, indlevel=0):
        self.classname = classname
        self.indlevel = indlevel
        self.fields = []

    def add_field(self, field):
        self.fields.append(field)

    def __str__(self):
        self_str = ''
        self_str += '\t' * self.indlevel + f"\tpublic {self.classname}("
        for field in self.fields:
            self_str += f"{field.type} {field.name}"
            self_str += ', ' if field != self.fields[-1] else ') {\n'
        for field in self.fields:
            self_str += '\t' * self.indlevel + f"\t\tthis.{field.name} = {field.name};\n"
        self_str += '\t' * self.indlevel + '\t}\n\n'
        return self_str


class JavaField:
    def __init__(self, type, name, indlevel=0):
        self.type = type
        self.name = name
        self.indlevel = indlevel

    def __str__(self):
        return f"\tprivate {self.type} {self.name};"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return self.name == other.name and self.type == self.type


class JavaClass:
    def __init__(self, classname, package, extclass=None, superclass=None, serializable=False):
        self.extclass = extclass
        self.name = classname
        self.indlevel = 1 if extclass is not None else 0
        self.all_args_constructor = AllArgsConstructor(self.name, self.indlevel)
        self.package = package
        self.superclass = superclass
        self.serializable = serializable
        self.innerclasses = []
        self.classannotations = []
        self.imports = []
        self.fields = []
        self.default_constructor = None
        self.jsonproperties = dict()
        self.jsonignore = list()
        self.getters = list()
        self.setters = list()
        self.extclass = extclass
        self.init = True

    def add_annotations(self, anns):
        self.classannotations.extend(anns)
        self.classannotations.append('\n')

    def add_field(self, name, fieldtype, jsonproperty=None, jsonignore=False,
                  getter=False, setter=False, constructors=False):

        if fieldtype == 'BigDecimal':
            self.add_import('import java.math.BigDecimal;')
        field = JavaField(fieldtype, name)

        if jsonproperty is not None:
            self.jsonproperties[field] = jsonproperty
            self.add_import('import com.fasterxml.jackson.annotation.JsonProperty;\n')

        if jsonignore:
            self.jsonignore.append(field)
            self.add_import('import com.fasterxml.jackson.annotation.JsonIgnore;\n')

        self.fields.append(field)

        if constructors:
            if self.default_constructor is None:
                self.default_constructor = get_default_constructor(self.name, self.indlevel)
            self.all_args_constructor.add_field(field)
        else:
            self.all_args_constructor = None

        if getter:
            self.getters.append(field)

        if setter:
            self.setters.append(field)

    def add_import(self, importrow):
        if self.extclass is not None:
            self.extclass.add_import(importrow)
        elif self.imports.count(importrow) == 0:
            self.imports.append(importrow)

    def __setattr__(self, key, value):
        if not hasattr(self, 'init'):
            super().__setattr__(key, value)
            return
        if key == 'indlevel':
            super().__setattr__(key, value)
            self.default_constructor = get_default_constructor(self.name, self.indlevel)
            if self.all_args_constructor is not None:
                self.all_args_constructor.indlevel = value
        elif key == 'serializable' and value:
            super().__setattr__(key, value)
            self.add_import('import java.io.Serializable;\n')
        else:
            super().__setattr__(key, value)

    def __str__(self):
        return self.header() + self.footer()
        # self_str = ''
        # classname = get_class_header_name(' static' if self.extclass is not None else '',
        #                                   self.name, self.indlevel, self.superclass, self.serializable)
        # if self.extclass is None:
        #     self_str += f'package {self.package};\n\n' if self.package is not None else '\n'
        #     self_str += ''.join(self.imports)
        # self_str += '\n' + ''.join(['\t' * self.indlevel + ann for ann in self.classannotations])
        # self_str += classname
        # self_str += '\n'.join(['\t' * self.indlevel + str(ic) for ic in self.innerclasses])
        # self_str += '\n'
        # self_str += ''.join(['\t' * self.indlevel + f for f in self.fields])
        # self_str += self.default_constructor if self.default_constructor is not None else ''
        # self_str += str(self.all_args_constructor)
        # self_str += '\n'.join(['\t' * self.indlevel + m for m in self.method])
        # self_str += '\t' * self.indlevel + '}\n'
        # return self_str

    def header(self, indlevel=0):
        classname = get_class_header_name(' static' if indlevel > 0 else '',
                                          self.name, indlevel, self.superclass, self.serializable)
        self_hdr = ''
        if self.extclass is None:
            self_hdr += f'package {self.package};\n\n' if self.package is not None else '\n'
            self_hdr += ''.join(self.imports)
        self_hdr += '\n' + ''.join(['\t' * indlevel + ann for ann in self.classannotations])
        self_hdr += classname
        self_hdr += '\n'

        return self_hdr

    def footer(self, indlevel=0):
        self_ftr = ''
        if self.serializable:
            self_ftr += '\n' + '\t' * indlevel + f"\tprivate static final long serialVersionUID = " \
                        f"-{random.randint(20, 30) ** random.randint(20, 30)}L;\n"
        self_ftr += '\n'.join(['\t' * indlevel + str(ic) for ic in self.innerclasses])
        self_ftr += '\n'
        for f in self.fields:
            if f in self.jsonproperties:
                self_ftr += '\t' * self.indlevel + '\t@JsonProperty(\"{}\")\n'.format(self.jsonproperties[f])
            if f in self.jsonignore:
                self_ftr += '\t' * self.indlevel + '\t@JsonIgnore\n'
            self_ftr += '\t' * self.indlevel + str(f) + '\n\n'
        self_ftr += self.default_constructor if self.default_constructor is not None else ''
        self_ftr += str(self.all_args_constructor) if self.all_args_constructor is not None else ''
        self_ftr += '\n'.join([get_getter(g.type, g.name, self.indlevel) for g in self.getters])
        self_ftr += '\n'
        self_ftr += '\n'.join([get_setter(s.type, s.name, self.name, self.indlevel) for s in self.setters])
        self_ftr += '\t' * indlevel + '}\n'
        return self_ftr

    def body(self, indlevel=1):
        classname = get_class_header_name(' static' if indlevel > 0 else '',
                                          self.name, indlevel, self.superclass, self.serializable)
        self_bdy = ''
        self_bdy += '\n' + ''.join(['\t' * indlevel + ann for ann in self.classannotations])
        self_bdy += classname
        self_bdy += self.footer(indlevel)
        return self_bdy


class JavaClassWriter:
    def __init__(self, javaclasses, **kwargs):
        self.path = kwargs['path']
        self.javaclasses = javaclasses
        self.f = None
        self.use_inner = kwargs['inner']

    @staticmethod
    def __writelines(lines, f):
        if f is not None:
            f.write(lines)
        else:
            print(lines)

    def __write_class(self, jclass):
        self.__writelines(str(jclass), self.f)

    def __write_header(self, jclass):
        self.__writelines(jclass.header(), self.f)

    def __write_footer(self, jclass):
        self.__writelines(jclass.footer(), self.f)

    def __write_body(self, jclass):
        self.__writelines(jclass.body(), self.f)

    def write(self):
        if not self.use_inner:
            for jclass in self.javaclasses:
                self.f = open(f'{self.path}/{jclass.name}.java', 'w')
                self.__write_class(jclass)
                self.f.close()
        else:
            extclass = self.javaclasses[-1]
            self.f = open(f'{self.path}/{extclass.name}.java', 'w')
            self.__write_header(extclass)
            for jclass in self.javaclasses[:-1]:
                jclass.indlevel = 1
                self.__write_body(jclass)
            self.__write_footer(extclass)
            self.f.close()
