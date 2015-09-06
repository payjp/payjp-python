# coding: utf-8

import sys

def utf8(value):
    if sys.version_info < (3, 0) and isinstance(value, unicode):
        return value.encode('utf-8')
    else:
        return value
