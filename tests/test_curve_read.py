import dlisio
dlisio.set_encodings(['latin1'])
import os
import sys

def test_curve_read():
    root = os.path.dirname( __file__ )
    file = 'data/COP_Pharos-1__VISION Service_CUSTOMER_482.11-5220.00mMD.dlis'
    filepath = os.path.abspath(os.path.join(root, file))
    curves_L = []
    with dlisio.load(filepath) as logfile:
        for d in logfile:
            for fram in d.frames:
                for channel in fram.channels:
                    curves = channel.curves()
                    curves_L.append(curves)
    assert len(curves_L) > 0
