import re
import subprocess
import os

# QBiC barcode regex
BARCODE_REGEX = "Q[A-X0-9]{4}[0-9]{3}[A-X][A-X0-9]"
# MARKER file types
ERROR_MARKER = "MARKER_error_"
STARTED_MARKER = "MARKER_started_"
OC_PART_FILE = "ocTransfer"
FINISHED_MARKER = "MARKER_is_finished_"


def is_marker_flag_file(file_path):
    """Checks if file is a marker flag file"""
    if ERROR_MARKER in file_path or STARTED_MARKER in file_path or\
                    FINISHED_MARKER in file_path:
        return True
    return False


def contains_valid_barcode(file_path):
    """Check if a file contains a valid barcode
    """
    stem, _ = os.path.splitext(os.path.basename(file_path))
    barcodes = re.findall(BARCODE_REGEX, stem)
    valid_barcodes = [b for b in barcodes if is_valid_barcode(b)]
    if len(barcodes) != len(valid_barcodes):
        return False
    if not barcodes:
        return False
    return True


def is_valid_barcode(barcode):
    """Check if barcode is a valid OpenBis barcode.
    (Code from Adrian's dropboxhandler, thx!)"""
    if re.match('^' + BARCODE_REGEX + '$', barcode) is None:
        return False
    csum = sum(ord(c) * (i + 1) for i, c in enumerate(barcode[:-1]))
    csum = csum % 34 + 48
    if csum > 57:
        csum += 7
    if barcode[-1] == chr(csum):
        return True
    return False


def is_currently_accessed(file_i, dir):
    """ Checks if a file is currently accessed by the system,
    and therefore should not be moved by the dropboxhandler yet.
    :param file_i: the input file
    :param dir:  the root directory
    :return: True if accessed, False else
    """
    exit_status = subprocess.call('bash -c \"' +
                                  str.format('lsof {0}/{1} > /dev/null',
                                             dir, correct_file_name(file_i)) +
                                  '\"', shell=True)
    if exit_status == 0 or OC_PART_FILE in file_i:
        return True
    return False


def correct_file_name(file_name):
    """ Correct for some bad window user's habit
    :param file_name: the file name to correct
    :return: the corrected file name
    """
    file_name = file_name.replace(" ", "\ ")
    file_name = file_name.replace("(", "\(")
    file_name = file_name.replace(")", "\)")
    return file_name


def get_filenames_from_tsv(tsv_file):
    """Extract the filenames from the tsv file
    and returns them in a list. If something went wrong,
    an empty list is returned."""
    header_index = -1
    file_names = []
    with open(tsv_file, "r") as fh:
        header_ls = fh.readline().split("\t")
        for index, name in enumerate(header_ls):
            if name.lower() == "filename":
                header_index = index
        if header_index == -1:
            return file_names
        for line in fh.read().splitlines():
            content_ls = line.split("\t")
            file_names.append(content_ls[header_index])
    return file_names


def create_marker_file(marker_flag, file_i, dir, logger):
    new_file = str.format('{0}/{1}{2}', dir, marker_flag, file_i)
    try:
        with open(new_file, 'w+'):
            logger.info('Marker file created for {0}/{1}'.format(dir,file_i))
            pass
    except Exception as err:
        #print('Could not create marker file. Reason: \n{0}'.format(err))
        logger.error(err)
