from unittest import TestCase
from unittest.mock import patch
import subprocess
from collections import namedtuple

from blower_tester import dut_tests
from blower_tester.config import conf

class mock_ftdi:
    device_node = 'dummy'

    def get(arg):
        if arg   == 'ID_VENDOR_ID': return conf['ftdi']['vid']
        elif arg == 'ID_MODEL_ID':  return conf['ftdi']['pid']
        else: raise ValueError

class mock_device_descriptor:
    sn = 'mock_dev'

room_temp = 25

class TestGroup(TestCase):
    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('subprocess.check_call')
    def test_set_mcu_option_bytes_pass(self, mock_sp_check_call,
                                             mock_on, mock_off,  mock_sleep):
        err, _ = dut_tests.set_mcu_option_bytes()
        assert err == False

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('subprocess.check_call',
                       side_effect=subprocess.CalledProcessError('cmd', 1))
    def test_set_mcu_option_bytes_fail(self, mock_sp_check_call,
                                             mock_on, mock_off, mock_sleep):
        err, err_str = dut_tests.set_mcu_option_bytes()
        assert err == True
        assert err_str == conf['stm']['fail_desig']

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('blower_tester.dut_tests.Ftdi.list_devices',
                                         return_value=[[mock_device_descriptor]])
    @patch('subprocess.check_call')
    def test_configure_ftdi_pass(self, mock_sp_check_call, mock_ftdi_devices,
                                 mock_on, mock_off, mock_sleep):
        err, _ = dut_tests.configure_ftdi()
        assert err == False

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('blower_tester.dut_tests.Ftdi.list_devices', return_value=None)
    @patch('subprocess.check_call')
    def test_configure_ftdi_fail(self, mock_sp_check_call, mock_ftdi_devices,
                                       mock_on, mock_off, mock_sleep):
        err, err_str = dut_tests.configure_ftdi()
        assert err == True
        assert err_str == conf['ftdi']['fail_desig']

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('pyudev.Context.list_devices', return_value=[mock_ftdi])
    @patch('subprocess.check_call')
    def test_prog_mcu_pass(self, mock_sp_check_call, mock_devices,
                                 mock_on, mock_off, mock_sleep):
        err, _ = dut_tests.program_microcontroller()
        assert err == False

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('pyudev.Context.list_devices', return_value=[])
    @patch('subprocess.check_call')
    def test_prog_mcu_no_ftdi(self, mock_sp_check_call, mock_devices,
                                    mock_on, mock_off, mock_sleep):
        err, err_str = dut_tests.program_microcontroller()
        assert err == True
        assert err_str == conf['stm']['fail_desig']

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('pyudev.Context.list_devices', return_value=[mock_ftdi])
    def test_prog_mcu_error(self, mock_devices,
                                  mock_on, mock_off, mock_sleep):
        err, err_str = dut_tests.program_microcontroller()
        assert err == True
        assert err_str == conf['stm']['fail_desig']

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.get_firmware_version', return_value=False)
    def test_check_fw_version_pass(self, mock_check_fw_version, mock_sleep):
        err, _ = dut_tests.check_fw_version()
        assert err == False

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.get_firmware_version', return_value=True)
    def test_check_fw_version_fail(self, mock_check_firmware_version, mock_sleep):
        err, err_str = dut_tests.check_fw_version()
        assert err == True
        assert err_str == conf['spi']['fail_desig']

    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    @patch('blower_tester.dut_tests.get_hdc_temp', return_value=room_temp)
    def test_onboard_temp_pass(self, mock_hdc_temp, mock_tmp_temp):
        err, _ = dut_tests.check_onboard_temp()
        assert err == False

    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    @patch('blower_tester.dut_tests.get_hdc_temp',
                      return_value=conf["hdc"]["max_temp"] + 1)
    def test_onboard_temp_fail(self, mock_hdc_temp, mock_tmp_temp):
        err, err_str = dut_tests.check_onboard_temp()
        assert err == True
        assert err_str == conf["hdc"]["fail_desig"]

    @patch('blower_tester.dut_tests.get_tc_temp', return_value=room_temp)
    def test_thermocouple_pass(self, mock_tmp_temp):
        err = dut_tests._check_thermocouple(1)
        assert err == False

    @patch('blower_tester.dut_tests.get_tc_temp',
                     return_value=conf["tc"]["min_temp"] - 1)
    def test_thermocouple_fail(self, mock_tmp_temp):
        err = dut_tests._check_thermocouple(1)
        assert err == True

    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    def test_thermocouple_out_of_range(self, mock_tmp_temp):
        with self.assertRaises(ValueError):
            dut_tests._check_thermocouple(min(conf["tc"]["range"]) - 1)

        with self.assertRaises(ValueError):
            dut_tests._check_thermocouple(max(conf["tc"]["range"]) + 1)

    @patch('blower_tester.dut_tests.get_tc_temp', return_value=room_temp)
    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    def test_check_thermocouples_pass(self, mock_tmp1075_temp, mock_tc_temp):
        err, _ = dut_tests.check_thermocouples()
        assert err == False

    @patch('blower_tester.dut_tests.get_tc_temp')
    @patch('blower_tester.dut_tests._tmp1075_temp', return_value=room_temp)
    def test_check_thermocouples_fail(self, mock_tmp1075_temp, mock_tc_temp):
        tc_temps = [room_temp for tc in conf['tc']['range']]
        tc_temps[-1] = conf["tc"]["max_temp"] + 1

        mock_tc_temp.side_effect = tc_temps
        err, err_str = dut_tests.check_thermocouples()
        assert err == True
        assert conf['tc']['fail_desig'] in err_str
        assert f"thermocouple channel {max(conf['tc']['range'])}" in err_str

    @patch('blower_tester.dut_tests.get_fan_speed',
            return_value=conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0)
    def test_fan_pass(self, mock_gfs):
        err = dut_tests._check_fan(1, conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0)
        assert err == False

    @patch('blower_tester.dut_tests.get_fan_speed',
                return_value=(1 - 2 * conf["fan"]["tol"] / 100) \
                                    * conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0)
    def test_fan_fail(self, mock_gfs):
        err = dut_tests._check_fan(1, conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0)
        assert err == True

    def test_fan_out_of_range(self):
        with self.assertRaises(ValueError):
            dut_tests.get_fan_speed(None, min(conf["fan"]["range"]) - 1)

        with self.assertRaises(ValueError):
            dut_tests.get_fan_speed(None, max(conf["fan"]["range"]) + 1)

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.get_fan_speed',
            return_value=conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0)
    def test_fans_pass(self, mock_fan_speeds, mock_sleep):
        err, _ = dut_tests.check_fans()
        assert err == False

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.get_fan_speed')
    def test_fans_fail(self, mock_fan_speeds, mock_sleep):
        fan_speeds = [conf["fan"]["speed"] for fan in conf['fan']['range']]
        fan_speeds[-1] = (1 - 2 * conf["fan"]["tol"] / 100) * \
                          conf["fan"]["speed"] * conf["fan"]["duty"] / 100.0

        mock_fan_speeds.side_effect = fan_speeds
        err, err_str = dut_tests.check_fans()
        assert err == True
        assert conf['fan']['fail_desig'] in err_str
        assert f"fan channel {max(conf['fan']['range'])}" in err_str

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('pyudev.Context.list_devices', return_value=[mock_ftdi])
    @patch('subprocess.check_call')
    def test_erase_mcu_pass(self, mock_sp_check_call, mock_devices,
                                 mock_on, mock_off, mock_sleep):
        err, _ = dut_tests.erase_mcu_flash()
        assert err == False

    @patch('time.sleep')
    @patch('blower_tester.dut_tests.dut_pwr_off')
    @patch('blower_tester.dut_tests.dut_pwr_on')
    @patch('pyudev.Context.list_devices', return_value=[mock_ftdi])
    def test_erase_mcu_error(self, mock_devices,
                                  mock_on, mock_off, mock_sleep):
        err, err_str = dut_tests.erase_mcu_flash()
        assert err == True
        assert err_str == conf['stm']['fail_desig']