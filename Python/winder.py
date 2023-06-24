import serial
from serial.tools import list_ports
import time

VID = 1155 # Vendor ID, USB Device
PID = 22336 # Product ID, USB Device

TIMEOUT = 3.0
BAUDRATE = 115200

MAX_ATTEMPTS = 1000

X_MIN = 0
X_MAX = 200

TURNS_MIN = -1000
TURNS_MAX = 1000

STEPS_PER_MM = 93.00 # For Extruder
#STEPS_PER_MM = 800.00 # For Extruder
STEPS_PER_REV = 200.00
E_MICROSTEPS = 16.

E_MAX_RELATIVE_MOVE = 200.

FEED_RATE_MIN = 100.
FEED_RATE_MAX = 10800.

#WIND_RPM_MIN = 1. # need to calculate in mm/sec
#WIND_RPM_MAX = 25.

MM_PER_REV = E_MICROSTEPS * STEPS_PER_REV / STEPS_PER_MM

class Winder:
    def __init__(self, port = None, verbose = False):

        self.verbose = verbose

        if port is None:
            port = self.autodetect()
        self._port = port
        self._ser = None

        self.open()
        self._abs_turns = 0

    def autodetect(self):
        for p in list_ports.comports():
            if p.vid == VID and p.pid == PID:
                return p.device
        raise RuntimeError('Unable to Automatically detect serial port.\nPlease Confirm Device is Plugged in or Enter Port Manually')

    def open(self):
        print('Attempting to open serial...')
        if self._ser is not None:
            raise RuntimeError('Device connection already open')
        self._ser = serial.Serial(port = self._port, baudrate = BAUDRATE, timeout = TIMEOUT)

        print('Waiting for Initialization...')
        time.sleep(5)

        attempts = 0
#        while self._ser.inWaiting == 0 and attempts < 100:
#            attempt+= 1
#            time.sleep(0.1)

        while self._ser.inWaiting():
            out = self.read()
            if self.verbose:
                print(out)

        print('Done.')


    def close(self):
        if self._ser is not None:
            self._ser.close()
            self._ser = None

    def write(self, command):
        command += '\n'
        if self.verbose:
            print('Sending Command:', repr(command))
        self._ser.write(command.encode('utf-8'))

    def read(self):
        out = self._ser.readline().decode('utf-8').strip()
        if self.verbose:
            print('Reading:', repr(out))
        return out


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
        if self.verbose:
            print('Flushing Buffer...')
            if self._ser.inWaiting() > 0:
                print('Flushing %i Bytes in Waiting.'%self._ser.inWaiting())
        self._ser.reset_input_buffer()
        self._ser.reset_output_buffer()
        if self.verbose:
            print('Bytes in Waiting after Flush:', self._ser.inWaiting())
            print('Done Flushing.')
    
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
        if x < X_MIN or x > X_MAX:
            raise ValueError('X value out of bounds. Value of "x" must be between %0.02f and %0.02f'%(X_MIN, X_MAX))
        command = 'G0 X%0.02f'%x
        self.write(command)
        self.wait_until_finished()
        self._x = x

    def set_x_rotate(self, x, turns):
        self.flush()
        if x < X_MIN or x > X_MAX:
            raise ValueError('X value out of bounds. Value of "x" must be between %0.02f and %0.02f'%(X_MIN, X_MAX))
        x_command = ' X%0.02f'%x
        self._x = x

        if turns < TURNS_MIN or turns > TURNS_MAX:
            raise ValueError('X value out of bounds. Value of "turns" must be between %0.02f and %0.02f'%(TURNS_MIN, TURNS_MAX))
        move_mm = turns * MM_PER_REV

        if move_mm > E_MAX_RELATIVE_MOVE:
            raise ValueError('Movement in mm is %0.02f. This exceeds the maximum value of %0.02f'%(move_mm, E_MAX_RELATIVE_MOVE))
        e_command = ' E%0.02f'%(turns * MM_PER_REV)
        command = 'G0' + x_command + e_command
        self.write(command)
        self.wait_until_finished()
        self._abs_turns += turns
        self._turns = turns

    def finish_moves(self):
        if self.verbose:
            print('Waiting for moves to finish...')
        self.write('M400')
        self.wait_until_finished()
        if self.verbose:
            print('Moves Finished.')

    def set_rate(self, rate):
        ''' Set the Feed Rate in mm/min'''

        if rate < FEED_RATE_MIN or rate > FEED_RATE_MAX:
            raise ValueError('Feed Rate of %i is out of range. must be between %i and %i.'%(rate, FEED_RATE_MIN, FEED_RATE_MAX))

        self.write('G0 F%0.02f'%rate)
        self.wait_until_finished()

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

    def unconditional_stop(self, expire_time = None, message = ''):
        '''Issue Unconditional Stop Command - M0'''
        self.flush()
        command = 'M0'
        if expire_time is not None:
            if expire_time > 0:
                command += ' S%i'%expire_time

        command += message

        self.write(command)
        self.wait_until_finished()

    def set_current_position(self, x, e):
        '''Set the current position (does not move steppers)'''

        self.flush()
        command = 'G92 X%0.02f E%0.02f'%(x,e)

        self.write(command)
        self.wait_until_finished()

    def zero_current_position(self):
        '''Set the current position to zero'''

        self.set_current_position(0,0)

    def set_feedrate_percent(self, percent):
        '''Set percent max feedrate'''

        self.flush()
        command = 'M220 S%0.02f'%percent

        self.write(command)
        self.wait_until_finished()



if __name__ == '__main__':
    w = Winder(verbose = True)
#    w.zero_current_position()
#    w.set_x(10)
#    w.finish_moves()
#    w.zero_current_position()
#    w.write('M914 X60')
#    w.wait_until_finished()
#    w.set_feedrate_percent(10)
#    w.home()
#    w.finish_moves()
#    w.set_feedrate_percent(100)
#    w.set_x(20)
#    w.finish_moves()
#    w.e_relative()
#    w.override_extrude()
#    w.read()
#    w.read()
#    w.set_rate(10000)
#    w.set_x(10)
#    w.rotate(1)
#    w.finish_moves()
#    w.set_x(20)
#    w.rotate(1)
#    w.finish_moves()
#    w.set_x(10)
#    w.rotate(1)
#    w.finish_moves()
#
