#!/bin/bash
#
# Power the DUT on and open a serial monitor to its FT231X on this Pi.
#
# Drives the board power-enable (GPIO26, active-high) high, waits for the
# FT231X to enumerate, then connects at 115200 8N1 and resets the STM32 into
# its application so the USART1 telemetry streams:
#   RTS = LOW   -> BOOT0 selects boot-from-flash (run the app)
#   DTR pulse   -> assert then release reset, so the app restarts and prints
# RTS=high would hold the MCU boot-selected (bootloader) and the port stays
# silent. This is the same polarity stm32flash uses: RTS=1 to enter the
# bootloader, RTS=0 to run the application.
#
# Hold until Ctrl-C, then the board is powered back off on exit.
#
# GPIO26 matches blower_tester/blower_tester/config.py:
#   dut_pwr_en = OutputDevice(26, initial_value=False)
#
# Usage:
#   ./power_on_dut.sh                # power GPIO26, monitor /dev/ttyUSB0
#   ./power_on_dut.sh /dev/ttyUSB1   # explicit serial device
#
# Run with the blower_tester service stopped so it isn't also driving the GPIO:
#   sudo systemctl stop blower_tester.service

set -uo pipefail

PIN=26
DEV="${1:-/dev/ttyUSB0}"
BAUD=115200

if ! command -v pinctrl >/dev/null 2>&1; then
    echo "Error: 'pinctrl' not found (expected on Raspberry Pi OS)." >&2
    exit 1
fi

cleanup() {
    trap - INT TERM HUP EXIT      # disarm so this runs once
    pinctrl set "$PIN" op dl      # drive low -> power off
    echo
    echo "DUT power OFF (GPIO$PIN low). Exiting."
}
on_signal() { exit 0; }           # triggers the EXIT trap (-> cleanup)
trap on_signal INT TERM HUP
trap cleanup EXIT

# Power on
if ! pinctrl set "$PIN" op dh; then
    echo "Error: failed to drive GPIO$PIN high" >&2
    exit 1
fi
echo "DUT power ON (GPIO$PIN high)."

# Wait for the FT231X serial device to enumerate (up to ~10s)
printf "Waiting for %s ..." "$DEV"
for _ in $(seq 1 50); do
    [ -e "$DEV" ] && break
    sleep 0.2
done
if [ ! -e "$DEV" ]; then
    echo " not found."
    echo "FT231X did not enumerate at $DEV - check the USB/power connection." >&2
    exit 1
fi
echo " up."
echo "Connecting at ${BAUD} 8N1, RTS=low + DTR reset pulse (run app). Press Ctrl-C to power off and exit."
echo "----------------------------------------------------------------------------"

# Serial monitor: stdlib only (no pyserial/tio needed). Holds DTR+RTS high and
# reconnects across FT231X re-enumeration so a flapping bridge doesn't kill it.
SERIAL_DEV="$DEV" SERIAL_BAUD="$BAUD" python3 - <<'PY'
import os, sys, time, select, struct, fcntl, termios

dev  = os.environ["SERIAL_DEV"]
baud = getattr(termios, "B" + os.environ["SERIAL_BAUD"])

def open_port(path):
    fd = os.open(path, os.O_RDWR | os.O_NOCTTY | os.O_NONBLOCK)
    a = termios.tcgetattr(fd)
    a[0] = termios.IGNPAR                                   # iflag
    a[1] = 0                                                # oflag
    a[2] = termios.CS8 | termios.CREAD | termios.CLOCAL     # cflag: 8N1, no flow
    a[3] = 0                                                # lflag: raw
    a[4] = baud                                             # ispeed
    a[5] = baud                                             # ospeed
    termios.tcsetattr(fd, termios.TCSANOW, a)
    # Run the app (not the bootloader): RTS=low selects boot-from-flash, then
    # pulse DTR (assert reset, release) so the firmware restarts and streams its
    # USART1 telemetry. RTS=high would hold the MCU boot-selected -> silent.
    rts = struct.pack('I', termios.TIOCM_RTS)
    dtr = struct.pack('I', termios.TIOCM_DTR)
    fcntl.ioctl(fd, termios.TIOCMBIC, rts)   # RTS = low  (boot from flash)
    fcntl.ioctl(fd, termios.TIOCMBIS, dtr)   # DTR = high (assert reset)
    time.sleep(0.1)
    fcntl.ioctl(fd, termios.TIOCMBIC, dtr)   # DTR = low  (release reset -> run app)
    return fd

out = sys.stdout.buffer
try:
    while True:                       # reconnect loop (survives re-enumeration)
        try:
            fd = open_port(dev)
        except OSError:
            time.sleep(0.3); continue
        time.sleep(0.1)               # let DTR/RTS settle (the msleep(100) in tio)
        try:
            while True:
                r, _, _ = select.select([fd], [], [], 0.5)
                if fd in r:
                    data = os.read(fd, 4096)
                    if not data:      # EOF / disconnect
                        break
                    out.write(data); out.flush()
        except OSError:
            pass                      # bridge dropped; fall through to reopen
        finally:
            try: os.close(fd)
            except OSError: pass
        time.sleep(0.2)
except KeyboardInterrupt:
    pass
PY
