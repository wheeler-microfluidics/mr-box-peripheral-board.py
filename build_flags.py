from __future__ import print_function

from __future__ import absolute_import
import argparse
import sys

from mr_box_peripheral_board import __version__


def parse_args(args=None):
    if args is None:
        args = sys.argv[1:]
    parser = argparse.ArgumentParser()

    default_version = __version__
    parser.add_argument('-V', '--version', default=default_version)
    parser.add_argument('arg', nargs='*')

    return parser.parse_known_args(args=args)


if __name__ == '__main__':
    args, extra_args = parse_args()

    extra_args += [r'-DDEVICE_ID_RESPONSE=\"mr::{}\"'
                  .format(args.version)]
    # extra_args += [r'-DDEVICE_ID_RESPONSE=\"mr::0.1\"']

    print(' '.join(extra_args))
