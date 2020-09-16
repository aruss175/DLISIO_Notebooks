import dlisio
dlisio.set_encodings(['latin1'])
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from func_dlis_to_las import move_valid_index_to_first_col

def test_curve_read():
    root = os.path.dirname( __file__ )
    file = 'data/COP_Pharos-1__VISION Service_CUSTOMER_482.11-5220.00mMD.dlis'
    filepath = os.path.abspath(os.path.join(root, file))
    with dlisio.load(filepath) as logfile:
        for d in logfile:
            depth_channels = d.match('TDEP')
            for channel in depth_channels:
                depth_array = channel.curves()
                print(len(depth_array))
    assert len(depth_array) > 0


def test_index_is_first_col():
    curves_name = ['TDEP', 'DEPTH']
    reordered_curves = move_valid_index_to_first_col(curves_name)
    assert reordered_curves[0] == 'DEPTH'
    assert reordered_curves[1] == 'TDEP'
