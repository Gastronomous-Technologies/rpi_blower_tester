from collections import namedtuple
from unittest.mock import patch, Mock

from blower_tester import blower_main

dut_test = namedtuple("dut_test", ["name", "func", "prompt", "debug_prompt"])

def man_test(): pass
def auto_test(): pass
def auto_test_bad(): "bad"

class TestGroup:
    @patch('builtins.input', return_value='y')
    @patch('blower_tester.blower_main.get_test_seq')
    @patch('blower_tester.blower_main.pwr_off')
    @patch('blower_tester.blower_main.pwr_on')
    def test_good_brd(self, mock_pwr_on, mock_pwr_off, mock_tseq, mock_in):

        test_seq = [
            dut_test("man test",   man_test,  "bob", "loblaw"),
            dut_test("auto test",  auto_test, None,   None),
        ]
        mock_tseq.return_value = test_seq

        brd_err = blower_main.test_brd()
        assert brd_err == False

    @patch('builtins.input', return_value='e')
    @patch('blower_tester.blower_main.get_test_seq')
    @patch('blower_tester.blower_main.pwr_off')
    @patch('blower_tester.blower_main.pwr_on')
    def test_man_fail_brd(self, mock_pwr_on, mock_pwr_off, mock_tseq, mock_in):

        test_seq = [
            dut_test("man test",   man_test,  "bob", "loblaw"),
            dut_test("auto test",  auto_test, None,   None),
        ]
        mock_tseq.return_value = test_seq

        brd_err = blower_main.test_brd()
        assert brd_err

    @patch('builtins.input', return_value='e')
    @patch('blower_tester.blower_main.get_test_seq')
    @patch('blower_tester.blower_main.pwr_off')
    @patch('blower_tester.blower_main.pwr_on')
    def test_auto_fail_brd(self, mock_pwr_on, mock_pwr_off, mock_tseq, mock_in):

        test_seq = [
            dut_test("man test",   man_test,     "bob", "loblaw"),
            dut_test("auto test",  auto_test,    None,   None),
            dut_test("auto fail", auto_test_bad, None,   None)
        ]

        mock_tseq.return_value = test_seq

        brd_err = blower_main.test_brd()
        assert brd_err