import argparse
import asyncio
import os

from agentcoreclient import AgentCoreClient
from setproctitle import setproctitle
from lib.check import CHECKS
from lib.config import read_asset_config
from lib.version import __version__


# Migrate the mssql configuration and credentials
def migrate_config_folder():
    if os.path.exists('/data/config/OsVmwareProbe'):
        os.rename('/data/config/OsVmwareProbe', '/data/config/vmwareprobe')
    if os.path.exists('/data/config/vmwareprobe/defaultCredentials.ini'):
        os.rename('/data/config/vmwareprobe/defaultCredentials.ini',
                  '/data/config/vmwareprobe/defaultAssetConfig.ini')


if __name__ == '__main__':
    setproctitle('vmwareprobe')

    migrate_config_folder()

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-l', '--log-level',
        default='warning',
        help='set the log level',
        choices=['debug', 'info', 'warning', 'error'])

    parser.add_argument(
        '--log-colorized',
        action='store_true',
        help='use colorized logging')

    args = parser.parse_args()

    AgentCoreClient.setup_logger(args.log_level, args.log_colorized)

    cl = AgentCoreClient(
        'vmwareProbe',
        __version__,
        CHECKS,
        read_asset_config,
        '/data/config/vmwareprobe/vmwareProbe-config.json'
    )

    asyncio.get_event_loop().run_until_complete(
        cl.connect_loop()
    )
