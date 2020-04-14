#!/usr/local/bin/python
import argparse
import sys
import os

from etl.conf import settings
import flows

FLOW_NAMES = tuple(flows.FLOWS.keys())

parser = argparse.ArgumentParser(
    description="Create flow visualizations"
)
parser.add_argument(
    'flow',
    nargs='*',
    default=FLOW_NAMES,
    help=f'Defaults to all. Must be one of: {FLOW_NAMES}'
)
parser.add_argument(
    '-d', '--directory',
    default=settings.FLOW_VISIUALIZATIONS_PATH,
    help=f'Location to save images.'
)

if __name__ == '__main__':
    pargs = parser.parse_args()
    flow_names = pargs.flow
    directory = pargs.directory

    unknown_flow_names = set(flow_names) - set(FLOW_NAMES)
    if len(unknown_flow_names):
        sys.stdout.write(
            f'Unknown flow names: {unknown_flow_names} '
            f'not one of {FLOW_NAMES}\n'
        )
        sys.exit(1)

    for flow_name in flow_names:
        flow = flows.FLOWS[flow_name]
        filename = os.path.join(directory, flow_name)
        sys.stdout.write(f'{flow_name} -> "{filename}"\n')
        flow.visualize(filename=filename)
