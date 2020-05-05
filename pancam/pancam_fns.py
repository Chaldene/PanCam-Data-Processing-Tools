# PC_Fns.py
#
# Barry Whiteside
# Mullard Space Science Laboratory - UCL
#
# PanCam Data Processing Tools

from pathlib import Path
from natsort import natsorted, ns
from bitstruct import unpack_from as upf
import pandas as pd
import binascii
import logging

logger = logging.getLogger(__name__)
status = logging.getLogger('status')


def Find_Files(DIR, FILT, SingleFile=False, Recursive=True):
    """Finds all the files within DIR using the wildcard FILT.
    If SingleFile is True expects to return only one file."""

    logger.info("Find_Files Called")
    if Recursive:
        FoundFiles = natsorted(DIR.rglob(FILT), alg=ns.PATH)
    else:
        FoundFiles = natsorted(DIR.glob(FILT), alg=ns.PATH)

    logger.debug(filename for filename in FoundFiles)

    num = len(FoundFiles)
    if num == 0:
        logger.warning("No %s Files Found", FILT)
        return []
    else:
        logger.info("Number of %s files found: %d", FILT, num)

    if (SingleFile == True) & (num > 1):
        logger.warning("More than one %s found, only first used.", FILT)
    return FoundFiles


class LID_Browse_Error(Exception):
    """error for unexpected things"""
    pass


def LID_Browse(RawHDR_Dict, Model):
    """returns a string to name the browse images

    Standard format:

    <cam_ID><filter_ID>_<taskID>_<taskRun>_<img_no.>_ <temp>_<exposure>_<date-time>.ext

    """

    Cams = ('L', 'R', 'H')
    LID_str = Model + '-' + Cams[RawHDR_Dict['Cam']-1]

    # Filter
    if RawHDR_Dict['Cam'] == 3:
        LID_str += 'RC_'
    elif 0 < RawHDR_Dict['Cam'] < 3:
        LID_str += "{0:0=2d}".format(RawHDR_Dict['FW']) + "_"
    else:
        LID_Browse_Error("Warning invalid CAM number")

    # TaskID, Run Number, Image Number
    LID_str += "{0:0=3d}".format(RawHDR_Dict['Task_ID']) + "_"
    LID_str += "{0:0=3d}".format(RawHDR_Dict['Task_RNO']) + "_"
    LID_str += "{0:0=3d}".format(RawHDR_Dict['Img_No']) + "_"

    # Temp and Integration time (Uncal for now)
    if 0 < RawHDR_Dict['Cam'] < 3:
        LID_str += "{0:0=4d}".format(RawHDR_Dict['W_End_Temp']) + "_"
        LID_str += "{0:0=7d}".format(RawHDR_Dict['W_Int_Time']) + "_"
    elif RawHDR_Dict['Cam'] == 3:
        LID_str += "{0:0=4d}".format(RawHDR_Dict['H_Temp']) + "_"
        LID_str += "{0:0=7d}".format(RawHDR_Dict['H_Int_Time']) + "_"
    else:
        LID_Browse_Error("Warning invalid CAM number")

    # Need to add ability to include start time in reasonable format

    return LID_str


def PandUPF(Column, Len, OffBy, OffBi):
    """Extracts a single RAW value from a binary pandas data column"""
    if int(Len[1:]) > 63:
        raise ValueError(
            "PandUPF used for variable larger than 63 bits. Returned value is cast to an Int64")
    Extract = Column.apply(lambda x: upf(
        Len, x, offset=8*OffBy+OffBi)[0]).astype('Int64')
    return Extract


def ReturnCUC_RAW(TM, Bin):
    """Returns the 6 bytes of the PKT CUC time as a single integer"""

    TM['Pkt_CUC'] = PandUPF(Bin, 'u48', 0, 16)
    return TM


def DropTM(TM_ErrorFrame, TM, Bin):
    """Function to remove error entries. The TM_ErrorFrame must be
    a subset of the TM dataframe. TM and Bin are pandas dataframes
    of the same size.

    The function returns the reduced TM and Bin"""

    for index, _ in TM_ErrorFrame.iterrows():
        logging.info("Packet removed: %s", binascii.hexlify(Bin[index]))
    newTM = TM.drop(TM_ErrorFrame.index)
    newBin = Bin.drop(TM_ErrorFrame.index)
    return newTM, newBin


def setup_logging():
    """Adds a configured stream handler to the root logger for console output.

    2 logging streams created:
        - display errors to console
        - display status to console

    Returns:
        logger -- standard logger to console used for errors
        stat -- logger used for status of processing for many files
    """

    # Setup 2 loggers one for general and one for status
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    stat = logging.getLogger('status')
    stat.setLevel(logging.INFO)

    # create console handler logger
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    ch_formatter = logging.Formatter(
        '%(module)s.%(funcName)s - %(levelname)s - %(message)s')
    ch.setFormatter(ch_formatter)
    logger.addHandler(ch)

    # create status logger
    sh = logging.StreamHandler()
    sh_formatter = logging.Formatter(
        'STATUS:   %(module)s.%(funcName)s - %(message)s')
    sh.setFormatter(sh_formatter)
    stat.addHandler(sh)

    return logger, stat


def setup_proc_logging(logger, proc_dir):
    """Sets the output file of the main logger with INFO logging level.

    Arguments:
        logger -- the logging.logger used to record messages
        proc_dir -- pathlib.dir where to create the processing.log
    """

    fh = logging.FileHandler(proc_dir / 'processing.log')
    fh.setLevel(logging.INFO)
    fh_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(module)s.%(funcName)s - %(message)s')
    fh.setFormatter(fh_formatter)

    logger.addHandler(fh)
