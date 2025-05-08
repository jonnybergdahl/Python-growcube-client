#!/usr/bin/env python3
import unittest

# Import all test modules
from tests import growcubecommand_tests
from tests import growcubemessage_tests
from tests import growcubereport_tests
from tests import growcubeclient_tests
from tests import growcubeprotocol_tests
from tests import growcubediscovery_tests
from tests import growcubeenums_tests

# Create a test suite
def create_test_suite():
    test_suite = unittest.TestSuite()
    
    # Add test cases from each module
    test_suite.addTest(unittest.makeSuite(growcubecommand_tests.GrowCubeCommandTestCase))
    test_suite.addTest(unittest.makeSuite(growcubemessage_tests.GrowCubeMessageTestCase))
    test_suite.addTest(unittest.makeSuite(growcubereport_tests.GrowCubeReportTestCase))
    test_suite.addTest(unittest.makeSuite(growcubeclient_tests.GrowcubeClientTestCase))
    test_suite.addTest(unittest.makeSuite(growcubeprotocol_tests.GrowcubeProtocolTestCase))
    test_suite.addTest(unittest.makeSuite(growcubediscovery_tests.GrowcubeDiscoveryTestCase))
    test_suite.addTest(unittest.makeSuite(growcubeenums_tests.GrowcubeEnumsTestCase))
    
    return test_suite

if __name__ == '__main__':
    # Create and run the test suite
    test_suite = create_test_suite()
    test_runner = unittest.TextTestRunner()
    test_runner.run(test_suite)
    
    print("\nNote: Some tests for async code may show warnings about coroutines never being awaited.")
    print("This is expected with the standard unittest runner and doesn't affect test validity.")