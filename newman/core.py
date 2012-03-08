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

from argument import Argument
from decorators import task
from . import get_version

pp = pprint.PrettyPrinter(indent=4)

VERSION = get_version()

# setting globals
DEBUG = False
ROOT_PATH = os.getcwd()
ABS_TASK_PATH = os.path.join(ROOT_PATH, 'lib', 'tasks')
TASK_PATH = os.path.join('lib', 'tasks')
NEWMAN_FILE = "%s/NewmanFile" % ROOT_PATH
NEWMAN_CONFIG = "%s/.newmanrc" % ROOT_PATH

excluded_modules = ['__init__.py', '.pyc', '.pyo', '.svn', '.swp']

def load_task_modules(subparser):
    """Loads task modules from the first detected path from TASK_PATHS"""
    # first let's import the task group modules
    task_modules = []
    for filename in os.listdir(ABS_TASK_PATH):
        if any(map(lambda x: x in filename, excluded_modules)):
            # ignore any files that contain an entry from excluded modules
            continue
        (mod_name, ext) = os.path.splitext(filename)
        task_modules.append(mod_name)
        debug("loading task module: {0}".format(mod_name))
  
    debug("Loading Task Path: {0}".format(TASK_PATH))
    ## change the local tasks module either from a script importing newman 
    # or a dir that you are running newman in.
    mod_prefix = TASK_PATH.replace('/', '.')

    for mod in task_modules:
        __import__('%s.%s' % (mod_prefix, mod))

    # now that they are all in the tasks namespace, let's build our task hash
    tasks = {}
    for mod_name in task_modules:
        mod_parser = None
        mod = sys.modules['%s.%s' % (mod_prefix, mod_name)]

        # setup module parser
        mod_parser = subparser.add_parser(mod_name, help=mod.__doc__)
        mod_task_parser = mod_parser.add_subparsers(
          title='Tasks under %s' % mod_name,
          help='The following are valid task commands',
          dest='task'
        )
    
        # building a hash of task groups and tasks
        #tasks[mod_name] = {}
        tasks = {}
        for task_name, task_obj in inspect.getmembers(mod, inspect.isfunction):
            debug("TASK Name: %s" % task_name)
            if task_obj.func_dict.get('task'):
                # create a task
                task_parser = mod_task_parser.add_parser(
                  task_name,
                  help=task_obj.__doc__
                )
    
                # add task arguments
                add_task_arguments(task_parser, task_obj)
                task_parser.set_defaults(func=task_obj)

## NOTE: This is the start to refactor some of the above
#def add_tasks(mod_task_parser, task_name, task_obj):
#    """docstring for add_tasks"""
#    if task_obj.func_dict.get('task'):
#        # create a task
#        task_parser = mod_task_parser.add_parser(task_name, help=task_obj.__doc__)
#
#        # add task arguments
#        add_task_arguments(task_parser, task_obj)
#        task_parser.set_defaults(func=task_obj)

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

## TODO: still need to add the newmanfile feature
def load_task(parser):
    for task_name, task_obj in inspect.getmembers(tm, inspect.isfunction):
        debug("Loading Task Name: %s" % task_name)
        #pp.pprint(dir(task_obj))
        if task_obj.func_dict.get('task'):
            # create a task
            task_parser = mod_task_parser.add_parser(
                task_name,
                help=task_obj.__doc__
            )

            # add task arguments
            add_task_arguments(task_parser, task_obj)
            task_parser.set_defaults(func=task_obj)

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

def config_parser(parser):
    # main parser arguments
    # this feature is down the roadmap
    #parser.add_argument('-t', '--tasks', type=bool, default=True,
    #                    help="Lists all the tasks available.")
    # add our top-level arguments to the main parser
    parser.add_argument('-v', '--version',
                        action='version', help='show version and exit',
                        version='%%(prog)s %s' % VERSION)
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
        tasks = load_task_modules(subparser)
        # TODO: I think want to load the tasks first before configuring argparse
        #add_modules_arguments(tasks)

def run(script_path, task_path, version=None):
    global TASK_PATH
    global ROOT_PATH
    global ABS_TASK_PATH
    global VERSION

    # setting paths
    TASK_PATH = task_path
    ROOT_PATH = script_path
    ABS_TASK_PATH = os.path.join(ROOT_PATH, TASK_PATH)
    if version:
        VERSION = version

    main()

def main():
    global DEBUG
    debug("Running newman in: {0}".format(ROOT_PATH))
    
    # add the root path to the sys path
    if ROOT_PATH not in sys.path:
        sys.path.insert(0, ROOT_PATH)
    
    if os.path.isfile(NEWMAN_CONFIG):
        read_config()
    
    parser = argparse.ArgumentParser()
    config_parser(parser)
    args = parser.parse_args()
    
    args.func(args)
