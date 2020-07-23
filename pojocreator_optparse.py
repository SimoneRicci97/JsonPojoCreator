import optparse
import json
import sys

from json2java_mapper import map_json_name

ERR_BAD_ARGS = 2

CONF_FILE = 'pojobuilder.conf.json'


def set_parse_option():
    parser = optparse.OptionParser(description='Copy/paste tool')
    parser.add_option('-j', '--json', default=None, dest='json', help='json to transform in java class')
    parser.add_option('-c', '--classname', default=None, dest='classname', help='Name of java class')
    parser.add_option('-v', '--version', default=False, action='store_true', dest='version', help='print version')
    parser.add_option('-l', '--lombock', default=False, action='store_true', dest='lombock',
                      help='generate lombock annotations')
    parser.add_option('-q', '--jsonproperty', default=False, action='store_true', dest='jsonproperty',
                      help='Add @JsonProperty annotations')
    parser.add_option('-e', '--exclude', default=None, dest='exclude', help='Exclude json fields from java class')
    parser.add_option('-i', '--jsonignore', default=None, dest='jsonignore',
                      help='Comma separeted list. Add @JsonIgnore annotations over specified fields')
    parser.add_option('-p', '--package', default=None, dest='package',
                      help='Path where you will find java class/es. The default value is \'.\'. '
                           'It must contain the subpath \'src/main/java/\' and the next portion will represent '
                           'the package name for the class/es')
    parser.add_option('-I', '--inner', default=False, action='store_true', dest='inner', help='Use inner classes')
    parser.add_option('-s', '--primitive', default=False, action='store_true', dest='primitive',
                      help='Use primitive types')
    parser.add_option('--ignore', default=None, dest='ignore',
                      help='Comma separated list. json fields in list will be ignored building java class')
    parser.add_option('-f', '--conf', default=False, dest='conf', action='store_true',
                      help=f"Load cli option from the \'{CONF_FILE}\' file.")

    return parser


def usage(parser=None, excode=0):
    if parser is None:
        parser = set_parse_option()
    parser.print_help()
    sys.exit(excode)


def bad_args_error(errtext):
    print(errtext, end='\n\n')
    usage(excode=ERR_BAD_ARGS)


def check_csl_arg(arg):
    if arg is not None and type(arg) == str:
        return arg.split(',')
    elif arg is not None and type(arg) != list:
        return None
    else:
        return []


def load_json_options():
    with open(CONF_FILE, 'r') as f:
        json_opt = json.load(f)

    options = optparse.Values()
    for k, v in json_opt.items():
        options.ensure_value(k, v)

    options.version = False

    return options


def pojo_creator_argparse():
    parser = set_parse_option()
    options, args = parser.parse_args()

    if options.version:
        return options

    if options.conf:
        options = load_json_options()

    if options.json is None:
        bad_args_error("json (-j, --json) arg is required")

    if options.classname is None:
        options.classname = map_json_name(options.json.split('/')[-1].split('.')[0], isclass=True)

    options.classname = map_json_name(options.classname, isclass=True)

    options.exclude = check_csl_arg(options.exclude)
    if options.exclude is None:
        bad_args_error('exclude mast be a comma separated list id running by command line, or a JSON array '
                       'if running by conf file')

    options.jsonignore = check_csl_arg(options.ignore)
    if options.jsonignore is None:
        bad_args_error('jsonignore mast be a comma separated list id running by command line, or a JSON array '
                       'if running by conf file')

    if options.package is not None:
        java_subpath = 'src/main/java'

        if options.package[-1] == '/':
            options.package = options.package[:-1]
        print(options.package)
        if options.package.count(java_subpath) > 0:
            options.path = options.package
            options.package = options.package[options.package.index(java_subpath) + len(java_subpath) + 1:] \
                .replace('/', '.')
        else:
            bad_args_error(f"package must contain the subpath \'{java_subpath}\'")
    else:
        options.path = '.'

    options.ignore = check_csl_arg(options.ignore)
    if options.ignore is None:
        bad_args_error('ignore must be a comma separated list id running by command line, or a JSON array '
                       'if running by conf file')

    return options
