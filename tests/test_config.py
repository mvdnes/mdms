import unittest
import config

class ConfigTest(unittest.TestCase):
    def test_non_existing(self):
        self.assertRaises(OSError, config.parse, "")

    def test_malformed(self):
        self.assertRaises(Exception, config.parse ,"tests/config_fail.toml")

    def test_ok(self):
        v = config.parse("tests/config_ok.toml")
        expected = {
            'database': {
                'type': 'sqlite',
                'sqlite': {'file': 'dbmdms.db'},
            },
            'filesystem': {
                'location': 'data'
            },
        }
        self.assertEqual(v, expected)
