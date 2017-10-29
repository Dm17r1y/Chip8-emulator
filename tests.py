#!/usr/bin/python3

import unittest
from interpreter import Interpreter
from display import Point
from commands import Command


class TestCommandsDecode(unittest.TestCase):

    def setUp(self):
        self.interpreter = Interpreter("games/UFO", None, [])
        for i in range(16):
            self.interpreter.V[i].value = i*10

    def test_code_0(self):
        self.check_correct_command(0x00e0, Command.Clear, [])
        self.check_correct_command(0x00ee, Command.Return, [])

    def test_code_1(self):
        self.check_correct_command(0x1100, Command.Jump, [0x100])

    def test_code_2(self):
        self.check_correct_command(0x2110, Command.Call, [0x110])

    def test_code_3(self):
        self.check_correct_command(0x3123, Command.PassIfEqual,
                                   [self.interpreter.V[1].value, 0x23])

    def test_code_4(self):
        self.check_correct_command(0x4123, Command.PassIfNotEqual,
                                   [self.interpreter.V[1].value, 0x23])

    def test_code_5(self):
        self.check_correct_command(0x5ab0, Command.PassIfEqual,
                                   [self.interpreter.V[0x0a].value,
                                    self.interpreter.V[0x0b].value])

    def test_code_6(self):
        self.check_correct_command(0x6055, Command.Move,
                                   [self.interpreter.V[0], 0x55])

    def test_code_7(self):
        self.check_correct_command(0x7155, Command.Move,
                                   [self.interpreter.V[1],
                                    0x55+self.interpreter.V[1].value])

    def test_code_8(self):
        self.check_correct_command(0x8120, Command.Move,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8121, Command.Or,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8122, Command.And,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8123, Command.Xor,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8124, Command.Add,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8125, Command.Sub,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8126, Command.ShiftRight,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x8127, Command.SubN,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])
        self.check_correct_command(0x812e, Command.ShiftLeft,
                                   [self.interpreter.V[1],
                                    self.interpreter.V[2].value])

    def test_code_9(self):
        self.check_correct_command(0x9120, Command.PassIfNotEqual,
                                   [self.interpreter.V[1].value,
                                    self.interpreter.V[2].value])

    def test_code_a(self):
        self.check_correct_command(0xa123, Command.Move,
                                   [self.interpreter.I, 0x123])

    def test_code_b(self):
        self.check_correct_command(0xb100, Command.Jump,
                                   [0x100 + self.interpreter.V[0].value])

    def test_code_c(self):
        self.check_correct_command(0xc123, Command.Random,
                                   [self.interpreter.V[1],
                                   0x23])

    def test_code_d(self):
        self.check_correct_command(0xd123, Command.Draw,
                                   [self.interpreter.V[1].value,
                                    self.interpreter.V[2].value, 3])

    def test_code_e(self):
        self.check_correct_command(0xe19e, Command.CheckPushed,
                                   [self.interpreter.V[1].value])
        self.check_correct_command(0xe1a1, Command.CheckNotPushed,
                                   [self.interpreter.V[1].value])

    def test_code_f(self):
        self.check_correct_command(0xf107, Command.Move,
                                   [self.interpreter.V[1],
                                    self.interpreter.delay_timer.ticks])
        self.check_correct_command(0xf10a, Command.WaitPushing,
                                   [self.interpreter.V[1]])
        self.check_correct_command(0xf115, Command.SetDelayTimer,
                                   [self.interpreter.V[1].value])
        self.check_correct_command(0xf118, Command.SetSoundTimer,
                                   [self.interpreter.V[1].value])
        self.check_correct_command(0xf11e, Command.Move,
                                   [self.interpreter.I,
                                    self.interpreter.V[1].value])
        self.check_correct_command(0xf129, Command.SetSymbolLocation,
                                   [self.interpreter.V[1].value])
        self.check_correct_command(0xf133, Command.StoreDecimalToMemory,
                                   [self.interpreter.V[1].value])
        self.check_correct_command(0xf155, Command.StoreRegisters, [1])
        self.check_correct_command(0xf165, Command.LoadRegisters, [1])

    def test_wrong_command(self):
        self.assertRaises(Exception, self.interpreter.decode, 0x0000)


    def check_correct_command(self, code, command, arguments):
        comm, *args = self.interpreter.decode(code)
        self.assertEqual(command, comm)
        self.check_correct_arguments(arguments, args)

    def check_correct_arguments(self, first_list, second_list):
        self.assertEqual(len(first_list), len(second_list))
        for first, second in zip(first_list, second_list):
            self.assertEqual(first, second)


class TestController:

    def __init__(self, return_value):
        self.return_value = return_value

    def get_key_code(self):
        return self.return_value

class TestExecuteCommands(unittest.TestCase):

    def setUp(self):
        self.controller = TestController(42)
        self.interpreter = Interpreter("games/UFO", self.controller, [])
        self.interpreter.V[0xf].value = 1

    def test_clear(self):
        self.interpreter.display.set_pixel(Point(0, 0), 1)
        self.assertEqual(1, self.interpreter.display.get_pixel(Point(0, 0)))
        Command.Clear(self.interpreter).execute_command()
        self.assertEqual(0, self.interpreter.display.get_pixel(Point(0, 0)))

    def test_call(self):
        Command.Call(self.interpreter).execute_command(0x111)
        self.assertEqual(0x111, self.interpreter.instruction_pointer)
        self.assertEqual(1, self.interpreter.stack.length)
        self.assertEqual(0x200, self.interpreter.stack.pop())

    def test_return(self):
        Command.Call(self.interpreter).execute_command(0x111)
        Command.Return(self.interpreter).execute_command()
        self.assertEqual(0x200, self.interpreter.instruction_pointer)
        self.assertEqual(0, self.interpreter.stack.length)

    def test_jump(self):
        Command.Jump(self.interpreter).execute_command(0x111)
        self.assertEqual(0x111, self.interpreter.instruction_pointer)

    def test_pass_if_equal(self):
        Command.PassIfEqual(self.interpreter).execute_command(10, 0)
        self.assertEqual(0x200, self.interpreter.instruction_pointer)
        Command.PassIfEqual(self.interpreter).execute_command(0, 0)
        self.assertEqual(0x202, self.interpreter.instruction_pointer)

    def test_pass_if_not_equal(self):
        Command.PassIfNotEqual(self.interpreter).execute_command(0, 0)
        self.assertEqual(0x200, self.interpreter.instruction_pointer)
        Command.PassIfNotEqual(self.interpreter).execute_command(10, 0)
        self.assertEqual(0x202, self.interpreter.instruction_pointer)

    def test_move(self):
        Command.Move(self.interpreter).execute_command(
                                       self.interpreter.V[1], 10)
        self.assertEqual(10, self.interpreter.V[1].value)

    def test_add(self):
        self.interpreter.V[1].value = 10
        Command.Add(self.interpreter)\
            .execute_command(self.interpreter.V[1], 20)
        self.assertEqual(30, self.interpreter.V[1].value)
        self.assertEqual(0, self.interpreter.V[0xf].value)
        self.interpreter.V[0].value = 255
        Command.Add(self.interpreter)\
            .execute_command(self.interpreter.V[0], 1)
        self.assertEqual(0, self.interpreter.V[0].value)
        self.assertEqual(1, self.interpreter.V[0xf].value)

    def test_or(self):
        self.interpreter.V[0].value = 0xf
        Command.Or(self.interpreter)\
            .execute_command(self.interpreter.V[0], 0xf0)
        self.assertEqual(0xff, self.interpreter.V[0].value)

    def test_and(self):
        self.interpreter.V[0].value = 0xff
        Command.And(self.interpreter)\
            .execute_command(self.interpreter.V[0], 0x0f)
        self.assertEqual(0x0f, self.interpreter.V[0].value)

    def test_xor(self):
        self.interpreter.V[0].value = 100
        Command.Xor(self.interpreter)\
            .execute_command(self.interpreter.V[0], 200)
        self.assertEqual(100^200, self.interpreter.V[0].value)

    def test_sub(self):
        self.interpreter.V[0].value = 100
        Command.Sub(self.interpreter)\
            .execute_command(self.interpreter.V[0], 30)
        self.assertEqual(70, self.interpreter.V[0].value)
        self.assertEqual(1, self.interpreter.V[0xf].value)
        self.interpreter.V[1].value = 10
        Command.Sub(self.interpreter)\
            .execute_command(self.interpreter.V[1], 11)
        self.assertEqual(0xff, self.interpreter.V[1].value)
        self.assertEqual(0, self.interpreter.V[0xf].value)

    def test_subn(self):
        self.interpreter.V[1].value = 100
        Command.SubN(self.interpreter)\
            .execute_command(self.interpreter.V[1], 130)
        self.assertEqual(30, self.interpreter.V[1].value)
        self.assertEqual(1, self.interpreter.V[0xf].value)
        self.interpreter.V[1].value = 10
        Command.SubN(self.interpreter)\
            .execute_command(self.interpreter.V[1], 9)
        self.assertEqual(0xff, self.interpreter.V[1].value)
        self.assertEqual(0, self.interpreter.V[0xf].value)

    def test_shift_right(self):
        self.interpreter.V[0].value = 2
        Command.ShiftRight(self.interpreter)\
            .execute_command(self.interpreter.V[0], None)
        self.assertEqual(1, self.interpreter.V[0].value)
        self.assertEqual(0, self.interpreter.V[0xf].value)

        self.interpreter.V[1].value = 15
        Command.ShiftRight(self.interpreter)\
            .execute_command(self.interpreter.V[1], None)
        self.assertEqual(7, self.interpreter.V[1].value)
        self.assertEqual(1, self.interpreter.V[0xf].value)

    def test_shift_left(self):
        self.interpreter.V[0].value = 4
        Command.ShiftLeft(self.interpreter)\
            .execute_command(self.interpreter.V[0], None)
        self.assertEqual(8, self.interpreter.V[0].value)
        self.assertEqual(0, self.interpreter.V[0xf].value)

        self.interpreter.V[1].value = 128
        Command.ShiftLeft(self.interpreter)\
            .execute_command(self.interpreter.V[1], None)
        self.assertEqual(0, self.interpreter.V[1].value)
        self.assertEqual(1, self.interpreter.V[0xf].value)

    def test_random(self):
        Command.Random(self.interpreter)\
            .execute_command(self.interpreter.V[0], 10)
        self.assertLessEqual(self.interpreter.V[0].value, 10)

    def test_draw(self):
        self.assertEqual(False, self.interpreter.need_redraw)
        self.interpreter.memory.store_value(0, 255)
        self.interpreter.memory.store_value(1, 1)
        Command.Draw(self.interpreter).execute_command(0, 0, 1)
        self.assertEqual(0, self.interpreter.V[0x0f].value)
        for i in range(8):
            self.assertEqual(1,
                             self.interpreter.display.get_pixel(Point(i, 0)))
        self.interpreter.I.value = 1
        Command.Draw(self.interpreter).execute_command(0, 0, 1)
        self.assertEqual(1, self.interpreter.V[0x0f].value)
        self.assertEqual(0, self.interpreter.display.get_pixel(Point(7, 0)))
        for i in range(0, 7):
            self.assertEqual(1,
                             self.interpreter.display.get_pixel(Point(i, 0)))
        self.assertEqual(True, self.interpreter.need_redraw)

    def test_check_pushed(self):
        Command.CheckPushed(self.interpreter).execute_command(42)
        self.assertEqual(0x202, self.interpreter.instruction_pointer)
        Command.CheckPushed(self.interpreter).execute_command(43)
        self.assertEqual(0x202, self.interpreter.instruction_pointer)

    def test_check_not_pushed(self):
        Command.CheckNotPushed(self.interpreter).execute_command(42)
        self.assertEqual(0x200, self.interpreter.instruction_pointer)
        Command.CheckNotPushed(self.interpreter).execute_command(43)
        self.assertEqual(0x202, self.interpreter.instruction_pointer)

    def test_set_delay_timer(self):
        Command.SetDelayTimer(self.interpreter).execute_command(10)
        self.assertEqual(10, self.interpreter.delay_timer.ticks)

    def test_wait_pushing(self):
        self.interpreter.instruction_pointer = 4
        self.controller.return_value = None
        Command.WaitPushing(self.interpreter)\
            .execute_command(self.interpreter.V[1])
        self.assertEqual(2, self.interpreter.instruction_pointer)
        self.controller.return_value = 15
        Command.WaitPushing(self.interpreter)\
            .execute_command(self.interpreter.V[1])
        self.assertEqual(2, self.interpreter.instruction_pointer)
        self.assertEqual(15, self.interpreter.V[1].value)

    def test_set_sound_timer(self):
        Command.SetSoundTimer(self.interpreter).execute_command(10)
        self.assertEqual(10, self.interpreter.sound_timer.ticks)

    def test_set_symbol_location(self):
        for i in range(16):
            Command.SetSymbolLocation(self.interpreter).execute_command(i)
            self.assertEqual(i*5, self.interpreter.I.value)

    def test_store_decimal_to_memory(self):
        Command.StoreDecimalToMemory(self.interpreter).execute_command(254)
        self.assertEqual(2, self.interpreter.memory.get_value(0))
        self.assertEqual(5, self.interpreter.memory.get_value(1))
        self.assertEqual(4, self.interpreter.memory.get_value(2))

    def test_store_registers(self):
        self.interpreter.V[0].value = 10
        self.interpreter.V[1].value = 20
        self.interpreter.V[2].value = 30
        Command.StoreRegisters(self.interpreter).execute_command(2)
        self.assertEqual(10, self.interpreter.memory.get_value(0))
        self.assertEqual(20, self.interpreter.memory.get_value(1))
        self.assertEqual(30, self.interpreter.memory.get_value(2))

    def test_load_registers(self):
        self.interpreter.memory.store_value(0, 10)
        self.interpreter.memory.store_value(1, 20)
        self.interpreter.memory.store_value(2, 30)
        Command.LoadRegisters(self.interpreter).execute_command(2)
        self.assertEqual(10, self.interpreter.V[0].value)
        self.assertEqual(20, self.interpreter.V[1].value)
        self.assertEqual(30, self.interpreter.V[2].value)


class InterpreterTests(unittest.TestCase):

    correct_sprites = [
        0xf0, 0x90, 0x90, 0x90, 0xf0,       # 0
        0x20, 0x60, 0x20, 0x20, 0x70,       # 1
        0xf0, 0x10, 0xf0, 0x80, 0xf0,       # 2
        0xf0, 0x10, 0xf0, 0x10, 0xf0,       # 3
        0x90, 0x90, 0xf0, 0x10, 0x10,       # 4
        0xf0, 0x80, 0xf0, 0x10, 0xf0,       # 5
        0xf0, 0x80, 0xf0, 0x90, 0xf0,       # 6
        0xf0, 0x10, 0x20, 0x40, 0x40,       # 7
        0xf0, 0x90, 0xf0, 0x90, 0xf0,       # 8
        0xf0, 0x90, 0xf0, 0x10, 0xf0,       # 9
        0xf0, 0x90, 0xf0, 0x90, 0x90,       # A
        0xe0, 0x90, 0xe0, 0x90, 0xe0,       # B
        0xf0, 0x80, 0x80, 0x80, 0xf0,       # C
        0xe0, 0x90, 0x90, 0x90, 0xe0,       # D
        0xf0, 0x80, 0xf0, 0x80, 0xf0,       # E
        0xf0, 0x80, 0xf0, 0x80, 0x80        # F
    ]

    def setUp(self):
        self.interpreter = Interpreter("games/UFO", None, self.correct_sprites)

    def test_initialize_sprites(self):


        for i, j in zip(self.correct_sprites, self.interpreter.memory._memory):
            self.assertEqual(i, j)

    def test_execute_command(self):
        self.interpreter.execute_next_command()
        self.assertEqual(0x2cd, self.interpreter.I.value)
        self.assertEqual(0x202, self.interpreter.instruction_pointer)

    def test_read_instruction(self):
        code = self.interpreter.read_instruction()
        self.assertEqual(0xa2cd, code)

    def test_serialization(self):
        self.interpreter.sound_timer.ticks = 10
        self.interpreter.delay_timer.ticks = 20
        for i in range(16):
            self.interpreter.V[i].value = i
        self.interpreter.I.value = 255
        self.interpreter.instruction_pointer = 30
        self.interpreter.stack.push(100)
        self.interpreter.display.set_pixel(Point(0, 1), 1)

        serialize = self.interpreter.serialize_state()
        new_interpreter = Interpreter("games/UFO", None, [])
        new_interpreter.load_state(serialize)

        self.assertEqual(10, new_interpreter.sound_timer.ticks)
        self.assertEqual(20, new_interpreter.delay_timer.ticks)
        for i in range(16):
            self.assertEqual(i, new_interpreter.V[i].value)

        self.assertEqual(255, new_interpreter.I.value)
        self.assertEqual(30, new_interpreter.instruction_pointer)
        self.assertEqual(self.interpreter.stack._memory,
                         new_interpreter.stack._memory)
        self.assertEqual(1, new_interpreter.stack._stack_pointer)
        self.assertEqual(self.interpreter.memory._memory,
                         new_interpreter.memory._memory)
        self.assertEqual(self.interpreter.display._pixels,
                         new_interpreter.display._pixels)

if __name__ == "__main__":
    unittest.main()
