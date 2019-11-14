import dlisio
import os
import sys

def test_header_origin():
    root = os.path.dirname( __file__ )
    file = 'data/semantic.dlis'
    filepath = os.path.abspath(os.path.join(root, file))
    with dlisio.load(filepath) as logfile:
        for d in logfile:
            for origin in d.origins:
                originlength = len(str(origin))
    assert originlength > 0
