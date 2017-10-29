#!/usr/bin/python3


class Memory:

    def __init__(self):
        self._memory = [0 for _ in range(4096)]

    def _check_address(self, address):
        if not 0 <= address <= 4095:
            raise Exception("address " + address +
                            " was outside of the memory")

    def store_value(self, address, value):
        self._check_address(address)
        self._memory[address] = value

    def get_value(self, address):
        self._check_address(address)
        return self._memory[address]


class Stack:

    def __init__(self):
        self._memory = [0 for _ in range(16)]
        self._stack_pointer = 0

    @property
    def length(self):
        return self._stack_pointer

    def push(self, value):
        if self._stack_pointer == 15:
            raise Exception("Stack is full")
        self._memory[self._stack_pointer] = value
        self._stack_pointer += 1

    def pop(self):
        if self._stack_pointer == 0:
            raise Exception("Stack is empty")
        self._stack_pointer -= 1
        return self._memory[self._stack_pointer]


class Register:

    def __init__(self, bits):
        self._bits = bits
        self._value = 0

    @property
    def value(self):
        return self._value % 2**self._bits

    @value.setter
    def value(self, argument):
        self._value = argument
