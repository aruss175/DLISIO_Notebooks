import os
import sys

import pandas as pd
import numpy as np
import dlisio

dlisio.set_encodings(["latin1"])

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Follows sys.path.insert so that func_dlis_to_las is found
from func_dlis_to_las import process_curve_info


def test_curve_read():
    root = os.path.dirname(__file__)
    file = "data/COP_Pharos-1__VISION Service_CUSTOMER_482.11-5220.00mMD.dlis"
    filepath = os.path.abspath(os.path.join(root, file))
    with dlisio.load(filepath) as logfile:
        for d in logfile:
            depth_channels = d.match("TDEP")
            for channel in depth_channels:
                depth_array = channel.curves()
                print(len(depth_array))
    assert len(depth_array) > 0


def test_process_curve_info():
    channel_data = {
        "curves_name": ["TDEP"],
        "longs": ["Tool Depth"],
        "unit": ["0.1 in"],
        "curve_df": pd.DataFrame(),
        "curves_L": [np.array([189810.0, 189820.0, 189830.0, 189840.0, 189850.0])],
        "las_units": [],
        "las_longs": [],
    }
    las_units, las_longs, curve_df, object_warning = process_curve_info(channel_data)
    assert las_units == ["0.1 in"]
    assert las_longs == ["Tool Depth"]
    assert len(curve_df) == 5
    assert len(curve_df.columns) == 1
    assert curve_df.columns[0] == "TDEP"
    assert curve_df["TDEP"].min() == 189810
