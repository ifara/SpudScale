#!/usr/bin/python3
import threading
import serial


class Scale(threading.Thread):
    """Scale connects to a designated COM port and continuously listens for data.

    Each instance of Scale launches a thread which reads from a COM port it
    processes that data and saves select information to an entry in a dict.

    Args:
        comPort: string; name of a COM port.
        container: dict; shared memory for use by all Scale threads.
    """

    def __init__(self, comPort, container):
        threading.Thread.__init__(self, daemon=True)
        self._stop = threading.Event()
        self.container = container
        self.port = comPort
        self.ser = serial.Serial(
            port=comPort,
            baudrate=2400,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=None)
        self.ser.close()

    def run(self):
        """Listens for scale messages and updates shared memory."""
        # length of scale output (used to ensure
        # only complete messages are processed)
        msgLength = 21
        while True:
            rawLine = self.ser.readline()
            if (len(rawLine) == msgLength):
                line = rawLine.decode('ascii')
                print(line)
                ID = line[0]
                sign = line[6]
                if (sign == '-'):
                    value = '0.00'
                else:
                    value = line[8:13].replace(' ', '')
                self.container[ID] = value
            if self.stopped():
                self.ser.close()
                break

# is a stop function necessary if thread runs as daemon?
# maybe necessary to close the serial port?
    def stop(self):
        self._stop.set()

    def stopped(self):
        return self._stop.isSet()
