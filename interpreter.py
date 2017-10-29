#!/usr/bin/python3

import memory
from commands import Command
from display import Display, Point
import struct
import pickle
import timer


class Interpreter:

    def __init__(self, game_file, controller, sprites,
                 play_sound_func=timer.empty_func):
        self.controller = controller
        self.V = [memory.Register(8) for _ in range(16)]
        self.I = memory.Register(16)
        self.instruction_pointer = 0x200
        self.memory = memory.Memory()
        self.stack = memory.Stack()
        self.display = Display()
        self.delay_timer = timer.Timer()
        self.sound_timer = timer.Timer(end_timer_func=play_sound_func)
        with open(game_file, 'rb') as f:
            self.load_commands(f.read())
        self.initialize_sprites(sprites)
        self._need_redraw = False


    def initialize_sprites(self, sprites):
        for i, sprite_line in enumerate(sprites):
            self.memory.store_value(i, sprite_line)

    def read_instruction(self):
        first_value = self.memory.get_value(self.instruction_pointer)
        second_value = self.memory.get_value(self.instruction_pointer + 1)
        return first_value << 8 | second_value

    def load_commands(self, data):
        for i, char in enumerate(data):
            self.memory.store_value(0x200 + i, char)

    def get_key_code(self):
        return self.controller.get_key_code()

    def decode(self, code):

        command_number = (code & 0xf000) >> 12
        first_register = self.V[(code & 0x0f00) >> 8]
        second_register = self.V[(code & 0x00f0) >> 4]

        if command_number == 0x0:
            if code == 0x00e0:
                return Command.Clear,
            elif code == 0x00ee:
                return Command.Return,

        elif command_number == 0x1:
            return Command.Jump, code & 0x0fff

        elif command_number == 0x2:
            return Command.Call, code & 0x0fff

        elif command_number == 0x3:
            return Command.PassIfEqual, first_register.value, code & 0x00ff

        elif command_number == 0x4:
            return Command.PassIfNotEqual, first_register.value, code & 0x00ff

        elif command_number == 0x5:
            if code & 0x000f == 0:
                return Command.PassIfEqual, first_register.value,\
                       second_register.value

        elif command_number == 0x6:
            return Command.Move, first_register, code & 0x00ff

        elif command_number == 0x7:
            return Command.Move, first_register,\
                   first_register.value + code & 0x00ff

        elif command_number == 0x8:
            commands = {0: Command.Move,
                        1: Command.Or,
                        2: Command.And,
                        3: Command.Xor,
                        4: Command.Add,
                        5: Command.Sub,
                        6: Command.ShiftRight,
                        7: Command.SubN,
                        0xe: Command.ShiftLeft}
            if code & 0x000f in commands:
                return commands[code & 0xf], first_register,\
                       second_register.value

        elif command_number == 0x9:
            if code & 0x000f == 0:
                return Command.PassIfNotEqual, first_register.value,\
                       second_register.value

        elif command_number == 0xa:
            return Command.Move, self.I, code & 0x0fff

        elif command_number == 0xb:
            return Command.Jump, (code & 0x0fff) + self.V[0].value

        elif command_number == 0xc:
            return Command.Random, first_register, code & 0x00ff

        elif command_number == 0xd:
            return Command.Draw, first_register.value, second_register.value,\
                   code & 0x000f

        elif command_number == 0xe:
            if code & 0x00ff == 0x9e:
                return Command.CheckPushed, first_register.value

            elif code & 0x00ff == 0xa1:
                return Command.CheckNotPushed, first_register.value

        elif command_number == 0xf:
            first_register_number = (code & 0x0f00) >> 8
            commands = {
                0x07: (Command.Move, first_register, self.delay_timer.ticks),
                0x0a: (Command.WaitPushing, first_register),
                0x15: (Command.SetDelayTimer, first_register.value),
                0x18: (Command.SetSoundTimer, first_register.value),
                0x1e: (Command.Move, self.I, self.I.value +
                       first_register.value),
                0x29: (Command.SetSymbolLocation, first_register.value),
                0x33: (Command.StoreDecimalToMemory, first_register.value),
                0x55: (Command.StoreRegisters, first_register_number),
                0x65: (Command.LoadRegisters, first_register_number)
                }
            if code & 0x00ff in commands:
                return commands[code & 0x00ff]

        raise Exception("Wrong command code: " + hex(code))

    @property
    def need_redraw(self):
        return self._need_redraw

    @need_redraw.setter
    def need_redraw(self, value):
        self._need_redraw = value

    def execute_next_command(self):
        code = self.read_instruction()
        command_type, *args = self.decode(code)
        command = command_type(self)
        self.instruction_pointer += 2
        command.execute_command(*args)

    def serialize_state(self):
        return pickle.dumps(self)

    def load_state(self, state):
        interpreter = pickle.loads(state)
        for i in range(16):
            self.V[i].value = interpreter.V[i].value
        self.I.value = interpreter.I.value
        self.instruction_pointer = interpreter.instruction_pointer
        self.memory = interpreter.memory
        self.stack = interpreter.stack
        self.display = interpreter.display
        self.delay_timer.ticks = interpreter.delay_timer.ticks
        self.sound_timer.ticks = interpreter.sound_timer.ticks
