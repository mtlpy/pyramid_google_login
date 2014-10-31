import unittest

import mock


class Test(unittest.TestCase):

    def test_encode_state(self):
        from pyramid_google_login.google_oauth2 import encode_state

        tested = [('param1', 'value1'),
                  ('param2', 'value2'),
                  ('param2', 'value3')]
        resp = encode_state(tested)
        expected = 'param1=value1&param2=value2&param2=value3'
        self.assertEqual(resp, expected)

    def test_decode_state(self):
        from pyramid_google_login.google_oauth2 import decode_state

        tested = 'param1=value1&param2=value2&param2=value3'
        resp = decode_state(tested)
        expected = {'param1': ['value1'], 'param2': ['value2', 'value3']}
        self.assertEqual(resp, expected)
