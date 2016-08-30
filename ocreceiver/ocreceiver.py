from __future__ import print_function

import logging.config
import os
import sys

import yaml

from ocreceiver.hfunctions import *

if not hasattr(__builtins__, 'FileNotFoundError'):
    FileNotFoundError = IOError

# Later it will be /etc/owncloud_receiver/ocr_config.yaml
DEFAULT_CONFIG_LOC = sys.argv[1]

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
logger = logging.getLogger('logFile')
logger.info('Started search for new incoming files in root directory:' +
            config['data_location'])

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
