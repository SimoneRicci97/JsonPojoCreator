import random
from java_methods import *


def get_class_header_name(static, classname, indlevel=0, superclass=None, serializable=False):
    return '\t' * indlevel + f"public{static} class {classname}" + \
           (f" extends {superclass}" if superclass is not None else '') + \
           (" implements Serializable" if serializable else '') + \
           ' {\n'


def check_type(jtype):
    if jtype == 'BigDecimal':
        return 'java.math.BigDecimal'
    if jtype == 'Integer':
        return 'java.lang.Integer'
    if jtype == 'Boolean':
        return 'java.lang.Boolean'
    return None


def is_lang_type(field_type):
    return field_type in ['int', 'Integer', 'String', 'float', 'BigDecimal', 'boolean', 'Boolean']


class JavaField:
    def __init__(self, jtype, name, indlevel=0, accessor='private'):
        self.type = jtype
        self.name = name
        self.accessor = accessor
        self.indlevel = indlevel

    def __str__(self):
        return f"\t{self.accessor} {self.type} {self.name};"

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        return type(other) == type(self) and self.name == other.name and self.type == other.type


class JavaClass:
    def __init__(self, classname, package, extclass=None, superclass=None, serializable=False):
        self.extclass = extclass
        self.name = classname
        self.indlevel = 1 if extclass is not None else 0
        self.all_args_constructor = Constructor(self, self.name, [], indlevel=self.indlevel)
        self.package = package
        self.superclass = superclass
        self.serializable = serializable
        self.innerclasses = []
        self.classannotations = []
        self.imports = []
        self.fields = []
        self.default_constructor = DefaultConstructor(self, self.name, indlevel=self.indlevel)
        self.jsonproperties = dict()
        self.jsonignore = list()
        self.getters = list()
        self.setters = list()
        self.methods = list()
        self.extclass = extclass
        if type(self) != Builder:
            self.builder = Builder(self, self.package)
        self.init = True

    def add_annotations(self, anns):
        self.classannotations.append(anns)

    def add_field(self, name, fieldtype, jsonproperty=None, jsonignore=False):
        _import = check_type(fieldtype)
        if _import is not None:
            self.add_import(f'import {_import};\n')
        field = JavaField(fieldtype, name)

        if jsonproperty is not None:
            self.jsonproperties[field] = jsonproperty
            self.add_import('import com.fasterxml.jackson.annotation.JsonProperty;\n')

        if jsonignore:
            self.jsonignore.append(field)
            self.add_import('import com.fasterxml.jackson.annotation.JsonIgnore;\n')

        self.fields.append(field)

        if self.all_args_constructor is not None:
            self.all_args_constructor.add_field(field)

        self.getters.append(Getter(self, field, prefix='get', indlevel=self.indlevel))

        self.setters.append(Setter(self, field, prefix='set', indlevel=self.indlevel))

        if hasattr(self, 'builder') and self.builder is not None:
            self.builder.add_field(name, fieldtype)

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
            if self.default_constructor is not None:
                self.default_constructor = DefaultConstructor(self, self.name, indlevel=value)

            if self.all_args_constructor is not None:
                self.all_args_constructor.indlevel = value

            for g in self.getters:
                g.indlevel = value
            for s in self.setters:
                s.indlevel = value
        elif key == 'serializable' and value:
            super().__setattr__(key, value)
            self.add_import('import java.io.Serializable;\n')
        else:
            super().__setattr__(key, value)

    def __str__(self):
        return self.get_header() + self.get_footer()

    def get_header(self):
        classname = get_class_header_name(' static' if self.indlevel > 0 else '',
                                          self.name, self.indlevel, self.superclass, self.serializable)
        self_hdr = ''
        if self.extclass is None:
            if self.package is not None and len(self.package) > 0:
                self_hdr += f'package {self.package};\n\n' if self.package is not None else '\n'
            self_hdr += ''.join(self.imports)
        self_hdr += '\n' + ''.join(['\t' * self.indlevel + ann for ann in self.classannotations])
        self_hdr += classname
        self_hdr += '\n'

        return self_hdr

    def get_footer(self):
        self_ftr = ''
        if self.serializable:
            self_ftr += '\n' + '\t' * self.indlevel + f"\tprivate static final long serialVersionUID = " \
                        f"-{str(random.randint(20, 30) ** random.randint(20, 30))[:8]}L;\n"
        self_ftr += '\n'.join(['\t' * self.indlevel + str(ic) for ic in self.innerclasses])
        self_ftr += '\n'
        self_ftr += self.get_fields()
        self_ftr += self.get_methods()
        self_ftr += str(self.builder) if hasattr(self, 'builder') and self.builder is not None else ''
        self_ftr += '\t' * self.indlevel + '}\n'
        return self_ftr

    def get_fields(self):
        self_fld = ''
        for f in self.fields:
            if f in self.jsonproperties:
                self_fld += '\t' * self.indlevel + '\t@JsonProperty(\"{}\")\n'.format(self.jsonproperties[f])
            if f in self.jsonignore:
                self_fld += '\t' * self.indlevel + '\t@JsonIgnore\n'
            if f in self.getters:
                self_fld += '\t' * self.indlevel + '\t@Getter\n'
            if f in self.getters:
                self_fld += '\t' * self.indlevel + '\t@Setter\n'
            self_fld += '\t' * self.indlevel + str(f) + '\n\n'
        return self_fld

    def get_body(self):
        classname = get_class_header_name(' static' if self.indlevel > 0 else '',
                                          self.name, self.indlevel, self.superclass, self.serializable)
        self_bdy = ''
        self_bdy += '\n' + ''.join(['\t' * self.indlevel + ann for ann in self.classannotations])
        self_bdy += classname
        self_bdy += self.get_footer()
        return self_bdy

    def get_methods(self):
        self_mtd = ''
        self_mtd += str(self.default_constructor) if self.default_constructor is not None else ''
        self_mtd += str(self.all_args_constructor) if self.all_args_constructor is not None and \
            len(self.fields) > 0 else ''
        if all(list(map(lambda g: type(g) == Getter, self.getters))):
            self_mtd += ''.join([str(g) for g in self.getters])
            self_mtd += '\n'
        if all(list(map(lambda s: type(s) == Setter, self.setters))):
            self_mtd += ''.join([str(s) for s in self.setters])
        self_mtd += ''.join([str(m) for m in self.methods])
        return self_mtd

    def use_lombock(self):
        self.add_import('import lombok.Getter;\n')
        self.add_import('import lombok.Setter;\n')
        self.add_import('import lombok.AllArgsConstructor;\n')
        self.add_import('import lombok.NoArgsConstructor;\n')
        self.add_import('import lombok.experimental.Accessors;\n')

        if len(self.getters) == len(self.fields):
            self.add_annotations('@Getter\n')
            self.getters = []
        else:
            self.getters = [g.field for g in self.getters]

        if len(self.setters) == len(self.fields):
            self.add_annotations('@Setter\n')
            self.setters = []
        else:
            self.setters = [s.field for s in self.setters]
        self.add_annotations('@NoArgsConstructor\n')
        self.add_annotations('@AllArgsConstructor\n')
        self.default_constructor = None
        self.all_args_constructor = None
        if hasattr(self, 'builder') and self.builder is not None:
            self.add_import('import lombok.Builder;\n')
            self.add_annotations('@Builder\n')
        self.builder = None
        self.add_annotations('@Accessors(chain = true)\n')


class Builder(JavaClass):
    def __init__(self, javaclass, package):
        super().__init__('Builder', package, extclass=javaclass)
        self.all_args_constructor = None
        self.methods.append(BuilderMethod(self, javaclass, self.indlevel))

    def add_field(self, name, fieldtype, jsonproperty=None, jsonignore=False):
        super().add_field(name, fieldtype, jsonproperty, jsonignore)
        self.getters = []
        self.setters[-1].method_name = f"with{name.capitalize()}"


class JavaClassWriter:
    def __init__(self, javaclasses, **kwargs):
        self.path = kwargs['path']
        self.javaclasses = javaclasses
        self.f = None
        self.use_inner = kwargs['inner'] if 'inner' in kwargs else False

    @staticmethod
    def __writelines(lines, f):
        if f is not None:
            f.write(lines)
        else:
            print(lines)

    def __write_class(self, jclass):
        self.__writelines(str(jclass), self.f)

    def __write_header(self, jclass):
        self.__writelines(jclass.get_header(), self.f)

    def __write_footer(self, jclass):
        self.__writelines(jclass.get_footer(), self.f)

    def __write_body(self, jclass):
        self.__writelines(jclass.get_body(), self.f)

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
