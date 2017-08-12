from collections import OrderedDict
from importlib import import_module
import os
import sys

from paver.easy import task, needs, path, sh, options
from paver.setuputils import install_distutils_tasks
try:
    import base_node_rpc
    from base_node_rpc.pavement_base import *
except ImportError:
    pass

# Make standard `setuptools.command` tasks available (e.g., `sdist`).
install_distutils_tasks()

# Add package directory to Python path. This enables the use of
# `mr_box_peripheral_board` functions for discovering, e.g., the
# path to the Arduino firmware sketch source files.
sys.path.append(path('.').abspath())
from mr_box_peripheral_board.version import getVersion

# Import project module.
PROJECT_PREFIX = 'mr_box_peripheral_board'
package_name = PROJECT_PREFIX.replace('_', '-')
rpc_module = import_module(PROJECT_PREFIX)
VERSION = getVersion()
PROPERTIES = OrderedDict([('base_node_software_version',
                           base_node_rpc.__version__),
                          ('package_name', package_name),
                          ('display_name', 'MR-Box peripherals'),
                          ('manufacturer', 'Wheeler Microfluidics Lab'),
                          ('software_version', VERSION),
                          ('url', 'https://github.com/wheeler-microfluidics/mr-box-peripheral-board.py')])

# XXX Properties used to generate Arduino library properties file.
LIB_PROPERTIES = PROPERTIES.copy()
LIB_PROPERTIES.update(OrderedDict([('author', 'Christian Fobel'),
                                   ('author_email', 'christian@fobel.net'),
                                   ('camelcase_name', 'MrBoxPeripheralBoard'),
                                   ('short_description', 'Firmware for MR-Box controller board for various peripherals (e.g., motorized magnet, LED panels, micro pump, temperature/humidity sensor)'),
                                   ('version', VERSION),
                                   ('long_description', ''),
                                   ('category', ''),
                                   ('architectures', 'avr')]))

options(
    rpc_module=rpc_module,
    PROPERTIES=PROPERTIES,
    LIB_PROPERTIES=LIB_PROPERTIES,
    # Classes inherited from headers in `BaseNodeRpc` Arduino library.
    base_classes=['BaseNodeSerialHandler',
                  'BaseNodeEeprom',
                  'BaseNodeConfig<ConfigMessage, Address>'],
    # Classes inherited from headers within sketch directory.
    rpc_classes=['mr_box_peripheral_board::PMT',
                 'mr_box_peripheral_board::Pump',
                 'base_node_rpc::ZStage',
                 'mr_box_peripheral_board::Max11210Adc',
                 'mr_box_peripheral_board::Node'],
    setup=dict(name=PROPERTIES['package_name'],
               version=VERSION,
               description=LIB_PROPERTIES['short_description'],
               author=LIB_PROPERTIES['author'],
               author_email=LIB_PROPERTIES['author'],
               url=PROPERTIES['url'],
               license='BSD',
               install_requires=['base-node-rpc>=0.23'],
               include_package_data=True,
               package_data={'mr_box_peripheral_board.notebooks': '*.ipynb'},
               packages=['mr_box_peripheral_board',
                         'mr_box_peripheral_board.bin',
                         'mr_box_peripheral_board.notebooks',
                         'mr_box_peripheral_board.ui']))
