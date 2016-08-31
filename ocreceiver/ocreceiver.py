from __future__ import print_function

import logging.config
import os
import sys

import yaml

from hfunctions import *

if not hasattr(__builtins__, 'FileNotFoundError'):
    FileNotFoundError = IOError

# Later it will be /etc/owncloud_receiver/ocr_config.yaml
if len(sys.argv) != 2:
    print('You have to prive a configuration file as argument like:\n'
          'ocreceiver.py [settings.conf]')
    sys.exit(1)
DEFAULT_CONFIG_LOC = sys.argv[1]


# Set the umask
os.umask(0o007)

# Defines the marker string
MARKER = ".MARKER_is_finished_"

# Load the configuration file
try:
    with open(DEFAULT_CONFIG_LOC) as f:
        config = yaml.safe_load(open(DEFAULT_CONFIG_LOC))
except FileNotFoundError:
    print("Could not find configuration file {0}. Make sure it"
          " exists!".format(DEFAULT_CONFIG_LOC))
    sys.exit(1)

# Load logging settings and create the logger
try:
    logging.config.dictConfig(config)
except ValueError as err:
    print('Something went horribly wrong!')
    print(err.message)
    sys.exit(1)
except AttributeError:
    import logutils.dictconfig
    logutils.dictconfig.dictConfig(config)

logger = logging.getLogger('logFile')
logger.info('Started search for new incoming files in root directory:' +
            config['data_location'])

if not os.path.exists(config['data_location']):
    logger.error('The location of the data directory {0} does not exist'
                 .format(config['data_location']))
    sys.exit(1)

# Get all files and start to check if files are still writen onto the
# file system or if they are ready to move. If so, then the
# ".MARKER_is_finished" file will be created. This will be the signal for
# dropboxhandler to move this file to the respective data storage server (DSS).
for root, _, files in os.walk(config["data_location"]):
    if not os.access(root, os.X_OK):
        logger.error('Cannot access {0}'.format(root))
        continue
    if files:
        for ifile in files:
            # Skip .MARKER files
            if not contains_valid_barcode(ifile):
                logger.warning(
                    '{0} does not carry a valid barcode'.format(ifile))
                continue
            if MARKER in ifile:
                logger.warning(
                    'Marker file for {0}/{1} already exists.'.format(root, ifile))
                continue
            # Check if file is accessed by the system
            if is_currently_accessed(ifile, root):
                logger.warning(str.format(
                    '{0} is currently accessed by the system.',
                    root + "/" + ifile))
            else:
                create_marker_file(MARKER, ifile, root, logger)

# Finish logging message
logger.info('Finished search for new incoming files.')
sys.exit(0)
