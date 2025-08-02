from unittest import TestCase
from unittest.mock import patch, Mock

from blower_tester import dut_tests
from blower_tester.config import conf
 
class TestGroup(TestCase):
    room_temp = 25

    @patch("time.sleep", return_value=None)
    @patch('subprocess.Popen')
    def test_prog_mcu_pass(self, mock_popen, mock_sleep):

        process_mock = Mock()
        attrs = {"communicate.return_value": 
                 (bytearray("output flash written and verified", 'utf-8'), 
                  bytearray("error", 'utf-8'))}

        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock

        err = dut_tests.prog_mcu()
        assert err == None

    @patch("time.sleep", return_value=None)
    @patch('subprocess.Popen')
    def test_prog_mcu_fail(self, mock_popen, mock_sleep):

        process_mock = Mock()
        attrs = {"communicate.return_value": 
                 (bytearray("output flash not written", 'utf-8'), 
                  bytearray("error", 'utf-8'))}

        process_mock.configure_mock(**attrs)
        mock_popen.return_value = process_mock

        err = dut_tests.prog_mcu()
        assert err

    @patch("time.sleep", return_value=None)
    def test_prog_mcu_error(self, mock_sleep):
        err = dut_tests.prog_mcu()
        assert err

    @patch('blower_tester.dut_tests.do_spi_ack', return_value=None)
    def test_spi_ack_pass(self, mock_spi_ack):
        err = dut_tests.spi_ack()
        assert err == None

    @patch('blower_tester.dut_tests.do_spi_ack', return_value="random error")
    def test_spi_ack_fail(self, mock_spi_ack):
        err = dut_tests.spi_ack()
        assert err

    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    def test_thermocouple_pass(self, mock_tmp_temp):
        err = dut_tests._check_tc(1, self.room_temp, 'a,b,c')
        assert err == None

    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    def test_thermocouple_fail(self, mock_tmp_temp):
        out_of_range_temp = (1 - 2 * conf["tc"]["tol"] / 100) * self.room_temp 
        err = dut_tests._check_tc(1, out_of_range_temp, 'a,b,c')
        assert err

    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    def test_thermocouple_out_of_range(self, mock_tmp_temp):
        with self.assertRaises(ValueError): 
            dut_tests.get_tc_temp(min(conf["tc"]["range"]) - 1)

        with self.assertRaises(ValueError): 
            dut_tests.get_tc_temp(max(conf["tc"]["range"]) + 1)

    @patch('blower_tester.dut_tests.get_fan_speed', return_value=conf["fan"]["speed"][1])
    def test_fan_pass(self, mock_gfs):
        err = dut_tests._check_fan(1, conf["fan"]["speed"][1], 'a,b,c')
        assert err == None
    
    @patch('blower_tester.dut_tests.get_fan_speed', 
                return_value=(1 - 2 * conf["fan"]["tol"] / 100) * conf["fan"]["speed"][1])
    def test_fan_fail(self, mock_gfs):
        err = dut_tests._check_fan(1, conf["fan"]["speed"][1], 'a,b,c')
        assert err

    def test_thermocouple_out_of_range(self):
        with self.assertRaises(ValueError): 
            dut_tests.get_fan_speed(max(conf["fan"]["range"]) + 1)