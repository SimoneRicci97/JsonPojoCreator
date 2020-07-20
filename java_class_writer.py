

def get_getter(field_type, fieldname, indlevel=0):
    return '\t' * indlevel + f'public {field_type} get{fieldname.capitalize()}()' + '{\n' + \
           '\t' * indlevel + f'\treturn this.{fieldname};\n' + \
           '\t' * indlevel + '}\n\n'


def get_setter(ret_type, fieldname, indlevel=0):
    return '\t' * indlevel + f"public void set{fieldname.capitalize()}({ret_type} {fieldname}) " + '{\n' + \
           '\t' * indlevel + f"\tthis.{fieldname} = {fieldname};\n" + \
           '\t' * indlevel + '}\n\n'


def get_class_header_name(static, classname, indlevel=0):
    return '\t' * indlevel + f"public{static} class {classname}" + ' {\n'


class JavaClass:
    def __init__(self, classname, package, extclass=None):
        self.name = classname
        self.indlevel = 1 if extclass is not None else 0
        self.package = package
        self.classname = get_class_header_name(' static' if extclass is not None else '', classname, self.indlevel)
        self.innerclasses = []
        self.classannotations = []
        self.imports = []
        self.fields = []
        self.method = []
        self.extclass = extclass

    def add_annotations(self, anns):
        self.classannotations.extend(anns)
        self.classannotations.append('\n')

    def add_field(self, name, fieldtype, jsonproperty=None, jsonignore=False, getter=False, setter=False):
        field_info = []

        if fieldtype == 'BigDecimal':
            self.add_import('import java.math.BigDecimal;')

        if jsonproperty is not None:
            field_info.append('\t@JsonProperty(\"{}\")\n'.format(jsonproperty))
            self.add_import('import com.fasterxml.jackson.annotation.JsonProperty;\n')

        if jsonignore:
            field_info.append('\t@JsonIgnore\n')
            self.add_import('import com.fasterxml.jackson.annotation.JsonIgnore;\n')

        field_info.append(f'\tprivate {fieldtype} {name};')

        for info in field_info:
            self.fields.append(info)
        self.fields.append('\n\n')

        if getter:
            self.method.append(get_getter(fieldtype, name, self.indlevel))

        if setter:
            self.method.append(get_setter(fieldtype, name, self.indlevel))

    def add_import(self, importrow):
        if self.extclass is not None and self.extclass.imports.count(importrow) == 0:
            self.extclass.imports.append(importrow)
        elif self.imports.count(importrow) == 0:
            self.imports.append(importrow)

    def __str__(self):
        self_str = ''
        if self.extclass is None:
            self_str += f'package {self.package};\n\n'
            self_str += ''.join(self.imports)
        self_str += '\n' + ''.join(['\t' * self.indlevel + ann for ann in self.classannotations])
        self_str += self.classname
        self_str += '\n'.join(['\t' * self.indlevel + str(ic) for ic in self.innerclasses])
        self_str += '\n'
        self_str += ''.join(['\t' * self.indlevel + f for f in self.fields])
        self_str += '\n'.join(['\t' * self.indlevel + m for m in self.method])
        self_str += '\t' * self.indlevel + '}\n'
        return self_str


class JavaClassWriter:
    def __init__(self, javaclass):
        path = 'src/main/java/' + javaclass.package.replace('.', '/')
        self.path = f'{path}/{javaclass.name}.java'
        self.javaclass = javaclass

    @staticmethod
    def __writelines(lines, f):
        if f is not None:
            f.write(lines)
        else:
            print(lines)

    def write(self):
        f = None
        if self.path is not None:
            f = open(self.path, 'w')
        self.__writelines(str(self.javaclass), f)
