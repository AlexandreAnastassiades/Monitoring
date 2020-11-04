# pylint: disable-all
""" Monitoring project methods , getting data from aws server  , test module"""
import unittest
from app import *

class TestAwsSSH(unittest.TestCase):
    """ Class testing the methods """
    SERVER_ONE = "52.4.91.83"
    LOGIN_SERVER_ONE = "interfadm"
    PASS_SERVER_ONE = "Projet654!"

    def test_get_data_error_pages(self):
        """ check if we really do return number of error page """
        print("test_get_data_error_pages")
        self.assertTrue(get_access_log_data_error_pages(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE))

    def test_get_ram_data_total(self):
        """ check the total memory  """
        print("test_get_ram_data_total")
        self.assertGreater(get_ram_data(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)[0], 0)

    def test_get_ram_data_free(self):
        """ check the free memory  """
        print("test_get_ram_data_free")
        self.assertGreater(get_ram_data(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)[1], 0)

    def test_get_ram_data_available(self):
        """ check the available memory """
        print("test_get_ram_data_available")
        self.assertGreater(get_ram_data(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)[2], 0)

    def test_get_processor_used(self):
        """ check the cpu usage """
        print("test_get_processor_used")
        self.assertGreater(float(get_processor_used(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)), 0)


    def test_stdout_page_one_data(self):
        """ Check the number of http connectionsto page one  """
        print("test_stdout_page_one_data")
        self.assertGreater(get_http_connections(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)["page1"], 0)

    def test_stdout_page_two_data(self):
        """ Check the number of http connections  to page two """
        print("test_stdout_page_two_data")
        self.assertGreaterEqual(get_http_connections(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)["page2"], 0)

    def test_stdout_page_three_data(self):
        """ Check the number of http connections  to page three"""
        print("test_stdout_page_three_data")
        self.assertGreaterEqual(get_http_connections(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)["page3"], 0)

    def test_stdout_index_data(self):
        """ Check the number of http connections  to index"""
        print("test_stdout_index_data")
        self.assertGreaterEqual(get_http_connections(
            self.SERVER_ONE, self.LOGIN_SERVER_ONE, self.PASS_SERVER_ONE)["index"], 0)


if __name__ == '__main__':
    unittest.main()
