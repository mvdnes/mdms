"""
usage: mdms test
"""

from docopt import docopt
import unittest

def main(argv):
    args = docopt(__doc__, argv = argv)
    suite = unittest.TestLoader().discover('tests', pattern = "test_*.py")
    unittest.TextTestRunner(verbosity=2).run(suite)
