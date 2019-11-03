#!env python3
""" Helper command line utility for Docker commands

TODO:
* how to pass arbitrary arguments through to sub functions


"""
# NOTE: only use standard library so it's a bit easier to use
import os
import sys
import argparse
import logging
import datetime


PROJECT_DIR = os.path.dirname(__file__)


# ########################################################################### #
# GLOBALS
# ########################################################################### #

root_parser = argparse.ArgumentParser()
subparsers = root_parser.add_subparsers()

try:
    import argcomplete
    argcomplete.autocomplete(root_parser)
except ImportError:
    pass

# ########################################################################### #
# HELPERS
# ########################################################################### #

KEYWORD_ALLOW_UNKNOWN = 'unknown_args'
KEYWORD_SUBPROCESS_COMMAND = 'subprocess_command'


def popattr(ns, name, default=None):
    """ Remove an attribute from an object """
    # hmmmm, may want them to actually be immutable. idk
    if hasattr(ns, name):
        value = getattr(ns, name)
        delattr(ns, name)
        return value
    else:
        return default


def pass_unknown_args(subparser):
    """ For the parser, set that unknown variables are allowed
    """
    # hacking this a bit to use the defaults and namespace
    # _could_ write this better.
    subparser.set_defaults(**{KEYWORD_ALLOW_UNKNOWN: None})
    return subparser


def parse_args(parser):
    """ Parse arguments. This checks to see if I wanted to allow unknown
    arguments to be passed through or not. If I do then they're added to the
    namespace passed forward.
    """
    pargs, unknown = parser.parse_known_args()
    if hasattr(pargs, KEYWORD_ALLOW_UNKNOWN):
        setattr(pargs, KEYWORD_ALLOW_UNKNOWN, unknown)
    elif len(unknown):
        parser.error('unrecognized arguments: {}'.format(' '.join(unknown)))
    return pargs


def config_logging(level):
    logging.basicConfig(
        stream=sys.stdout,
        format='%(asctime)s (%(levelname)s): %(message)s',
    )
    loglevel = (level or 'info').upper()
    logging.root.setLevel(loglevel)


def process_global_arguments(pargs):
    """ Take the parsed arguments namespace and process some global attributes
    """
    # TODO: could make this immutable function, but maybe not? idk

    # logging
    level = popattr(pargs, 'log')
    config_logging(level)


def as_subparser(func):
    """ This is a decorator which wraps a function and adds it as subparser


    Example:

        @as_subparser
        def foo(x, y):
            \"\"\" This is a summary


            This is a bunch of info about foo
            it goes on
            and on...
            and on...
            and on...
            \"\"\"
            print('win', x, y)
        foo.add_argument('-x', type=int, default=1)
        foo.add_argument('y', type=float)

        main()
    """
    # configure the subparser using the function doc
    doc_lines = func.__doc__.split('\n')
    summary = doc_lines[0].strip()
    description = '\n'.join(doc_lines[1:])
    subparser = subparsers.add_parser(
        func.__name__,
        description=description,
        help=summary,
        formatter_class=argparse.RawTextHelpFormatter,
    )

    def subparser_command(pargs):
        args = list(pargs._get_args())
        kws = dict(pargs._get_kwargs())
        return func(*args, **kws)

    subparser.set_defaults(
        **{KEYWORD_SUBPROCESS_COMMAND: subparser_command},
    )
    return subparser


def execute_bash_command(*cmd):
    command = ' '.join(cmd)
    logging.info(command)
    os.system(command)


# ########################################################################### #
# COMMANDS
# ########################################################################### #

root_parser.add_argument(
    '--log',
    help='set the logging level: CRITICAL, INFO, ERROR, DEBUG, WARNING',
)


# --------------------------------------------------------------------------- #
#       General Commands
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
@as_subparser
def add_cmd_to_path():
    """ Add cmd command to your terminal

    cmd is a command to help you with common tasks. It can be excuted directly
    with `./dapi <shortcut>`. However, it is often more convient to shortent
    to `dapi <shortcut>` and make accessible in subfolders. There are several
    methods to achieve this though, including:

    * Create global symlink, may require sudo

        ln -s /{project_path}/dapi /usr/local/bin/dapi

    * (Default) Create python relative symlink. This is the preferred method
        but does require being within a python virtualenvironment. That's what
        this command will do by default.

        ln -s /{project_path}/dapi /{python_virtualenv_path}/bin/dapi

    * Add to your path (could add to ~/.bash_profile)

        export PATH=${PATH}:/{project_path}/dapi

    * Create an alias (could add to ~/.bash_profile)

        alias dapi=/{project_path}/dapi
    """

    # Check if i'm in a virutalenvironment because I want it explicitly
    # in the virtualenvironment
    real_prefix = getattr(sys, 'real_prefix', None)
    base_prefix = getattr(sys, 'base_prefix', None)
    prefix = getattr(sys, 'prefix', None)
    in_venv = (
        real_prefix is not None or
        base_prefix is not None and
        base_prefix != prefix
    )
    if not in_venv:
        raise Exception(
            'Not currently in virualenvironment.\n\n'
            'sys.real_prefix={}\n'
            'sys.base_prefix{}\n'
            'sys.prefix={}'
            .format(real_prefix, base_prefix, prefix)
        )
    venvdir = os.path.abspath(prefix)
    venv = os.path.basename(venvdir)
    logging.info('Inside virtualenv "{}" at {}'.format(venv, venvdir))

    # location of this source command
    source = os.path.abspath(__file__)
    command = os.path.basename(source)

    # destination for the symlink
    symdir = os.path.join(venvdir, 'bin')
    symlink = os.path.join(symdir, command)

    # execute the command and check the result workedd
    execute_bash_command('ln', '-s', source, symlink)
    with os.popen('which {}'.format(command)) as p:
        resp = p.read()
    if resp.rstrip() != symlink:
        raise Exception('symlink failed, {}'.foramt(resp))

    # closing thoughts
    logging.info('Link created, remove with `rm {}`'.format(symlink))
    logging.info(
        'You can now use `{}` command anywhere '
        'as long as you\'re in the {} virtualenv'
        .format(
            command, venv,
        )
    )

# --------------------------------------------------------------------------- #
#       Web Commands
# --------------------------------------------------------------------------- #

# --------------------------------------------------------------------------- #
@as_subparser
def bash():
    """ This starts a bash shell on the web server
    """
    execute_bash_command(
        'docker-compose run web bash'
    )

# --------------------------------------------------------------------------- #
#       Database Commands
# --------------------------------------------------------------------------- #

# ---------------------------------------------------------------------------
@as_subparser
def psql():
    """ Connect to the database service using psql
    """
    execute_bash_command(
        'docker-compose exec db',
        # note: need the single quotes to use environment variables
        "bash -c 'psql -U $POSTGRES_USER -d $POSTGRES_DB'",
    )


@as_subparser
def db_script(filename):
    """ Connect to the database service using psql
    """
    fn = os.path.basename(filename)
    fp = os.path.join('/opt/postgres/scripts', fn)
    execute_bash_command(
        'docker-compose exec db',
        # note: need the single quotes to use environment variables
        f"bash -c 'psql -U $POSTGRES_USER -d $POSTGRES_DB -f {fp}'",
    )


db_script.add_argument(
    'filename',
    help=(
        'Filename of the script, '
        'can use path `postgres/scripts/0000_init.psql`'
    )
)


@as_subparser
def db_backup():
    """ Backup the database
    """
    path = 'postgres/untracked_backups'

    outdir_host = os.path.join(PROJECT_DIR, path)
    if not os.path.isdir(outdir_host):
        os.mkdir(outdir_host)
    outdir = os.path.join('/opt', path)

    # pgdump_2019-10-09T21:02:26.backup
    now = datetime.datetime.now().isoformat().split('.')[0]
    fn = f'pgdump_{now}.backup'

    fp = os.path.join(outdir, fn)

    execute_bash_command(
        'docker-compose exec db',
        # note: need the single quotes to use environment variables
        f"bash -c 'pg_dump -U $POSTGRES_USER -d $POSTGRES_DB > {fp}'"
    )


# ########################################################################### #
# MAIN
# ########################################################################### #

if __name__ == '__main__':
    pargs = parse_args(root_parser)
    process_global_arguments(pargs)
    subparser_command = popattr(
        pargs, KEYWORD_SUBPROCESS_COMMAND, None
    )
    if subparser_command is None:
        root_parser.print_help(sys.stderr)
        sys.exit(1)
    else:
        subparser_command(pargs)
