import dlisio

def test_header_origin():
    file = 'data/semantic.dlis'
    with dlisio.load(file) as logfile:
        for d in logfile:
            for origin in d.origins:
                originlength = len(str(origin))
    assert originlength > 0
