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
import opcode
import warnings
import contextlib


# use a small hack to get back the setdefaultencoding function
_d = sys.__dict__.copy()
reload(sys)
_setdefaultencoding = sys.setdefaultencoding
sys.__dict__.clear()
sys.__dict__.update(_d)


class UnicodeConversionWarning(UnicodeWarning):
    """Warning issued for all kinds of unicode conversions that happen
    implicitly.
    """


class UnicodeComparisonWarning(UnicodeConversionWarning):
    """Unicode comparision warning.  These are especially critical to
    monitor because they will silently fail on Python 3.
    """


class UnicodeConcatenationWarning(UnicodeConversionWarning):
    """These are issued if concatenation between unicode and string is
    detected.  These will usually result in a runtime error on Python 3
    so they are easier to spot.
    """


def get_opcode(code, instruction):
    """Returns the best opcode match for the given code with it's argument"""
    i = 0
    extended_arg = 0
    codes = code.co_code
    end = len(codes)
    while i < end:
        c = codes[i]
        op = ord(c)
        i += 1
        if op >= opcode.HAVE_ARGUMENT:
            oparg = ord(codes[i]) + ord(codes[i + 1]) * 256 + extended_arg
            extended_arg = 0
            i += 2
            if op == opcode.EXTENDED_ARG:
                extended_arg = oparg << 16
        else:
            oparg = 0
        if i >= instruction:
            return op, oparg
    return None, None


def get_warning(frame, target):
    """Returns the best possible warning for the given frame."""
    cls = UnicodeConversionWarning
    buffer = []
    if target is str:
        buffer.append('Implicit conversion of unicode to str.')
    elif target is unicode:
        buffer.append('Implicit conversion of str to unicode.')
    if frame is not None:
        op, arg = get_opcode(frame.f_code, frame.f_lasti + 1)
        if op == opcode.opmap['COMPARE_OP']:
            cls = UnicodeComparisonWarning
            buffer.append('Conversion happened when attempting to compare '
                          'two strings of different types.  This will '
                          'silently fail without warning on Python 3.')
        elif op == opcode.opmap['BINARY_ADD']:
            cls = UnicodeConcatenationWarning
            buffer.append('Conversion happened when attempting to '
                          'concatenate strings of different types.')
    return cls(' '.join(buffer))


def warning_encode(input, errors='strict'):
    warnings.warn(get_warning(sys._getframe(1), target=str),
                  stacklevel=2)
    return codecs.ascii_encode(input, errors)


def warning_decode(input, errors='strict'):
    warnings.warn(get_warning(sys._getframe(1), target=unicode),
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
    """Enable or disable the unicode nazi for a block (not threadsafe)."""
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


def main():
    """Run the unicode nazi as script."""
    global __name__
    __name__ = 'unicodenazi'
    if len(sys.argv) < 2:
        print >> sys.stderr, 'usage: python -municodenazi script'
        sys.exit(1)
    import imp
    main_mod = imp.new_module('__main__')
    if '__name__' in sys.modules:
        sys.modules['unicodenazi'] = sys.modules['__name__']
    sys.modules['__name__'] = main_mod
    del sys.argv[0]
    execfile(sys.argv[0], main_mod.__dict__)


# register codec and enable
codecs.register(search_function)
enable()


if __name__=="__main__":
    main()
