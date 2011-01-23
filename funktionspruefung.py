import unicodenazi
import unittest
import warnings

from contextlib import contextmanager


@contextmanager
def catch_warnings():
    """Catch warnings in a with block in a list"""
    filters = warnings.filters
    warnings.filters = filters[:]
    old_showwarning = warnings.showwarning
    log = []
    def showwarning(message, category, filename, lineno, file=None, line=None):
        log.append(locals())
    try:
        warnings.showwarning = showwarning
        yield log
    finally:
        warnings.filters = filters
        warnings.showwarning = old_showwarning


class BaseTest(unittest.TestCase):

    def test_compare_error(self):
        with catch_warnings() as log:
            a = 'foo' == u'foo'
            self.assertEqual(len(log), 1)
            self.assertEqual(log[0]['message'].__class__,
                             unicodenazi.UnicodeComparisonWarning)
            self.assertEqual(str(log[0]['message']),
                'Implicit conversion of str to unicode. Conversion happened '
                'when attempting to compare two strings of different types.  '
                'This will silently fail without warning on Python 3.')

    def test_concat_error(self):
        with catch_warnings() as log:
            b = 'foo' + [u'foo'][0] # no constant folding fool
            self.assertEqual(len(log), 1)
            self.assertEqual(log[0]['message'].__class__,
                             unicodenazi.UnicodeConcatenationWarning)
            self.assertEqual(str(log[0]['message']),
                'Implicit conversion of str to unicode. Conversion happened '
                'when attempting to concatenate strings of different types.')

    def test_regular_errors(self):
        with catch_warnings() as log:
            a = unicode('foo')
            b = str(u'foo')
            self.assertEqual(len(log), 2)
            self.assertEqual(log[0]['message'].__class__,
                             unicodenazi.UnicodeConversionWarning)
            self.assertEqual(str(log[0]['message']),
                             'Implicit conversion of str to unicode.')
            self.assertEqual(log[1]['message'].__class__,
                             unicodenazi.UnicodeConversionWarning)
            self.assertEqual(str(log[1]['message']),
                             'Implicit conversion of unicode to str.')


if __name__ == '__main__':
    unittest.main()
