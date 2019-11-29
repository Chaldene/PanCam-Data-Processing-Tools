# Cal_HK.py
#
# Barry Whiteside
# Mullard Space Science Laboratory - UCL
#
# PanCam Data Processing Tools

import pandas as pd
import numpy as np
from pathlib import Path

class cal_HK_Error(Exception):
    """error for unexpected things"""
    pass

def cal_HK(PROC_DIR):
    """Takes the processed telemetery and produces calibrated HK pandas array"""

    print("---Calibrating TM HK Files")

    ## Search for PanCam Processed Files
    FILT_DIR = "*RAW_HKTM.pickle"
    PikFile = sorted(PROC_DIR.rglob(FILT_DIR))
    
    if len(PikFile) == 0:
        print("**No RAW HKTM Files Found**")
        print("Decoding TM HK Files Aborted")
        return
    elif len(PikFile) > 1:
        cal_HK_Error("Warning more than one 'RAW_TM.pickle' found.")

    ## Read RAW TM pickle file
    RAW = pd.read_pickle(PikFile[0])
    CalTM = RAW['DT'].copy()

    ## Voltages
    ratio = 4096*1.45914

    CalTM['Volt_Ref'] = ratio / RAW['Volt_Ref']
    CalTM['Volt_6V0'] = CalTM['Volt_Ref'] / 4096 * 6.4945 * RAW['Volt_6V0']
    CalTM['Volt_1V5'] = CalTM['Volt_Ref'] * RAW['Volt_1V5']/4096

    ## Temperatures
    Cal_A = [306.90, 308.57, 313.57, 307.91, 307.17, 310.42, 304.15]
    Cal_B = [-268.21, -268.14, -274.94, -267.41, -266.71, -270.04, -264.52]

    CalTM['Temp_LFW']  = RAW['Temp_LFW']  * Cal_A[0] / CalTM['Volt_Ref'] + Cal_B[0]
    CalTM['Temp_RFW']  = RAW['Temp_RFW']  * Cal_A[1] / CalTM['Volt_Ref'] + Cal_B[1]
    CalTM['Temp_HRC']  = RAW['Temp_HRC']  * Cal_A[2] / CalTM['Volt_Ref'] + Cal_B[2]
    CalTM['Temp_LWAC'] = RAW['Temp_LWAC'] * Cal_A[3] / CalTM['Volt_Ref'] + Cal_B[3]
    CalTM['Temp_RWAC'] = RAW['Temp_RWAC'] * Cal_A[4] / CalTM['Volt_Ref'] + Cal_B[4]
    CalTM['Temp_LDO']  = RAW['Temp_LDO']  * Cal_A[5] / CalTM['Volt_Ref'] + Cal_B[5]
    CalTM['Temp_HRCA'] = RAW['Temp_HRCA'] * Cal_A[6] / CalTM['Volt_Ref'] + Cal_B[6]
    
    write_file = PROC_DIR / (PikFile[0].stem.split('_RAW')[0] + "_Cal_HKTM.pickle")
    if write_file.exists():
        write_file.unlink()
        print("Deleting file: ", write_file.stem)
    with open(write_file, 'w') as f:
        CalTM.to_pickle(write_file)
        print("PanCam Cal HK TM pickled.") 

if __name__ == "__main__":
    DIR = Path(input("Type the path to the PROC folder where the processed files are stored: "))

    cal_HK(DIR)