import unittest
import test_login_create

suite = unittest.TestLoader().loadTestsFromModule(test_login_create)

unittest.TextTestRunner().run(suite)