"""
newman

Created by Matt O'Donnell on 2010-11-24.
Copyright (c) 2011 AdKeeper, Inc. All rights reserved.
"""

import imp
import errno
import argparse
import inspect
import os
import sys
import pprint

from . import get_version

pp = pprint.PrettyPrinter(indent=4)


# setting globals
DEBUG = False
ROOT_PATH = os.getcwd()
TASK_PATH = os.path.join('lib', 'tasks')
ABS_TASK_PATH = os.path.join(ROOT_PATH, TASK_PATH)
NEWMAN_FILE = "%s/NewmanFile" % ROOT_PATH
NEWMAN_CONFIG = "%s/.newmanrc" % ROOT_PATH

EXCLUDED_MODULES = ['__init__.py', '.pyc', '.pyo', '.svn', '.swp']


def find_task_modules():
    """Find the task modules from the file system"""

    task_modules = []
    for filename in os.listdir(ABS_TASK_PATH):
        # ignore any files that contain an entry from excluded modules
        if any(map(lambda x: x in filename, EXCLUDED_MODULES)):
            continue
        (mod_name, ext) = os.path.splitext(filename)
        task_modules.append(mod_name)
        debug("loading task module: {0}".format(mod_name))
    return task_modules


def import_task_modules():
    """Loads task modules from the first detected path from TASK_PATHS"""
    task_modules = find_task_modules()
    # first let's import the task group modules
    debug("Loading Task Path: {0}".format(TASK_PATH))
    ## change the local tasks module either from a script importing newman 
    # or a dir that you are running newman in.
    mod_prefix = TASK_PATH.replace('/', '.')

    for mod in task_modules:
        __import__('%s.%s' % (mod_prefix, mod))

    return task_modules


def build_mod_parsers(subparser, task_modules):
    # now that they are all in the tasks namespace, let's build our task hash
    parsers = {}
    mod_prefix = TASK_PATH.replace('/', '.')
    for mod_name in task_modules:
        mod = sys.modules['%s.%s' % (mod_prefix, mod_name)]

        # setup module parser
        mod_parser = subparser.add_parser(mod_name, help=mod.__doc__)
        mod_task_parser = mod_parser.add_subparsers(
            title='Tasks under %s' % mod_name,
            help='The following are valid task commands',
            dest='task'
        )

        # building a hash of task groups and tasks
        parsers[mod_name] = {
            'mod_obj': mod,
            'mod_parser': mod_parser,
            'task_parser': mod_task_parser
        }
        load_tasks(mod, mod_task_parser)
    return parsers


def load_tasks(mod_obj, mod_task_parser):
    """doc string for task parser"""
    for task_name, task_obj in inspect.getmembers(mod_obj, inspect.isfunction):
        debug("TASK Name: %s" % task_name)
        task_parser = build_task_parser(mod_task_parser, task_name, task_obj)
        return task_parser


## NOTE: This is the start to refactor some of the above
def build_task_parser(mod_task_parser, task_name, task_obj):
    """docstring for add_tasks"""
    if task_obj.func_dict.get('task'):
        # create a task
        task_parser = mod_task_parser.add_parser(task_name, help=task_obj.__doc__)

        # add task arguments
        add_task_arguments(task_parser, task_obj)
        task_parser.set_defaults(func=task_obj)
        return task_parser
    else:
        return False


def add_task_arguments(task_parser, task_obj):
    for arg in task_obj.options:
        kwargs = arg.parser_args()
        if arg.datatype == bool:
            kwargs["action"] = 'store_true'
            del kwargs['required']
            del kwargs['default']
            del kwargs['type']
        elif arg.datatype == list:
            del kwargs['default']
            del kwargs['type']
            kwargs.setdefault("nargs", "+")
        else:
            kwargs["action"] = 'store'
        task_parser.add_argument("--%s" % arg.name, **kwargs)


def load_newman_file():
    tm = imp.new_module('tasks')
    tm.__file__ = NEWMAN_FILE
    try:
        execfile(filename, tm.__dict__)
        return(tm)
    except IOError, e:
        if e.errno in (errno.ENOENT, errno.EISDIR):
            return False
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return True


def read_config():
    global ABS_TASK_PATH
    global TASK_PATH
    # create a dict to hold the config
    cfg = dict()
    
    # set abslute path to config file
    filename = os.path.join(ROOT_PATH, NEWMAN_CONFIG)
    try:
        execfile(filename, cfg)
        if cfg.get('task_path'):
            TASK_PATH = cfg["task_path"]
            ABS_TASK_PATH = os.path.join(ROOT_PATH, cfg["task_path"])
        return True
    except IOError, e:
        if e.errno in (errno.ENOENT, errno.EISDIR):
            return False
        e.strerror = 'Unable to load configuration file (%s)' % e.strerror
        raise
    return True


def debug(msg):
    """docstring for debug"""
    if DEBUG:
        print msg

def config_parser():
    parser = argparse.ArgumentParser()
    # main parser arguments
    # this feature is down the roadmap
    #parser.add_argument('-t', '--tasks', type=bool, default=True,
    #                    help="Lists all the tasks available.")
    # add our top-level arguments to the main parser
    parser.add_argument('-v', '--version',
                        action='version', help='show version and exit',
                        version='%%(prog)s %s' % get_version())
    # TODO: setup debugging
    #parser.add_argument('-d', '--debug', action='store_true', help='Print debug')
    
  
    if os.path.isfile(NEWMAN_FILE):
        task_mod = load_newman_file()
        # TODO: configure argparse after tasks have been loaded
        load_task(task_mod)
    elif os.path.isdir(ABS_TASK_PATH):
        debug("Loading TASKS from: {0}".format(ABS_TASK_PATH))
        # we are going to create a subparser for each task module
        subparser = parser.add_subparsers(title='Task Modules',
                                          description='Namespaces for the different sub tasks.',
                                          dest='task_module')
        task_modules = import_task_modules()
        build_mod_parsers(subparser, task_modules)
    return parser


def run(script_path, task_path, version=None):
    global TASK_PATH
    global ROOT_PATH
    global ABS_TASK_PATH

    # setting paths
    TASK_PATH = task_path
    ROOT_PATH = script_path
    ABS_TASK_PATH = os.path.join(ROOT_PATH, TASK_PATH)

    main()


def main():
    global DEBUG
    debug("Running newman in: {0}".format(ROOT_PATH))
    
    # add the root path to the sys path
    if ROOT_PATH not in sys.path:
        sys.path.insert(0, ROOT_PATH)
    
    if os.path.isfile(NEWMAN_CONFIG):
        read_config()
    
    parser = config_parser()
    args = parser.parse_args()
    args.func(args)
