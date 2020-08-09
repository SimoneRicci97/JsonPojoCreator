# JsonPojoCreator
## Build your custom Java Pojo starting from a json object!

JsonPojoCreator helps you to create a Java class representing the structure of a given JSON object.

You just need to run **pojoc** and you will find a class (named as you have specified, in the package that 
you have specified) with:  
1. all fields those had been found in the JSON object. The field name will be the same as the JSON object property name, 
but using CamelCase notation. So you are recommended to run JsonPojoCreator using the `-q, --json_property` option 
(see below). 
2. every field will provided of getter and setter method those can be replaced (using `-l, --lombock` option) by the 
proper lombock annotation.
3. same as point 2. applies to default constructor (0 arguments) and the all arguments constructor.  

N.B.: for setters methods **pojoc** use the chain pattern. It's so. You can change it? No. Is there an option to build 
setter method with no chain pattern? No. If you don't like chain pattern you deserve to build your pojo with your own 
hands.

## pojoc options
- `-h, --help` do you really need this option explained?
- `-j, --json` specify the file where read the JSON object or, if you have sins to be punished for, you can specify  
the json by command line.
- `-c, --classname` specify the class name of your main Pojo. If none **pojoc** will use the file name.
- `-v, --version` like all the noteworthy tools, print the version of **pojoc**
- `-l, --lombock` use lombock annotations instead of getter/setter and constructors
- `-q, --json_property` because of **pojoc** translate JSON properties name in CamelCase notation this option add
the `@JsonProperty("<json-property>")` over each class field
- `-e, --exclue` a comma separated list which specifies the JSON properties those must not appear in created Pojos
- `-i, --jsonignore` will add `@JsonIgnore` annotation over fields specified in comma separated list
- `-p, --package` Path where you will find java class/es. The default value is '.'. It must contain the subpath
'src/main/java/' and the next portion will represent the package name for the class/es
- `-I, --inner` use innser classes instead of build a Java file for each created class  
- `-s, --primitive` use primitive types


## Configuration file
A really useful option is the `-f, --conf` option. It allows you to use a conf file, written in JSON format (yes, pojoc 
can translate this in a Pojo too :wink:). The JSON object can contain the same options specified in help message (except 
for `-h`, `-v` and `-f`) with the same semantic. The main advantages of use a JSON conf file rather than command line
arguments are that you can quickly change it to build different Java entity based on different JSON schemes. And at the
same time it's quickly reusable to translate different Json schemes using the same options.
In addition you can specify a customizable option (through a property named "additionalOptions").  
The value of "additionalOptions" is a JSON object that represents a key-value map. The properties of this map can be:
- "alternativeNames" is a string to string map whose names of fields that in JSON scheme have another JSON object as 
value. The value mapped to this key will be the name of the class representing the JSON object.
- "superclass" (type: string) which allows you to specify the superclass of your main Pojo
- "serializable" (type: boolean) make **ALL** the created classes serializable (with the _implements_ construct and a 
_static final long serialVersionUID_) 
- "hideDefaulConstructor" (type: boolean) make default constructors of your Pojos private. 
- "builder" (type: boolean) add a builder to every created class (using @Builder annotation if lombock is used) 
- "IDontBelieve" (type: boolean) if true create a java main which instantiate an object of your main pojo and serialize 
it, printing the json string to stdout 


### Don't you belienìve in me?
If so, I suggest you to abilitate the option _IDontBelieve_. At the end of the building pojoc will create a main class with the code to instantiate and serialize the created Pojo.
The code will be executed and the JSON will be printed to the stdout, so you can check the differences with the source 
JSON. Little spoiler: **there won't be** :smirk:.  
Yes, this feature is just for developer of little faith.  
N.B.: _java_ and _javac_ must be runnable on your pc. 

### Coming soon
- More libraries (as Gson, javax and so on) to allow you to manipulate JSON and Java object as you prefer
- The overriding of toString, equals and hashCode methods
- A simple GUI to make you faster to build your Java pojo