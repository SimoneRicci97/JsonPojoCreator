class Method:
    def __init__(self, jclass, method_name, return_type, parameters, public=True, indlevel=0):
        self.jclass = jclass
        self.method_name = method_name
        self.return_type = return_type
        self.parameters = parameters
        self.public = public
        self.indlevel = indlevel

    def get_signature(self):
        signature = '\t' * self.indlevel + '\tpublic ' if self.public else '\tprivate '
        signature += (f"{self.return_type} " if self.return_type is not None else '')
        signature += f"{self.method_name}("
        for a in self.parameters:
            signature += f"{a.type} {a.name}"
            signature += ', ' if a != self.parameters[-1] else ''
        signature += ') {\n'
        return signature

    def strcall(self, arguments):
        strc = f"{self.method_name}("
        for a in arguments:
            strc += f"{a.name}"
            strc += ', ' if a != arguments[-1] else ''
        strc += ');\n'
        return strc

    def get_body(self):
        return '\t' * self.indlevel + '\t}\n\n'

    def __str__(self):
        return self.get_signature() + self.get_body()


class DefaultConstructor(Method):
    def __init__(self, jclass, classname, indlevel=0, public=True):
        super().__init__(jclass, classname, None, [], indlevel=indlevel, public=public)

    def add_field(self, field):
        pass

    def get_body(self):
        return '\t' * self.indlevel + '\t\tsuper();\n' + super().get_body()

    def strcall(self, arguments):
        return 'new ' + super().strcall(arguments)


class Constructor(DefaultConstructor):
    def __init__(self, jclass, classname, indlevel=0):
        super().__init__(jclass, classname, indlevel=indlevel)

    def add_field(self, field):
        self.parameters.append(field)

    def get_body(self):
        self_str = ''
        for a in self.parameters:
            self_str += '\t' * self.indlevel + f"\t\tthis.{a.name} = {a.name};\n"
        self_str += '\t' * self.indlevel + '\t}\n\n'
        return self_str


class Getter(Method):
    def __init__(self, jclass, field, prefix='get', indlevel=0):
        super().__init__(jclass, f"{prefix}{field.name.capitalize()}", field.type, [field], indlevel=indlevel)
        self.field = field

    def get_body(self):
        return '\t' * self.indlevel + f"\t\treturn this.{self.field.name};\n" + super().get_body()


class Setter(Method):
    def __init__(self, jclass, field, prefix='set', indlevel=0):
        super().__init__(jclass, f"{prefix}{field.name.capitalize()}", jclass.name, [field], indlevel=indlevel)
        self.field = field

    def get_body(self):
        self_str = '\t' * self.indlevel + f"\t\tthis.{self.field.name} = {self.field.name};\n"
        self_str += '\t' * self.indlevel + "\t\treturn this;\n"
        self_str += super().get_body()
        return self_str


class BuilderMethod(Method):
    def __init__(self, jclass, buildedclass, indlevel):
        super().__init__(jclass, 'build', buildedclass.name, [], indlevel=indlevel)

    def get_body(self):
        self_str = '\t' * self.indlevel + '\t\treturn '
        self_str += self.jclass.extclass.all_args_constructor.strcall(self.jclass.fields)
        return self_str + super().get_body()