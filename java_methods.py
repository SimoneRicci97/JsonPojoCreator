class Method:
    def __init__(self, jclass, method_name, return_type, parameters, public=True, indlevel=0):
        self.jclass = jclass
        self.method_name = method_name
        self.return_type = return_type
        self.parameters = parameters
        self.public = public
        self.indlevel = indlevel
        self.statements = []
        self.throwing = []

    def get_signature(self):
        signature = '\t' * self.indlevel + '\tpublic ' if self.public else '\tprivate '
        signature += (f"{self.return_type} " if self.return_type is not None else '')
        signature += f"{self.method_name}("
        for a in self.parameters:
            signature += f"{a.type} {a.name}"
            signature += ', ' if a != self.parameters[-1] else ''
        signature += ') '
        if len(self.throwing) > 0:
            signature += 'throws '
            for e in self.throwing:
                signature += e
                signature += ', ' if e != self.throwing[-1] else ''
        signature += '{\n'
        return signature

    def strcall(self, arguments):
        strc = f"{self.method_name}("
        for a in arguments:
            strc += a
            strc += ', ' if a != arguments[-1] else ''
        strc += ')'
        return strc

    def get_body(self):
        body = ''
        for stm in self.statements:
            body += '\t' * self.indlevel + '\t\t' + stm + '\n'
        return body + '\t' * self.indlevel + '\t}\n\n'

    def __str__(self):
        return self.get_signature() + self.get_body()

    def add_paramter(self, p):
        self.parameters.append(p)



class Constructor(Method):
    def __init__(self, jclass, classname, parameters, indlevel=0):
        super().__init__(jclass, classname, None, parameters, indlevel=indlevel)
        for a in self.parameters:
            self.statements.append(f"this.{a.name} = {a.name};")

    def add_field(self, field):
        self.parameters.append(field)
        for a in self.parameters:
            self.statements.append(f"this.{a.name} = {a.name};")

    def strcall(self, arguments):
        return 'new ' + super().strcall(arguments)


class DefaultConstructor(Constructor):
    def __init__(self, jclass, classname, indlevel=0, public=True):
        super().__init__(jclass, classname, [], indlevel=indlevel)
        self.public = public
        self.statements.append('super();')

    def add_field(self, field):
        pass

    def strcall(self, arguments):
        return super().strcall(arguments)

class Getter(Method):
    def __init__(self, jclass, field, prefix='get', indlevel=0):
        super().__init__(jclass, f"{prefix}{field.name.capitalize()}", field.type, [], indlevel=indlevel)
        self.field = field
        self.statements.append(f"return this.{self.field.name};")


class Setter(Method):
    def __init__(self, jclass, field, prefix='set', indlevel=0):
        super().__init__(jclass, f"{prefix}{field.name.capitalize()}", jclass.name, [field], indlevel=indlevel)
        self.field = field
        self.statements.extend([f"this.{self.field.name} = {self.field.name};", "return this;"])


class StaticMethod(Method):
    def __init__(self, jclass, method_name, return_type, parameters, public=True, indlevel=0):
        super().__init__(jclass, method_name, return_type, parameters, public=public, indlevel=indlevel)

    def get_signature(self):
        signature = '\t' * self.indlevel + '\tpublic static ' if self.public else '\tprivate '
        signature += (f"{self.return_type} " if self.return_type is not None else '')
        signature += f"{self.method_name}("
        for a in self.parameters:
            signature += f"{a.type} {a.name}"
            signature += ', ' if a != self.parameters[-1] else ''
        signature += ') '
        if len(self.throwing) > 0:
            signature += 'throws '
            for e in self.throwing:
                signature += e
                signature += ', ' if e != self.throwing[-1] else ''
        signature += '{\n'
        return signature


class BuilderMethod(Method):
    def __init__(self, jclass, buildedclass, indlevel):
        super().__init__(jclass, 'build', buildedclass.name, [], indlevel=indlevel)

    def get_body(self):
        self.statements.append("return " + self.jclass.extclass.all_args_constructor.strcall(
            [field.name for field in self.jclass.fields]) + ';\n')
        return super().get_body()