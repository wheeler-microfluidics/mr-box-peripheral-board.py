from collections import OrderedDict
import warnings

from path_helpers import path

from ._version import get_versions
__version__ = get_versions()['version']
if '+' in __version__:
    __version__ = __version__.split('+')[0]
del get_versions

try:
    from .proxy import Proxy, I2cProxy, SerialProxy
except (ImportError, TypeError) as exception:
    warnings.warn(str(exception))
try:
    from .config import Config
except (ImportError, TypeError) as exception:
    warnings.warn(str(exception))


def package_path():
    return path(__file__).parent


def get_sketch_directory():
    '''
    Return directory containing the Arduino sketch.
    '''
    return package_path().joinpath('..', 'src').realpath()


def get_lib_directory():
    return package_path().joinpath('..', 'lib').realpath()


def get_includes():
    '''
    Return directories containing the Arduino header files.

    Notes
    =====

    For example:

        import arduino_rpc
        ...
        print ' '.join(['-I%s' % i for i in arduino_rpc.get_includes()])
        ...

    '''
    import base_node_rpc

    return ([get_sketch_directory()] +
            list(get_lib_directory().walkdirs('src')) +
            base_node_rpc.get_includes())


def get_sources():
    '''
    Return Arduino source file paths.  This includes any supplementary source
    files that are not contained in Arduino libraries.
    '''
    import base_node_rpc

    return (get_sketch_directory().files('*.c*') +
            list(get_lib_directory().walkfiles('*.c*')) +
            base_node_rpc.get_sources())
