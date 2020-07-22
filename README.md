# JsonPojoCreator
## Build your custom Java Pojo starting from a json object!

JsonPojoCreator helps you to create a Java class representing the structure of a given JSON object.

You just need to run JsonPojoCreator and you will find a class (named as you have specified, in the package that 
you have specified) with:  
1. all fields those had been found in the JSON object. The field name will be the same as the JSON object property name, 
but using CamelCase notation. So you are recommended to run JsonPojoCreator using the `-q --json_property` option. So 
JsonPojoCreator will use the @JsonProperty annotation over every attribute, allowing you to have a simple java object 
to json string (and vice versa) conversion.  
Using option `-i, --jsonignore` you can specify a comma separated list of fields that must be annoted with @JsonIgnore 
annotation.  
2. every field will provided of getter and setter method those can be replaced (using `-l, --lombock` option) by the 
proper lombock annotation.
3. same as point 2. is valid for default constructor (0 arguments) and the all arguments constructor.  

In addition to the already explained command line options you can use the option `-I, --inner` to build inner static  
classes, instead of external files with their own public classes, for the internal JSON objects.

Another interesting option is the `-e, --exclude` option that will allow you to completely ignore the JSON properties 
specified in the comma separated list (These properties won't appear in Java class).  

A really useful option is the `-f, --conf` option. It allows you to use a conf file, written in JSON format (yes, pojoc 
can translate this in a Pojo too :smirk:). The JSON object can contain the same options specified in help message (except  
for `-h`, `-v` and `-f`) with the same semantic. The main advantages of use a JSON conf file rather than command line
arguments are that you can quickly change it to build different Java entity based on different JSON schemes.
In addition you can specify an option (through a property named "additionalOptions"). The value of "additionalOptions" is a JSON 
object that represents a key-value map. The properties of this map can be:
- The names of fields that in JSON scheme have another JSON object as value. The value mapped to this key will be the 
name of the class representing the JSON object.
- "superclass" (type: string) which allows you to specify the superclass of your main Pojo
- "serializable" (type: boolean) make **ALL** the created classes serializable (with the _implements_ construct and a 
_static final long serialVersionUID_) 
- "builder" (type: boolean) add a builder to every created class (using @Builder annotation if lombock is used) (TBD)

### Coming soon
1. Possibility to decide superclass of your pojo
2. More libraries (as Gson, javax and so on) to allow you to manipulate JSON and Java object as you prefer
3. The overriding of toString, equals and hashCode methods
4. A simple GUI to make you faster to build your Java pojo