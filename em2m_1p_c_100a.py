#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec 14 22:27:45 2022

@author: sudarsun
"""

import time
import minimalmodbus
from minimalmodbus import NoResponseError

class EnergyMeter:
    """ Energy Meter RS485 interface to access the Selec device """

    def __init__(self, device, identifier, address, baudrate=9600, timeout=1):
        """ Create an instance of the device accessed through RS485 MODBUS protocol"""
        self._handle = minimalmodbus.Instrument(device, slaveaddress=address,
                                                close_port_after_each_call=True,
                                                mode = minimalmodbus.MODE_RTU)
        self._handle.serial.baudrate = baudrate
        self._handle.serial.timeout = timeout
        self._id = identifier
        self._retries = 0

    @property
    def name(self):
        return self._id

    @name.setter
    def name(self, identifier):
        self._id = identifier

    @property
    def retries(self):
        return self._retries

    @retries.setter
    def retries(self, count):
        self._retries = count

    def __retry_mechanism(self, function, *args):
        """ Retry mechanism for executing the MODBUS reads """
        retry = 0
        while retry <= self._retries:
            try:
                time.sleep(0.05)
                arglen = len(args)
                if arglen == 0:
                    return function()
                elif arglen == 1:
                    return function(args[0])
                elif arglen == 2:
                    return function(args[0], args[1])
                elif arglen == 3:
                    return function(args[0], args[1], args[2])
                elif arglen == 4:
                    return function(args[0], args[1], args[2], args[3])
                else:
                    return function()
            except (NoResponseError, IOError) as e:
                retry += 1
                # if we have reached the upper cutoff, rethrow.
                if retry == self._retries:
                    raise e
                time.sleep(1)
                continue
        raise ValueError(f"elapsed maximum retries ({self._retries}) calling the function", function)

    @property
    def current(self):
        """ Read the active current through the device """
        return self.__retry_mechanism(self._handle.read_float, 23, 4), 'A'

    @property
    def voltage(self):
        """ Read the active current through the device """
        return self.__retry_mechanism(self._handle.read_float, 21, 4), 'V'

    @property
    def frequency(self):
        """ Read the frequency of the voltage signal through the device """
        return self.__retry_mechanism(self._handle.read_float, 27, 4), 'Hz'

    @property
    def powerfactor(self):
        """ Read the power factor through the device """
        return self.__retry_mechanism(self._handle.read_float, 25, 4), 'pf'

    @property
    def active_power(self):
        """ Read the active power through the device """
        return self.__retry_mechanism(self._handle.read_float, 15, 4), 'KW'

    @property
    def reactive_power(self):
        """ Read the reactive power through the device """
        return self.__retry_mechanism(self._handle.read_float, 17, 4), 'KVAr'

    @property
    def apparent_power(self):
        """ Read the apparent power through the device """
        return self.__retry_mechanism(self._handle.read_float, 19, 4), 'KVA'

    @property
    def active_energy(self):
        """ Read the active energy value """
        return self.__retry_mechanism(self._handle.read_float, 1, 4), 'KWh'

    @property
    def reactive_energy(self):
        """ Read the reactive energy value """
        return self.__retry_mechanism(self._handle.read_float, 7, 4), 'KVArh'

    @property
    def apparent_energy(self):
        """ Read the apparent energy value """
        return self.__retry_mechanism(self._handle.read_float, 13, 4), 'KVAh'

    @property
    def active_powerdemand(self):
        """ Read the active power demand value """
        return self.__retry_mechanism(self._handle.read_float, 29, 4), 'KW'

    @property
    def reactive_powerdemand(self):
        """ Read the reactive power demand value """
        return self.__retry_mechanism(self._handle.read_float, 31, 4), 'KVAr'

    @property
    def apparent_powerdemand(self):
        """ Read the apparent power demand value """
        return self.__retry_mechanism(self._handle.read_float, 33, 4), 'KVA'

    # Read the static configuration details
    # Range is 0x01 to 0x0F, 0x29 to 0x2C
    # Note: the address used is one less than the actual address.
    @property
    def serial_config(self):
        """ Read the Serial port configuration (baudrate 0x0B, parity 0x0C, stopbits 0x0D) setup in the device """
        # get the baud rate code
        baud_code = self.__retry_mechanism(self._handle.read_register, 10, 3)
        baud_rate = 9600 if baud_code == 0 else 19200 if baud_code == 1 else 0
        # get the parity bits
        parity_bits = self.__retry_mechanism(self._handle.read_register, 11, 3)
        # get the stop bits
        stop_bits = self.__retry_mechanism(self._handle.read_register, 12, 3)
        # return the triplet
        return baud_rate, parity_bits, stop_bits

    @property
    def address(self):
        """ Read the slave ID [0x2] """
        return self.__retry_mechanism(self._handle.read_register, 1, 3)
