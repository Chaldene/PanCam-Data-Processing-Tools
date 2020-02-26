# Plotter.py
#
# Barry Whiteside
# Mullard Space Science Laboratory - UCL
#
# PanCam Data Processing Tools


import matplotlib.pyplot as plt
from matplotlib import gridspec
import matplotlib.dates as mdates
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import numpy as np
from pathlib import Path
import logging

import PC_Fns

logger = logging.getLogger(__name__)


register_matplotlib_converters()
myFmt = mdates.DateFormatter('%H:%M')

HK_Plot_Location = 'HK Plots'
# Voltage limits for calibrated plots
# Initialised as lists for dashed lines
Lim_VREF_Low = [3.1]
Lim_VREF_High = [3.6]
Lim_6V0_Low = [5.5]
Lim_6V0_High = [6.3]
Lim_1V5_Low = [1.4]
Lim_1V5_High = [1.6]


class plotter_Error(Exception):
    """error for unexpected things"""
    pass


def MakeHKPlotsDir(PROC_DIR):
    """Checks to see if the 'HK Plots' directory has been generated, if not creates it"""
    HK_DIR = PROC_DIR / HK_Plot_Location
    if HK_DIR.is_dir():
        logger.info("'HK Plots' Directory already exists")
    else:
        logger.info("Generating 'HK Plots' directory")
        HK_DIR.mkdir()
    return HK_DIR


def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    # Taken from https://stackoverflow.com/questions/18697417/not-plotting-zero-in-matplotlib-or-change-zero-to-none-python
    List = [float('nan') if x == 0 else x for x in values]
    List_Low = [float('nan') if x == 0 else x-15 for x in values]
    List_High = [float('nan') if x == 0 else x+15 for x in values]
    return List, List_Low, List_High


def HK_Voltages(PROC_DIR, Interact=False):
    """"Produces a calibrated and uncalibrated voltage plots from pickle files"""

    logger.info("Producing Voltage Plots")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam RAW Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RAW_HKTM.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    RAW = pd.read_pickle(RawPikFile[0])

    gs = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
    fig = plt.figure(figsize=(14.0, 9.0))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    ax2 = fig.add_subplot(gs[2], sharex=ax0)

    ax0.plot(RAW.DT, RAW.Volt_Ref.astype('int64'), 'r-', label='VRef RAW')
    ax0.set_xlabel('')
    ax0.set_ylabel('VRef RAW [ENG]')
    ax0.grid(True)
    ax0.set_xticklabels([], visible=False)

    ax1.plot(RAW.DT, RAW.Volt_6V0.astype('int64'), 'b-', label='6V RAW')
    ax1.set_xlabel('')
    ax1.set_ylabel('6V RAW [ENG]')
    ax1.grid(True)
    ax1.set_xticklabels([], visible=False)

    ax2.plot(RAW.DT, RAW.Volt_1V5.astype('int64'), 'g-', label='1V5 RAW')
    ax2.set_ylabel('1V5 RAW [ENG]')
    ax2.set_xlabel('Data Time')
    ax2.grid(True)
    # ax2.xaxis.set_major_formatter(myFmt)

    fig.tight_layout()
    fig.savefig(HK_DIR / 'VOLT_RAW.png')

    if Interact:
        plt.show(block=False)

    # Search for PanCam CAL Processed Files
    CalPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*Cal_HKTM.pickle", SingleFile=True)
    if not CalPikFile:
        logger.warning("No file found - ABORTING")
        return

    Cal = pd.read_pickle(CalPikFile[0])

    gs2 = gridspec.GridSpec(3, 1, height_ratios=[1, 1, 1])
    fig2 = plt.figure(figsize=(14.0, 9.0))
    ax3 = fig2.add_subplot(gs2[0])
    ax4 = fig2.add_subplot(gs2[1], sharex=ax3)
    ax5 = fig2.add_subplot(gs2[2], sharex=ax3)

    ax3.plot(Cal.DT, Cal.Volt_Ref, 'r-', label='VREF')
    ax3.plot([Cal['DT'].iloc[0], Cal['DT'].iloc[-1]],
             Lim_VREF_Low*2, 'darkred', linestyle='dashed')
    ax3.plot([Cal['DT'].iloc[0], Cal['DT'].iloc[-1]],
             Lim_VREF_High*2, 'darkred', linestyle='dashed')
    ax3.set_ylabel('VRef [V]')
    ax3.grid(True)
    ax3.set_xticklabels([], visible=False)

    ax4.plot(Cal.DT, Cal.Volt_6V0, 'b-', label='6V0')
    ax4.plot([Cal['DT'].iloc[0], Cal['DT'].iloc[-1]],
             Lim_6V0_Low*2, 'darkblue', linestyle='dashed')
    ax4.plot([Cal['DT'].iloc[0], Cal['DT'].iloc[-1]],
             Lim_6V0_High*2, 'darkblue', linestyle='dashed')
    ax4.set_ylabel('6V [V]')
    ax4.grid(True)
    ax4.set_xticklabels([], visible=False)

    ax5.plot(Cal.DT, Cal.Volt_1V5, 'g-', label='1V5')
    ax5.plot([Cal['DT'].iloc[0], Cal['DT'].iloc[-1]],
             Lim_1V5_Low*2, 'darkgreen', linestyle='dashed')
    ax5.plot([Cal['DT'].iloc[0], Cal['DT'].iloc[-1]],
             Lim_1V5_High*2, 'darkgreen', linestyle='dashed')
    ax5.set_ylabel('1V5 [V]')
    ax5.set_xlabel('Data Time')
    ax5.grid(True)
    # ax5.xaxis.set_major_formatter(myFmt)

    fig2.tight_layout()
    fig2.savefig(HK_DIR / 'VOLT_CAL.png')

    if Interact:
        plt.show(block=True)

    plt.close(fig)
    plt.close(fig2)

    logger.info("Producing Voltage Plots Completed")


def HK_Temperatures(PROC_DIR, Interact=False):
    """"Produces a calibrated and uncalibrated temperature plots from pickle files"""

    logger.info("Producing Temperature Plots")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam RAW Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RAW_HKTM.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    RAW = pd.read_pickle(RawPikFile[0])

    # RAW Plot and Heater
    gs = gridspec.GridSpec(4, 1, height_ratios=[2, 1, 0.5, 0.5])
    gs.update(hspace=0.0)
    fig = plt.figure(figsize=(14.0, 9.0))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    ax2 = fig.add_subplot(gs[2], sharex=ax0)
    ax3 = fig.add_subplot(gs[3], sharex=ax0)

    ax0.plot(RAW.DT, RAW.Temp_LFW.astype('int64'),  label='LFW')
    ax0.plot(RAW.DT, RAW.Temp_RFW.astype('int64'),  label='RFW')
    ax0.plot(RAW.DT, RAW.Temp_HRC.astype('int64'),  label='HRC')
    ax0.plot(RAW.DT, RAW.Temp_LWAC.astype('int64'), label='LWAC')
    ax0.plot(RAW.DT, RAW.Temp_RWAC.astype('int64'), label='RWAC')
    ax0.plot(RAW.DT, RAW.Temp_HRCA.astype('int64'), label='ACT')
    # Heater set-point and 15 values shaded either side
    HSP, HSP_L, HSP_H = zero_to_nan(RAW.Stat_Temp_Se.astype('int64'))
    ax0_HSP = ax0.plot(RAW.DT, HSP, '--', color='k', label='HTR Set Point')
    ax0.fill_between(RAW.DT, HSP_L, HSP_H,
                     color=ax0_HSP[0].get_color(), alpha=0.2)

    ax0.legend(loc='lower center', bbox_to_anchor=(
        0.5, 1.0), ncol=4, borderaxespad=0, frameon=False)
    ax0.text(.99, .95, 'Internal Temps', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax0.transAxes)
    ax0.set_ylabel('RAW [ENG]')
    ax0.grid(True)
    ax0.set_xticklabels([], visible=False)

    ax1.plot(RAW.DT, RAW.Temp_LDO.astype('int64'), '-k', label='LDO')
    ax1.text(.99, .9, 'LDO Temp', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax1.transAxes)
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position('right')
    ax1.set_xlabel('')
    ax1.set_ylabel('LDO RAW [ENG]')
    ax1.grid(True)
    ax1.set_xticklabels([], visible=False)

    ax2.plot(RAW.DT, RAW.Stat_Temp_He.astype('int64'), label='HTR')
    ax2.set_ylim([-0.5, 3.5])
    ax2.grid(True)
    ax2.text(.99, .8, 'HTR', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax2.transAxes)
    ax2.set_yticks([0, 1, 2, 3])
    ax2.set_yticklabels(['None', 'WACL', 'WACR', 'HRC'])
    ax2.set_xticklabels([], visible=False)

    ax3.plot(RAW.DT, RAW.Stat_Temp_On.astype('int64'), label='HTR On')
    ax3.plot(RAW.DT, RAW.Stat_Temp_Mo.astype('int64'), label='AUTO')
    ax3.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax3.set_ylim([-0.1, 1.1])
    ax3.get_yaxis().set_visible(False)
    ax3.set_xlabel('Data Time')
    ax3.grid(True)
    # ax3.xaxis.set_major_formatter(myFmt)

    fig.tight_layout()
    fig.savefig(HK_DIR / 'INT_TEMP_RAW.png')

    if Interact:
        plt.show(block=False)

    # Search for PanCam CAL Processed Files
    CalPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*Cal_HKTM.pickle", SingleFile=True)
    if not CalPikFile:
        logger.warning("No file found - ABORTING")
        return

    Cal = pd.read_pickle(CalPikFile[0])

    gs2 = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    fig2 = plt.figure(figsize=(14.0, 9.0))
    ax3 = fig2.add_subplot(gs2[0])
    ax4 = fig2.add_subplot(gs2[1], sharex=ax3)

    ax3.plot(Cal.DT, Cal.Temp_LFW,  label='LFW')
    ax3.plot(Cal.DT, Cal.Temp_RFW,  label='RFW')
    ax3.plot(Cal.DT, Cal.Temp_HRC,  label='HRC')
    ax3.plot(Cal.DT, Cal.Temp_LWAC, label='LWAC')
    ax3.plot(Cal.DT, Cal.Temp_RWAC, label='RWAC')
    ax3.plot(Cal.DT, Cal.Temp_HRCA, label='ACT')
    ax3.grid(True)
    ax3.set_ylabel('Temp [$^\circ$C]')
    ax3.legend(loc='lower center', bbox_to_anchor=(
        0.5, 1.0), ncol=5, borderaxespad=0, frameon=False)
    ax3.set_xticklabels([], visible=False)

    ax4.plot(Cal.DT, Cal.Temp_LDO, '-k', label='LDO')
    ax4.grid(True)
    ax4.set_ylabel('LDO Temp [$^\circ$C]')
    # ax4.xaxis.set_major_formatter(myFmt)

    fig2.tight_layout()
    fig2.savefig(HK_DIR / 'INT_TEMP_CAL.png')

    if Interact:
        plt.show(block=True)

    plt.close(fig)
    plt.close(fig2)

    logger.info("Producing Temperature Plots Completed")


def Rover_Temperatures(PROC_DIR, Interact=False):
    """"Produces a Rover temperature plot from pickle files"""

    logger.info("Producing Rover Temperature Plot")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam Rover Status Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RoverStatus.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    ROV = pd.read_pickle(RawPikFile[0])

    # Search for PanCam Rover Temperature Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RoverTemps.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    TMP = pd.read_pickle(RawPikFile[0])

    # Rover Temperatures
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    fig = plt.figure(figsize=(14.0, 9.0))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)

    ax0.plot(TMP.DT, TMP.PIU_T.astype('int64'), label='PIU')
    ax0.plot(TMP.DT, TMP.DCDC_T.astype('int64'), label='DCDC')
    ax0.legend(loc='upper right', frameon=False)
    ax0.set_ylabel('Rover Monitored \n Temperature [$^\circ$C]')
    ax0.grid(True)
    ax0.set_xticklabels([], visible=False)

    ax1.plot(ROV.DT, ROV.HTR_ST.astype('int64'), label='Heater Status')
    ax1.text(.99, .9, 'Rover Heater Status', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax1.transAxes)
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position('right')
    ax1.set_xlabel('')
    ax1.set_ylabel('LDO RAW [ENG]')
    ax1.grid(True)
    ax1.set_ylim([-0.1, 1.1])
    ax1.get_yaxis().set_visible(False)
    ax1.set_xlabel('Date Time')
    # ax1.xaxis.set_major_formatter(myFmt)

    fig.tight_layout()
    fig.savefig(HK_DIR / 'ROV_TEMPS.png')

    if Interact:
        plt.show()

    plt.close(fig)

    logger.info("Producing Rover Temperature Plot Completed")


def Rover_Power(PROC_DIR, Interact=False):
    """"Produces a Rover power consumption plot from pickle files"""

    logger.info("Producing Rover Power Plot")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam Rover Status Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RoverStatus.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    ROV = pd.read_pickle(RawPikFile[0])

    # Rover Current and Status Plot
    gs = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
    fig = plt.figure(figsize=(14.0, 9.0))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)

    ax0.plot(ROV.DT, ROV.Inst_Curr, label='Instr.')
    ax0.plot(ROV.DT, ROV.HTR_Curr, label='HTR')
    ax0.legend(loc='upper right')
    ax0.set_ylabel('Current [A]')
    ax0.grid(True)
    ax0.set_xticklabels([], visible=False)

    ax1.plot(ROV.DT, ROV.PWR_ST, label='Instr.')
    ax1.plot(ROV.DT, ROV.HTR_ST, label='HTR')
    ax1.text(.99, .9, 'Status', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax1.transAxes)
    ax1.yaxis.tick_right()
    ax1.yaxis.set_label_position('right')
    ax1.set_xlabel('')
    ax1.set_ylabel('Status')
    ax1.grid(True)
    ax1.set_ylim([-0.1, 1.1])
    ax1.get_yaxis().set_visible(False)
    ax1.set_xlabel('Date Time')
    # ax1.xaxis.set_major_formatter(myFmt)

    fig.tight_layout()
    fig.savefig(HK_DIR / 'ROV_PWR.png')

    if Interact:
        plt.show(block=False)

    plt.close(fig)

    # Rover Status and Power Extract
    ACT = ROV[(ROV.PWR_ST > 0) | (ROV.HTR_ST > 0)]
    if not ACT.empty:
        gs2 = gridspec.GridSpec(2, 1, height_ratios=[3, 1])
        fig2 = plt.figure(figsize=(14.0, 9.0))
        ax2 = fig2.add_subplot(gs2[0])
        ax3 = fig2.add_subplot(gs2[1], sharex=ax2)

        ax2.plot(ACT.DT, ACT.Inst_Curr, label='Instr.')
        ax2.plot(ACT.DT, ACT.HTR_Curr, label='HTR')
        ax2.legend(loc='upper right')
        ax2.set_ylabel('Current [A]')
        ax2.grid(True)
        ax2.set_xticklabels([], visible=False)

        ax3.plot(ACT.DT, ACT.PWR_ST, '.', label='Instr.')
        ax3.plot(ACT.DT, ACT.HTR_ST, '.', label='HTR')
        ax3.text(.99, .9, 'Status', color='0.25', fontweight='bold',
                 horizontalalignment='right', transform=ax3.transAxes)
        ax3.yaxis.tick_right()
        ax3.yaxis.set_label_position('right')
        ax3.set_xlabel('')
        ax3.set_ylabel('Status')
        ax3.grid(True)
        ax3.set_ylim([-0.1, 1.1])
        ax3.get_yaxis().set_visible(False)
        ax3.set_xlabel('Date Time')
        # ax3.xaxis.set_major_formatter(myFmt)

        fig2.tight_layout()
        fig2.savefig(HK_DIR / 'ROV_PWR_EXT.png')

    if Interact:
        plt.show()

    plt.close(fig)

    logger.info("Producing Rover Power Plot Completed")


def HK_Overview(PROC_DIR, Interact=False):
    """"Produces an overview of the TCs, Power Status and Errors"""

    logger.info("Producing Overview Plot")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam RAW Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RAW_HKTM.pickle", SingleFile=True)
    if not RawPikFile:
        logger.info("No RAW_HKTM file found - ABORTING")
        return

    RAW = pd.read_pickle(RawPikFile[0])

    # Search for PanCam Rover Telecommands
    # May need to switch to detect if Rover TC or LabView TC
    TCPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*Unproc_TC.pickle", SingleFile=True)
    if not TCPikFile:
        logger.info("No TC file found - Leaving Blank")
        TC = pd.DataFrame()
        TCPlot = False
    else:
        TCPlot = True

    if TCPlot:
        TC = pd.read_pickle(TCPikFile[0])

    # RAW Plot and Heater
    gs = gridspec.GridSpec(5, 1, height_ratios=[1, 0.5, 0.5, 0.5, 0.5])
    gs.update(hspace=0.0)
    fig = plt.figure(figsize=(14.0, 9.0))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    ax2 = fig.add_subplot(gs[2], sharex=ax0)
    ax3 = fig.add_subplot(gs[3], sharex=ax0)
    ax4 = fig.add_subplot(gs[4], sharex=ax0)

    # Action List
    if TCPlot:
        size = TC.shape[0]
        TC['LEVEL'] = 1
        markerline, stemline, baseline = ax0.stem(
            TC['DT'], TC['LEVEL'], linefmt='C3-', basefmt="k-", use_line_collection=True)
        plt.setp(markerline, mec="k", mfc="w", zorder=3)
        markerline.set_ydata(np.zeros(size))
        for i in range(0, size):
            ax0.annotate(TC.ACTION.iloc[i], xy=(TC.DT.iloc[i], TC.LEVEL.iloc[i]), xytext=(0, -2),
                         textcoords="offset points", va="top", ha="right", rotation=90)
    else:
        ax0.get_yaxis().set_visible(False)
    ax0.grid(True)
    ax0.text(.99, .95, 'Action List',
             horizontalalignment='right', transform=ax0.transAxes)

    # Cam Power and Enable
    ax1.plot(RAW.DT, RAW.Stat_PIU_En.astype('int64'), label='ENA')
    ax1.plot(RAW.DT, RAW.Stat_PIU_Pw.astype('int64'), label='PWR')
    ax1.text(.99, .9, 'Cam ENA and PWR', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax1.transAxes)
    ax1.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax1.grid(True)
    ax1.set_yticks([0, 1, 2, 3])
    ax1.set_yticklabels(['None', 'WACL', 'WACR', 'HRC'])

    # PIU Errors
    ax2.plot(RAW.DT, RAW.ERR_1_CMD.astype('int64') != 0, '.', label='CMD')
    ax2.plot(RAW.DT, RAW.ERR_1_FW.astype('int64') != 0,  '.', label='FW')
    ax2.plot(RAW.DT, (RAW.ERR_2_LWAC.astype('int64') != 0) & (
        RAW.ERR_2_LWAC.astype('int64') != 0x4), '.', label='LWAC')
    ax2.plot(RAW.DT, (RAW.ERR_2_RWAC.astype('int64') != 0) & (
        RAW.ERR_2_RWAC.astype('int64') != 0x4), '.', label='RWAC')
    ax2.plot(RAW.DT, RAW.ERR_3_HRC.astype('int64') != 0,  '.', label='HRC')
    ax2.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax2.set_ylim([-0.1, 1.1])
    ax2.get_yaxis().set_visible(False)
    ax2.grid(True)
    ax2.text(.99, .9, 'Errors excl. WAC CMD TO', color='0.25',
             fontweight='bold', horizontalalignment='right', transform=ax2.transAxes)

    ax3.plot(RAW.DT, RAW.ERR_2_LWAC.astype('int64')
             == 0x4, '.', label='LWAC', color='C2')
    ax3.plot(RAW.DT, RAW.ERR_2_RWAC.astype('int64')
             == 0x4, '.', label='RWAC', color='C3')
    ax3.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax3.set_ylim([-0.1, 1.1])
    ax3.get_yaxis().set_visible(False)
    ax3.grid(True)
    ax3.text(.99, .9, 'WAC CMD TO Error', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax3.transAxes)
    # ax3.xaxis.set_major_formatter(myFmt)

    ax4.plot(RAW.DT, RAW.IMG_No)
    if ax4.get_ylim()[1] < 1:
        ax4.set_ylim([-0.1, 1.1])
    ax4.grid(True)
    ax4.text(.99, .9, 'Img #', color='0.25', fontweight='bold',
             horizontalalignment='right', transform=ax4.transAxes)
    ax4.set_xlabel('Date Time')

    fig.tight_layout()
    fig.savefig(HK_DIR / 'HK_OVR.png')

    if Interact:
        plt.show(block=True)

    plt.close(fig)

    logger.info("Producing Overview Plot Completed")


def HRC_CS(PROC_DIR, Interact=False):
    """"Produces a plot of the HRC Camera Status from pickle files"""

    logger.info("Producing HRC Status Plots")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam RAW Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RAW_HKTM.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    RAW = pd.read_pickle(RawPikFile[0])

    if RAW['HRC_ACK'].empty:
        logger.info("No HRC data available")
        return

    # Search for PanCam Rover Telecommands
    # May need to switch to detect if Rover TC or LabView TC
    TCPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*Unproc_TC.pickle", SingleFile=True)
    if not TCPikFile:
        logger.info("No TC file found - Leaving Blank")
        TC = pd.DataFrame()
        TCPlot = False
    else:
        TCPlot = True

    if TCPlot:
        TC = pd.read_pickle(TCPikFile[0])

    # Create plot structure
    gs = gridspec.GridSpec(7, 1, height_ratios=[
                           1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    gs.update(hspace=0.0)
    fig = plt.figure(figsize=(14.0, 9))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    ax2 = fig.add_subplot(gs[2], sharex=ax0)
    ax3 = fig.add_subplot(gs[3], sharex=ax0)
    ax4 = fig.add_subplot(gs[4], sharex=ax0)
    ax5 = fig.add_subplot(gs[5], sharex=ax0)
    ax6 = fig.add_subplot(gs[6], sharex=ax0)

    # Action List
    if TCPlot:
        size = TC.shape[0]
        TC['LEVEL'] = 1

        markerline, stemline, baseline = ax0.stem(
            TC['DT'], TC['LEVEL'], linefmt='C3-', basefmt="k-", use_line_collection=True)
        plt.setp(markerline, mec="k", mfc="w", zorder=3)
        markerline.set_ydata(np.zeros(size))
        ax0.text(.99, .9, 'Action List', horizontalalignment='right',
                 transform=ax0.transAxes)
        ax0.grid(True)
        for i in range(0, size):
            ax0.annotate(TC.ACTION.iloc[i], xy=(TC.DT.iloc[i], TC.LEVEL.iloc[i]), xytext=(0, -2),
                         textcoords="offset points", va="top", ha="right", rotation=90)
        ax0.set_xticklabels([], visible=False)

    # remove y axis and spines
    ax0.get_yaxis().set_visible(False)

    # Encoder Value
    ax1.plot(RAW['DT'], RAW['HRC_ENC'], '.')
    ax1.text(.99, .8, 'Enc Value', horizontalalignment='right',
             transform=ax1.transAxes)
    ax1.grid(True)
    ax1.set_xticklabels([], visible=False)

    # Enc and MM Flag
    ax2.plot(RAW['DT'], RAW['HRC_EPF'], label='Enc')
    ax2.plot(RAW['DT'], RAW['HRC_MMF'], '.', label='MM')
    ax2.text(.99, .8, 'ENC & MM', horizontalalignment='right',
             transform=ax2.transAxes)
    ax2.grid(True)
    ax2.set_ylim([-0.1, 1.1])
    ax2.yaxis.tick_right()
    ax2.yaxis.set_label_position('right')
    ax2.set_xticklabels([], visible=False)
    ax2.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax2.get_yaxis().set_visible(False)

    # AF and AI Flag
    ax3.plot(RAW['DT'], RAW['HRC_AFF'], label='AF')
    ax3.plot(RAW['DT'], RAW['HRC_AIF'], label='AI')
    ax3.text(.99, .8, 'AF & AI', horizontalalignment='right',
             transform=ax3.transAxes)
    ax3.grid(True)
    ax3.set_ylim([-0.1, 1.1])
    ax3.set_xticklabels([], visible=False)
    ax3.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax3.get_yaxis().set_visible(False)

    # Current Sharpness
    ax4.plot(RAW['DT'], RAW['HRC_CS'])
    ax4.text(.99, .8, 'Sharpness', horizontalalignment='right',
             transform=ax4.transAxes)
    ax4.grid(True)
    ax4.set_xticklabels([], visible=False)

    # Image Counter
    ax5.plot(RAW['DT'], RAW['HRC_IFC'], '.')
    ax5.text(.99, .8, 'IMG Count', horizontalalignment='right',
             transform=ax5.transAxes)
    ax5.grid(True)
    ax5.yaxis.tick_right()
    plt.setp(ax5.get_yticklabels(), visible=False)
    ax5.yaxis.set_label_position('right')
    ax5.set_xticklabels([], visible=False)

    # Sensor Temp
    ax6.plot(RAW['DT'], RAW['HRC_TP'])
    ax6.text(.99, .8, 'RAW Sensor Temp',
             horizontalalignment='right', transform=ax6.transAxes)
    ax6.grid(True)

    # Re-adjust x-axis so that
    xlimits = ax0.get_xlim()
    new_xlimits = (xlimits[0], (xlimits[1] - xlimits[0])*1.1+xlimits[0])
    ax0.set_xlim(new_xlimits)

    fig.tight_layout()
    fig.savefig(HK_DIR / 'HRC_CS.png')

    if Interact:
        plt.show(block=True)

    plt.close(fig)

    logger.info("Producing HRC CS Plot Completed")


def FW(PROC_DIR, Interact=False):
    """"Produces a plot of the FW Status from pickle files"""

    logger.info("Producing FW Status Plots")

    HK_DIR = MakeHKPlotsDir(PROC_DIR)

    # Search for PanCam RAW Processed Files
    RawPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*RAW_HKTM.pickle", SingleFile=True)
    if not RawPikFile:
        logger.warning("No file found - ABORTING")
        return

    RAW = pd.read_pickle(RawPikFile[0])

    # Search for PanCam Rover Telecommands
    # May need to switch to detect if Rover TC or LabView TC
    TCPikFile = PC_Fns.Find_Files(
        PROC_DIR, "*Unproc_TC.pickle", SingleFile=True)
    if not TCPikFile:
        logger.info("No TC file found - Leaving Blank")
        TC = pd.DataFrame()
        TCPlot = False
    else:
        TCPlot = True

    if TCPlot:
        TC = pd.read_pickle(TCPikFile[0])

    # Create plot structure
    gs = gridspec.GridSpec(7, 1, height_ratios=[
                           1, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5])
    gs.update(hspace=0.0)
    fig = plt.figure(figsize=(14.0, 9))
    ax0 = fig.add_subplot(gs[0])
    ax1 = fig.add_subplot(gs[1], sharex=ax0)
    ax2 = fig.add_subplot(gs[2], sharex=ax0)
    ax3 = fig.add_subplot(gs[3], sharex=ax0)
    ax4 = fig.add_subplot(gs[4], sharex=ax0)
    ax5 = fig.add_subplot(gs[5], sharex=ax0)
    ax6 = fig.add_subplot(gs[6], sharex=ax0)

    # Action List
    if TCPlot:
        size = TC.shape[0]
        TC['LEVEL'] = 1

        markerline, stemline, baseline = ax0.stem(
            TC['DT'], TC['LEVEL'], linefmt='C3-', basefmt="k-", use_line_collection=True)
        plt.setp(markerline, mec="k", mfc="w", zorder=3)
        markerline.set_ydata(np.zeros(size))
        ax0.text(.99, .9, 'Action List', horizontalalignment='right',
                 transform=ax0.transAxes)
        ax0.grid(True)
        for i in range(0, size):
            ax0.annotate(TC.ACTION.iloc[i], xy=(TC.DT.iloc[i], TC.LEVEL.iloc[i]), xytext=(0, -2),
                         textcoords="offset points", va="top", ha="right", rotation=90)
        ax0.set_xticklabels([], visible=False)

    # remove y axis and spines
    ax0.get_yaxis().set_visible(False)

    # FW Running Flag
    ax1.plot(RAW['DT'], RAW['Stat_FWL_Op'], label='FWL')
    ax1.plot(RAW['DT'], RAW['Stat_FWR_Op'], label='FWR')
    ax1.text(.99, .8, 'Running', horizontalalignment='right',
             transform=ax1.transAxes)
    ax1.grid(True)
    ax1.set_ylim([-0.1, 1.1])
    ax1.legend(loc='center right', bbox_to_anchor=(
        1.0, 0.5), ncol=1, borderaxespad=0, frameon=False)
    ax1.set_xticklabels([], visible=False)
    ax1.get_yaxis().set_visible(False)

    # FW Home Flag
    ax2.plot(RAW['DT'], RAW['Stat_FWL_Ho'], label='FWL')
    ax2.plot(RAW['DT'], RAW['Stat_FWR_Ho'], label='FWR')
    ax2.text(.99, .8, 'Home', horizontalalignment='right',
             transform=ax2.transAxes)
    ax2.grid(True)
    ax2.set_ylim([-0.1, 1.1])
    ax2.yaxis.tick_right()
    ax2.set_xticklabels([], visible=False)
    ax2.get_yaxis().set_visible(False)

    # FW Index Flag
    ax3.plot(RAW['DT'], RAW['Stat_FWL_Id'], label='FWL')
    ax3.plot(RAW['DT'], RAW['Stat_FWR_Id'], label='FWR')
    ax3.text(.99, .8, 'Index', horizontalalignment='right',
             transform=ax3.transAxes)
    ax3.grid(True)
    ax3.set_ylim([-0.1, 1.1])
    ax3.set_xticklabels([], visible=False)
    ax3.get_yaxis().set_visible(False)

    # FW Position
    ax4.plot(RAW['DT'], RAW['Stat_FWL_Po'], label='FWL')
    ax4.plot(RAW['DT'], RAW['Stat_FWR_Po'], label='FWR')
    ax4.text(.99, .8, 'Position', horizontalalignment='right',
             transform=ax4.transAxes)
    ax4.grid(True)
    ax4.set_xticklabels([], visible=False)

    # Absolute Steps
    ax5.plot(RAW['DT'], RAW['FWL_ABS'], label='FWL')
    ax5.plot(RAW['DT'], RAW['FWR_ABS'], label='FWR')
    ax5.text(.99, .8, 'Absolute Steps',
             horizontalalignment='right', transform=ax5.transAxes)
    ax5.grid(True)
    ax5.yaxis.tick_right()
    ax5.yaxis.set_label_position('right')
    ax5.set_xticklabels([], visible=False)

    # Relative Steps
    ax6.plot(RAW['DT'], RAW['FWL_REL'], label='FWL')
    ax6.plot(RAW['DT'], RAW['FWR_REL'], label='FWR')
    ax6.text(.99, .8, 'Relative Steps',
             horizontalalignment='right', transform=ax6.transAxes)
    ax6.grid(True)

    # Re-adjust x-axis so that
    xlimits = ax0.get_xlim()
    new_xlimits = (xlimits[0], (xlimits[1] - xlimits[0])*1.1+xlimits[0])
    ax0.set_xlim(new_xlimits)

    fig.tight_layout()
    fig.savefig(HK_DIR / 'FW.png')

    if Interact:
        plt.show(block=True)

    plt.close(fig)

    logger.info("Producing FW Status Plot Completed")


if __name__ == "__main__":
    DIR = Path(
        input("Type the path to the PROC folder where the processed files are stored: "))

    logging.basicConfig(filename=(DIR / 'processing.log'),
                        level=logging.INFO,
                        format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s')
    logger.info('\n\n\n\n')
    logger.info("Running Plotter.py as main")
    logger.info("Reading directory: %s", DIR)

    # HK_Temperatures(DIR)
    # Rover_Temperatures(DIR)
    # Rover_Power(DIR)
    HK_Overview(DIR, True)
    # HK_Voltages(DIR)
    #HRC_CS(DIR, True)
    #FW(DIR, Interact=True)
