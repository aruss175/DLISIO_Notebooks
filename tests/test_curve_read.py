import dlisio
def test_curve_read():
    curves_L = []
    file = 'data/COP_Pharos-1__VISION Service_CUSTOMER_482.11-5220.00mMD.dlis'
    with dlisio.load(file) as logfile:
        for d in logfile:
            for channel in d.channels:
                curves = channel.curves()
                curves_L.append(curves)
    assert len(curves_L) > 0
