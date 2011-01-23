# -*- coding: utf-8 -*-
"""
    unicodenazi
    ~~~~~~~~~~~

    Annoying but helpful helper to find improper use of unicode and
    bytestring conversions.

    :copyright: (c) 2011 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""
import sys
import codecs
import warnings
import contextlib


# use a small hack to get back the setdefaultencoding function
_d = sys.__dict__.copy()
reload(sys)
_setdefaultencoding = sys.setdefaultencoding
sys.__dict__.clear()
sys.__dict__.update(_d)


def warning_encode(input, errors='strict'):
    warnings.warn(UnicodeWarning('Implicit conversion of unicode to str'),
                  stacklevel=2)
    return codecs.ascii_encode(input, errors)


def warning_decode(input, errors='strict'):
    warnings.warn(UnicodeWarning('Implicit conversion of str to unicode'),
                  stacklevel=2)
    return codecs.ascii_decode(input, errors)


class Codec(codecs.Codec):
    encode = staticmethod(warning_encode)
    decode = staticmethod(warning_decode)


class IncrementalEncoder(codecs.IncrementalEncoder):
    def encode(self, input, final=False):
        return warning_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):
    def decode(self, input, final=False):
        return warning_decode(input, self.errors)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def search_function(encoding):
    if encoding != 'unicode-nazi':
        return
    return codecs.CodecInfo(
        name='unicode-nazi',
        encode=warning_encode,
        decode=warning_decode,
        incrementalencoder=IncrementalEncoder,
        incrementaldecoder=IncrementalDecoder,
        streamwriter=StreamWriter,
        streamreader=StreamReader
    )


def enable():
    """Enable Unicode warnings"""
    _setdefaultencoding('unicode-nazi')


def disable():
    """Disable unicode warnings"""
    _setdefaultencoding('ascii')


def is_active():
    """Is the unicodenazi active?"""
    return sys.getdefaultencoding() == 'unicode-nazi'


@contextlib.contextmanager
def blockwise(enabled=True):
    if enabled:
        enable()
    else:
        disable()
    try:
        yield
    finally:
        if enabled:
            disable()
        else:
            enable()


# register codec and enable
codecs.register(search_function)
enable()


if __name__=="__main__":
    if len(sys.argv) > 1:
        scriptpath = sys.argv[1]
        del sys.argv[0]
        execfile(scriptpath)
