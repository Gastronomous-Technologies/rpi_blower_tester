from collections import namedtuple
from unittest.mock import patch

from blower_tester import blower_main

dut_test = namedtuple("dut_test", ["name", "func"])

def dummy_test_pass(): return False, None
def dummy_test_fail(): return True,  "bob loblaw"

class TestGroup:

    @patch('blower_tester.blower_main.get_test_seq',
                       return_value=[dut_test("test descript", dummy_test_pass)])
    @patch('blower_tester.blower_main.dut_pwr_off')
    @patch('blower_tester.blower_main.dut_pwr_on')
    def test_brd_pass(self, mock_dut_pwr_on, mock_dut_pwr_off, mock_tseq):
        brd_err = blower_main.test_brd()
        assert brd_err == False

    @patch('blower_tester.blower_main.get_test_seq',
                       return_value=[dut_test("test descript", dummy_test_fail)])
    @patch('blower_tester.blower_main.dut_pwr_off')
    @patch('blower_tester.blower_main.dut_pwr_on')
    def test_brd_fail(self, mock_dut_pwr_on, mock_dut_pwr_off, mock_tseq):
        brd_err = blower_main.test_brd()
        assert brd_err == True
