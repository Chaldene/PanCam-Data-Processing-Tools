# -*- coding: utf-8 -*-
"""
tc_cal.py

Barry Whiteside
Mullard Space Science Laboratory - UCL

PanCam Data Processing Tools
Created 06 Mar 2020
"""

from pathlib import Path
import logging
import pandas as pd

import pancam_fns

logger = logging.getLogger(__name__)

wac_cmd_dict = {0x00: "IA",
                0x01: "HK",
                0x02: "DT"}

hrc_cmd_dict = {0x00: "RST",
                0x01: "SID",
                0x02: "CS",
                0x03: "Motor Steps",
                0x04: "Motor Stop",
                0x05: "Set Gains",
                0x06: "Set Int",
                0x08: "Reset IMG #",
                0x09: "Set Win",
                0x0A: "Start AI",
                0x0B: "Start AF",
                0x0C: "Reg 1",
                0x0D: "Reg 2",
                0x0E: "Reg 4",
                0x0F: "Goto Enc",
                0x10: "Reg 3",
                0x11: "Set Enc",
                0x12: "Load AI",
                0x13: "Set Shr",
                0x14: "Set Win Sz",
                0x15: "Set Motor",
                0xF5: "Enc Direct",
                0xF6: "Enc Inver"}


def decode_all(proc_dir: Path):
    """Decodes all commands into thier specific functions

    Arguments:
        proc_dir {Path} -- Path to Unproc_TC.pickle file generated

    Generates:
        Cal_TC.pickle -- Containing the decoded Cam_Cmd dataframe.
    """

    logger.info("Decoding TCs")

    files_tc = pancam_fns.Find_Files(
        proc_dir, "Unproc_TC.pickle", SingleFile=True)

    if not files_tc:
        return

    tc = pd.read_pickle(files_tc[0])

    tc = cam_decode(tc)

    tc.to_pickle(proc_dir / "Cal_TC.pickle")
    logger.info("PanCam Decoded TC Pickled.")
    logger.info("--TC Camera Decode Completed")


def cam_decode(tc: pd.DataFrame()):
    """Decodes the camera specific telecommands

    Arguments:
        tc {pd.DataFrame()} -- Pandas dataframe consisting of telecommands

    Returns:
        tc {pd.DataFrame()} -- Pandas dataframe with additional 'Cam_Cmd' column
    """

    # Blank space needed after name as that is how it is stored
    wac = tc[tc['ACTION'] == 'WAC ']
    hrc = tc[tc['ACTION'] == 'HRC ']

    if not wac.empty:
        logger.info("WAC Commands Found")
        tc['Cam_Cmd'] = wac[5].replace(wac_cmd_dict)

    if not hrc.empty:
        logger.info("HRC Commands Found")
        tc['Cam_Cmd'] = hrc[5].replace(hrc_cmd_dict)

    return tc


if __name__ == "__main__":

    proc_dir = Path(
        input("Type the path to the folder PROC dir: "))

    logging.basicConfig(filename=(proc_dir / 'processing.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    logger.info('\n\n\n\n')
    logger.info("Running tc_cal.py as main")
    logger.info("Reading directory: %s", dir)

    decode_all(proc_dir)
