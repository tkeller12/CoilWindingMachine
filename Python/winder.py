import serial
from serial.tools import list_ports
import time


TIMEOUT = 1.0
BAUDRATE = 115200

MAX_ATTEMPTS = 1000

X_MIN = 0
X_MAX = 100

TURNS_MIN = -1000
TURNS_MAX = 1000

STEPS_PER_MM = 93.00
STEPS_PER_REV = 200.00
E_MICROSTEPS = 16.

E_MAX_RELATIVE_MOVE = 200.

MM_PER_REV = E_MICROSTEPS * STEPS_PER_REV / STEPS_PER_MM

class Winder:
    def __init__(self, port = None, verbose = False):
        if port is None:
            port = self.autodetect()
        self._port = port
        self._ser = None

        self.open()
        self.verbose = verbose
        self._abs_turns = 0

    def autodetect(self):
        for p in list_ports.comports():
            if p.vid == 6790:
                return p.device
        raise RuntimeError('Unable to Automatically detect serial port.\nPlease enter port manually')

    def open(self):
        print('Attempting to open serial...')
        if self._ser is not None:
            raise RuntimeError('Device connection already open')
        self._ser = serial.Serial(port = self._port, baudrate = BAUDRATE, timeout = TIMEOUT)

        print('Waiting for Initialization...')
        time.sleep(1)

        attempts = 0
#        while self._ser.inWaiting == 0 and attempts < 100:
#            attempt+= 1
#            time.sleep(0.1)

        while self._ser.inWaiting():
            self.read()

        print('Done.')


    def close(self):
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def write(self, command):
        command += '\n'
        self._ser.write(command.encode('utf-8'))

    def read(self):
        return self._ser.readline().decode('utf-8').strip()

    def query(self, command):
        self.write(command)
        return self.read()

    def home(self, wait_until_finished = True):
        self.flush()
        self.write('G28')
        if wait_until_finished:
            self.wait_until_finished()
        self._x = 0

    def flush(self):
        self._ser.flush()
    
    def override_extrude(self):
        self.flush()
        self.write('M302 P')
        self.wait_until_finished()

    def e_relative(self):
        self.flush()
        self.write('M83')
        self.wait_until_finished()

    def wait_until_finished(self):
        attempts = 0
        result = ''
        while attempts < MAX_ATTEMPTS and result != 'ok':
            result = self.read()
            attempts += 1
        if result == 'ok':
            return True
        else:
            raise RuntimeError('Failed Operation.')

    def set_x(self, x):
        self.flush()
        if x < 0 or x > 100:
            raise ValueError('X value out of bounds. Value of "x" must be between %0.02f and %0.02f'%(X_MIN, X_MAX))
        command = 'G0 X%0.02f'%x
        self.write(command)
        self.wait_until_finished()
        self._x = x

    def rotate(self, turns):
        self.flush()
        if turns < TURNS_MIN or turns > TURNS_MAX:
            raise ValueError('X value out of bounds. Value of "turns" must be between %0.02f and %0.02f'%(TURNS_MIN, TURNS_MAX))
        move_mm = turns * MM_PER_REV

        if move_mm > E_MAX_RELATIVE_MOVE:
            raise ValueError('Movement in mm is %0.02f. This exceeds the maximum value of %0.02f'%(move_mm, E_MAX_RELATIVE_MOVE))
        command = 'G0 E%0.02f'%(turns * MM_PER_REV)
        self.write(command)
        self.wait_until_finished()
        self._abs_turns += turns
        self._turns = turns


if __name__ == '__main__':
    w = Winder()
    w.home()
    w.e_relative()
    w.override_extrude()
    w.write('G0 Z10')
    w.read()
    w.write('G0 Y10')
    w.read()
    w.set_x(10)
    w.rotate(1)

