#!/usr/bin/python3

import random

from display import Point


class Command:

    class BaseCommand:
        def __init__(self, interpreter):
            self.interpreter = interpreter

    class Clear(BaseCommand):

        def execute_command(self):
            self.interpreter.display.clear()

    class Call(BaseCommand):

        def execute_command(self, new_address):
            self.interpreter.stack.push(self.interpreter.instruction_pointer)
            self.interpreter.instruction_pointer = new_address

    class Return(BaseCommand):

        def execute_command(self):
            address = self.interpreter.stack.pop()
            self.interpreter.instruction_pointer = address

    class Jump(BaseCommand):

        def execute_command(self, address):
            self.interpreter.instruction_pointer = address

    class PassIfEqual(BaseCommand):

        def execute_command(self, first_number, second_number):
            if first_number == second_number:
                self.interpreter.instruction_pointer += 2

    class PassIfNotEqual(BaseCommand):

        def execute_command(self, first_number, second_number):
            if first_number != second_number:
                self.interpreter.instruction_pointer += 2

    class Move(BaseCommand):

        def execute_command(self, register, value):
            register.value = value

    class Add(BaseCommand):

        def execute_command(self, register, value):
            self.interpreter.V[0xf].value = int(register.value + value > 0xff)
            register.value += value

    class Or(BaseCommand):

        def execute_command(self, register, value):
            register.value = register.value | value

    class And(BaseCommand):

        def execute_command(self, register, value):
            register.value = register.value & value

    class Xor(BaseCommand):

        def execute_command(self, register, value):
            register.value = register.value ^ value

    class Sub(BaseCommand):

        def execute_command(self, register, value):
            self.interpreter.V[0xf].value = int(register.value > value)
            register.value = register.value - value

    class SubN(BaseCommand):

        def execute_command(self, register, value):
            self.interpreter.V[0xf].value = int(value > register.value)
            register.value = value - register.value

    class ShiftRight(BaseCommand):

        def execute_command(self, register, value):
            self.interpreter.V[0xf].value = register.value & 1
            register.value = register.value >> 1

    class ShiftLeft(BaseCommand):

        def execute_command(self, register, value):
            self.interpreter.V[0xf].value = int(register.value & 0x80 != 0)
            register.value = register.value << 1

    class Random(BaseCommand):

        def execute_command(self, register, value):
            rand = random.randint(0, 255)
            register.value = rand & value

    class Draw(BaseCommand):

        def _get_bits(self, number):
            bits = list(map(int, bin(number)[2:]))
            bits = [0]*(8 - len(bits)) + bits

            return tuple(bits)

        def execute_command(self, x, y, lines):
            self.interpreter.need_redraw = True
            self.interpreter.V[0xf].value = 0
            for line in range(lines):
                memory_data = self.interpreter.memory\
                        .get_value(self.interpreter.I.value + line)
                bits = self._get_bits(memory_data)
                for bit_number, bit in enumerate(bits):
                    pixel_pos = Point(x + bit_number, y + line)
                    current_bit = self.interpreter.display.get_pixel(pixel_pos)
                    if bit == 1 and current_bit == 1:
                        self.interpreter.V[0xf].value = 1
                    self.interpreter.display.set_pixel(pixel_pos,
                                                       bit ^ current_bit)

    class CheckPushed(BaseCommand):

        def execute_command(self, value):
            key_code = self.interpreter.get_key_code()
            if key_code == value:
                self.interpreter.instruction_pointer += 2

    class CheckNotPushed(BaseCommand):

        def execute_command(self, value):
            key_code = self.interpreter.get_key_code()
            if key_code != value:
                self.interpreter.instruction_pointer += 2

    class SetDelayTimer(BaseCommand):

        def execute_command(self, value):
            self.interpreter.delay_timer.ticks = value

    class WaitPushing(BaseCommand):

        def execute_command(self, register):
            key_code = self.interpreter.get_key_code()
            if key_code is None:
                self.interpreter.instruction_pointer -= 2
            else:
                register.value = key_code

    class SetSoundTimer(BaseCommand):

        def execute_command(self, value):
            self.interpreter.sound_timer.ticks = value

    class SetSymbolLocation(BaseCommand):

        def execute_command(self, character_code):
            self.interpreter.I.value = character_code * 5

    class StoreDecimalToMemory(BaseCommand):

        def _get_decimal_representation(self, value):
            decimal = list(map(int, str(value)))
            return tuple([0] * (3 - len(decimal)) + decimal)

        def execute_command(self, value):
            decimal = self._get_decimal_representation(value)
            for i, number in enumerate(decimal):
                self.interpreter.memory\
                    .store_value(self.interpreter.I.value + i, number)

    class StoreRegisters(BaseCommand):

        def execute_command(self, register_number):
            for i in range(register_number + 1):
                value = self.interpreter.V[i].value
                self.interpreter.memory\
                    .store_value(self.interpreter.I.value + i, value)

    class LoadRegisters(BaseCommand):

        def execute_command(self, register_number):
            for i in range(register_number + 1):
                value = self.interpreter.memory\
                    .get_value(self.interpreter.I.value + i)
                self.interpreter.V[i].value = value
