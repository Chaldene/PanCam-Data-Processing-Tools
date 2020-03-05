# -*- coding: utf-8 -*-
"""
Created on Thu Oct 31 17:18:02 2019

@author: ucasbwh
Parses Rover .ha and .csv files by extracting PanCam data. 
"""

import pandas as pd
from pathlib import Path
from bitstruct import unpack_from as upf
import logging
import imageio

import PC_Fns

logger = logging.getLogger(__name__)


def TM_extract(ROV_DIR):
    """Searches for TM with Rover files and creates a binary array of each file found"""

    logger.info("Processing Rover TM Files")
    DF = pd.DataFrame()
    DRS = pd.DataFrame()
    DRT = pd.DataFrame()
    DG = pd.DataFrame()

    TMfiles = PC_Fns.Find_Files(ROV_DIR, "STDRawOcds*.csv")
    if not TMfiles:
        logger.warning("No files found - ABORTING")
        return False

    # Read CSV files and parse
    for file in TMfiles:
        logger.info("Reading %s", file.name)
        DT = pd.read_csv(file, sep=';', header=0, index_col=False)

        # Search for PanCam housekeeping
        DL = DT[(DT['NAME'] == "AB.TM.TM_RMI000401") | (
            DT['NAME'] == "AB.TM_TM_RMI000402")].copy()
        if not DL.empty:
            DL['RAW'] = DL.RAW_DATA.apply(lambda x: x[38:-4])
            DL['DT'] = pd.to_datetime(
                DL['GROUND_REFERENCE_TIME'], format='%d/%m/%Y %H:%M:%S.%f')
            DF = DF.append(DL[['RAW', 'DT']], ignore_index=True)

        # Rover HK both low and high speed
        DP = DT[(DT['NAME'] == "AB.TM.MRSP8001") | (
            DT['NAME'] == "AB.TM.MRSP8002")].copy()
        if not DP.empty:
            DG = DP.RAW_DATA.apply(lambda x: x[2:])
            DG = DG.apply(lambda x: bytearray.fromhex(x))
            # PanCam Current
            OffBy, OffBi, Len = 85, 4, 'u12'
            DP['RAW_Inst_Curr'] = DG.apply(
                lambda x: upf(Len, x, offset=8*OffBy+OffBi)[0])
            DP['Inst_Curr'] = DP['RAW_Inst_Curr'] * 1.1111/4095
            # PanCam Heater
            OffBy, OffBi, Len = 57, 4, 'u12'
            DP['RAW_HTR_Curr'] = DG.apply(
                lambda x: upf(Len, x, offset=8*OffBy+OffBi)[0])
            DP['HTR_Curr'] = DP['RAW_HTR_Curr'] * 1.1111/4095
            # PanCam Heater Status
            OffBy, OffBi, Len = 51, 2, 'u1'
            DP['HTR_ST'] = DG.apply(lambda x: upf(
                Len, x, offset=8*OffBy+OffBi)[0])
            # PanCam Power Status
            OffBy, OffBi, Len = 77, 1, 'u1'
            DP['PWR_ST'] = DG.apply(lambda x: upf(
                Len, x, offset=8*OffBy+OffBi)[0])
            DP['DT'] = pd.to_datetime(
                DP['GROUND_REFERENCE_TIME'], format='%d/%m/%Y %H:%M:%S.%f')
            DRS = DRS.append(DP, ignore_index=True)

        # Rover HK Thermistors Only contained within low speed HK
        DK = DT.loc[DT['NAME'] == "AB.TM.MRSP8001"].copy()
        if not DK.empty:
            DW = DK.RAW_DATA.apply(lambda x: x[2:])
            DW = DW.apply(lambda x: bytearray.fromhex(x))
            # PIU Temp
            OffBy, OffBi, Len = 511, 3, 'u13'
            DK['RAW_PIU_T'] = DW.apply(
                lambda x: upf(Len, x, offset=8*OffBy+OffBi)[0])
            # Calculated from thermistor curve provided
            DK['PIU_T'] = DK['RAW_PIU_T']*0.18640 - 259.84097
            # DCDC Temp
            OffBy, OffBi, Len = 559, 3, 'u13'
            DK['RAW_DCDC_T'] = DW.apply(
                lambda x: upf(Len, x, offset=8*OffBy+OffBi)[0])
            # Calculated from thermistor curve provided
            DK['DCDC_T'] = DK['RAW_DCDC_T']*0.18640 - 259.84097
            DK['DT'] = pd.to_datetime(
                DK['GROUND_REFERENCE_TIME'], format='%d/%m/%Y %H:%M:%S.%f')
            DRT = DRT.append(DK, ignore_index=True)

    # logger.info("Number of PanCam TMs found: %d", DF.shape[0])
    logger.info("Number of Rover Status Entries found: %d", DRS.shape[0])
    logger.info("Number of Rover Temperature Entries found: %d", DRT.shape[0])

    if DF.shape[0] != 0:
        write_dts = DF['DT'].iloc[0].strftime('%y%m%d_%H%M%S_')
        DF['Source'] = "STDRawOcds.csv"
        DF.to_pickle(ROV_DIR / "PROC" / (write_dts + "csv_Unproc_HKTM.pickle"))
        logger.info("PanCam HKTM pickled.")

    if DRS.shape[0] != 0:
        write_dts = DRS['DT'].iloc[0].strftime('%y%m%d_%H%M%S_')
        DRS.to_pickle(ROV_DIR / "PROC" / (write_dts + "RoverStatus.pickle"))
        logger.info("Rover Status TM pickled.")

    if DRT.shape[0] != 0:
        write_dts = DRT['DT'].iloc[0].strftime('%y%m%d_%H%M%S_')
        DRT.to_pickle(ROV_DIR / "PROC" / (write_dts + "RoverTemps.pickle"))
        logger.info("Rover Temperatures TM pickled.")

    logger.info("Processing Rover TM Files Completed")

    return True


def TC_extract(ROV_DIR):

    logger.info("Processing Rover TC Files")
    TC = pd.DataFrame()

    # Find all Rover TC files within folder and subfolders
    TCfiles = PC_Fns.Find_Files(ROV_DIR, "STDChrono*.csv")
    if not TCfiles:
        logger.error("No files found - ABORTING")
        return

    # Read CSV file and parse
    for file in TCfiles:
        logger.info("Reading %s", file.name)
        dt = pd.read_csv(file, sep=';', encoding="ISO-8859-1",
                         header=0, dtype=object, index_col=False)

        dp = dt[dt['DESCRIPTION'].str.contains(
            "Pan Cam", na=False) & dt['NAME'].str.contains("CRM", na=False)].copy()
        dm = dp['VARIABLE_PART'].str.split(',', -1, expand=True)

        if not dp.empty:
            TC = pd.concat(
                [dp[['NAME', 'DESCRIPTION', 'GROUND_REFERENCE_TIME']], dm.loc[:, 9:]], axis=1)
            TC['DT'] = pd.to_datetime(
                TC['GROUND_REFERENCE_TIME'], format='%d/%m/%Y %H:%M:%S.%f')
            TC['ACTION'] = TC['DESCRIPTION'].map(lambda x: x.lstrip('Pan Cam'))
            TC['LEVEL'] = 1

    logger.info("Number of PanCam TCs found: %d", TC.shape[0])

    if TC.shape[0] != 0:
        write_dts = TC['DT'].iloc[0].strftime('%y%m%d_%H%M%S_')
        TC.to_pickle(ROV_DIR / "PROC" / (write_dts + "Unproc_TC.pickle"))
        logger.info("Rover TC pickled")

    logger.info("Processing Rover TC Files Completed")


def NavCamBrowse(ROV_DIR):
    """Searches for PGM files and creates an 8-bit .png to browse"""

    logger.info("Searching for NavCam .pgm files to generate browse")
    PGM_Files = PC_Fns.Find_Files(ROV_DIR, "*.pgm")

    for curFile in PGM_Files:
        image = imageio.imread(curFile)
        write_file = curFile.with_suffix(".png")

        # Check if file exists
        if write_file.exists():
            write_file.unlink()
            logger.info("Deleting file: %s", write_file.name)
        logger.info("Creating file: %s", write_file.name)
        imageio.imwrite(write_file, image)


if __name__ == "__main__":
    DIR = Path(
        input("Type the path to thefolder where the Rover files are stored: "))

    logging.basicConfig(filename=(DIR / 'processing.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    logger.info('\n\n\n\n')
    logger.info("Running Rover.py as main")
    logger.info("Reading directory: %s", DIR)

    PROC_DIR = DIR / "PROC"
    if PROC_DIR.is_dir():
        logger.info("Processing' Directory already exists")
    else:
        logger.info("Generating 'Processing' directory")
        PROC_DIR.mkdir()

    TM_extract(DIR)
    TC_extract(DIR)
    NavCamBrowse(DIR)
