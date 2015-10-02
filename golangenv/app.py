import argparse
import HTMLParser as HP
import logging
import logging.config
import os
import platform
import shutil
import StringIO
import sys
import tarfile
import urllib2

#{{{ logging config
logging.config.dictConfig({
    'version': 1,
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'level': 'DEBUG',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'default': {
            'format': '%(levelname)s: %(message)s',
        }
    },
})
#}}}

#{{{ subparser implementation
class subcommand(object):
    _parser = argparse.ArgumentParser()
    _subparser = _parser.add_subparsers(dest='command')
    def __new__(cls, command_or_f=None, command=None):
        if isinstance(command_or_f, basestring):
            return lambda f: subcommand(f, command_or_f)
        elif callable(command_or_f):
            return object.__new__(cls)
    def __init__(self, function, command=None):
        self.parser = self._subparser.add_parser(command or function.__name__)
        self.parser.set_defaults(function=function)
    def __call__(self, *args, **kwargs):
        return self.function(*args, **kwargs)
    def __getattr__(self, key):
        return getattr(self.parser, key)
    @classmethod
    def parse_args(cls, *args, **kwargs):
        return cls._parser.parse_args(*args, **kwargs)
    @classmethod
    def dispatch(cls, *args, **kwargs):
        ns = cls._parser.parse_args(*args, **kwargs)
        return ns.function(ns)
    @classmethod
    def set_defaults(cls, *args, **kwargs):
        cls._parser.set_defaults(*args, **kwargs)
#}}}

def get_virtualenv_dir():
    if hasattr(sys, 'real_prefix'):
        return sys.prefix
    elif hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix:
        return sys.prefix
    raise Exception('no virtualenv found')


def _get_arch_string():
    system = platform.system()
    if system == 'Linux':
        arch = 'linux'
    elif system == 'Darwin':
        arch = 'darwin'
    if '64bit' in platform.architecture():
        arch += '-amd64'
    else:
        arch += '-386'
    if system == 'Darwin':
        arch += '-osx' + '.'.join(platform.mac_ver()[0].split('.')[0:2])
    return arch


def _get_prebuilt_list():
    response = urllib2.urlopen('https://golang.org/dl/')
    versions = []
    arch = _get_arch_string()

    # ugly!
    class Parser(HP.HTMLParser):
        def handle_starttag(self, tag, attrs):
            attrs = dict(attrs)
            if tag == 'a' and attrs['href'].startswith('https://storage.googleapis.com/golang/'):
                if arch in attrs['href']:
                    versions.append(attrs['href'])

    parser = Parser()
    parser.feed(response.read())
    return versions


@subcommand
def install(ns):
    try:
        prebuilts = _get_prebuilt_list()
        if ns.version == 'latest':
            url = prebuilts[0]
        else:
            for link in prebuilts:
                if link.endswith('%s.%s.tar.gz' % (ns.version, _get_arch_string())):
                    url = link
                    break
            else:
                print 'could not find version', ns.version
                sys.exit(1)

        extractpath = os.path.join(get_virtualenv_dir(), 'opt')
        binpath = os.path.join(get_virtualenv_dir(), 'bin')
        goroot = os.path.join(extractpath, 'go')
        gorootbin = os.path.join(goroot, 'bin')
        gopath = ns.gopath
        if gopath == '.':
            gopath = os.getcwd()

        if not os.path.exists(extractpath):
            os.mkdir(extractpath)

        if os.path.exists(goroot):
            shutil.rmtree(goroot)

        response = urllib2.urlopen(url)
        tf = tarfile.open(mode='r:gz', fileobj=StringIO.StringIO(response.read()))
        tf.extractall(extractpath)

        for app in ('go', 'gofmt', 'gocode'):
            os.symlink(os.path.join(gorootbin, app), os.path.join(binpath, app))

        act = os.path.join(binpath, 'postactivate')
        deact = os.path.join(binpath, 'predeactivate')

        with open(act, 'a') as f:
            f.write('export GOROOT=%s\n' % goroot)
            f.write('export GOPATH=%s\n' % gopath)
            f.write('export VENV_PATH_BKUP=${PATH}\n')
            f.write('export PATH=$GOPATH/bin:${PATH}\n')

        with open(deact, 'a') as f:
            f.write('export PATH=${VENV_PATH_BKUP}\n')
            f.write('unset VENV_PATH_BKUP\n')
            f.write('unset GOPATH\n')
            f.write('unset GOROOT\n')

    except Exception as e:
        print 'Could not install prebuilt binary', e
        import traceback
        traceback.print_exc()
        sys.exit(1)
install.add_argument('version', type=str, nargs='?', default='latest')
install.add_argument('gopath', type=str, nargs='?', default='.')

@subcommand('list')
def _list(ns):
    arch = _get_arch_string()
    for version in _get_prebuilt_list():
        version = version[len('https://storage.googleapis.com/golang/go'):]
        version = version[:-len('..tar.gz')] # extra dot accounted here
        version = version[:-len(arch)]
        print version

def main():
    subcommand.dispatch()
