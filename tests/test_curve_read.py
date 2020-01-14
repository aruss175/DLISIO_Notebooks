import dlisio
dlisio.set_encodings(['latin1'])
import os
import sys

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
