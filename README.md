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
specified in the comma separated list.

### Coming soon
1. Possibility to decide superclass/superinterface of your pojo
2. More libraries (as Gson, javax and so on) to allow you to manipulate JSON and Java object as you prefer
3. The overridin of toString, equals and hashCode methods
4. A simple GUI to make you faster to build your Java pojo