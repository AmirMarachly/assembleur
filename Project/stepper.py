import os
import curses

from cpu import CPU
from assembler import Assembler

class Stepper:
    def __init__(self, filename):
        self.assembler = Assembler()
        self.cpu = CPU()
        self.pointer = 0
        self.offset = 0
        self.autoscroll = True

        pre, ext = os.path.splitext(filename)
        output = f"{pre}.o"

        self.assembler.assemble(filename, output)
        self.cpu.load(output)

    def _hex(self, x):
        return bytes([x]).hex().upper()

    def _display_registers(self, stdscr):
        labels = ""
        content = ""

        for i, reg in enumerate(self.cpu.registers):
            labels += f" {chr(i + ord('A'))}  |"
            content += f" {self._hex(reg)} |"

        labels = labels[:-1]
        content = content[:-1]

        stdscr.addstr(1, 1, labels)
        stdscr.addstr(2, 1, content)

    def _current_label(self, a):
        width = 4

        for key, value in self.assembler.labels.items():
            if value == a:
                s = key.replace(":", "")
                s = s[:width - 1]
                s += ":"

                return s.ljust(width, " ")

        return " " * width

    def _current_instruction(self, a):
        try:
            return self.assembler.instructions[a // 2][0]

        except IndexError:
            return ""

    def _display_instructions(self, stdscr):
        y, x = stdscr.getmaxyx()
        START_X = 2
        START_Y = (y - 6) // 2

        for i in range(-START_Y, START_Y + 1):
            if self.autoscroll:
                a = self.pointer + 2 * i

            else:
                a = self.offset + 2 * i
            
            try:
                label = self._current_label(a)
                prefix = "-->" if a == self.pointer else "   "
                mem = f"{self._hex(self.cpu.memory[a])} {self._hex(self.cpu.memory[a + 1])}"
                instr = self._current_instruction(a)
                    
                s = f"{label} {prefix} {self._hex(a)} | {mem}   {instr}"
                stdscr.addstr(START_Y + i + 4, START_X, s)

            except (IndexError, ValueError):
                pass

    def _display_memory(self, stdscr):
        y, x = stdscr.getmaxyx()
        START_X = x - 47
        START_Y = (y - 22) // 2

        s = ""

        for i in range(16):
            s += f"{self._hex(i)} "

        stdscr.addstr(START_Y + 2, START_X, s)

        for i in range(16):
            s = f"{self._hex(i * 16)}  "

            for j in range(16):
                s += f"{self._hex(self.cpu.memory[i * 16 + j])} "

            stdscr.addstr(START_Y + i + 4, START_X - 4, s)

    def _display(self, stdscr):
        y, x = stdscr.getmaxyx()

        stdscr.clear()
        self._display_registers(stdscr)
        self._display_instructions(stdscr)
        self._display_memory(stdscr)
        stdscr.addstr(y - 2, x - 36, "SPACE/ENTER: next instruction")
        stdscr.addstr(y - 1, x - 36, "A: toggle autoscroll ARROWS: scroll")
        stdscr.refresh()

    def _next(self):
        self.cpu.next_instruction()
        self.pointer = self.cpu.pointer

    def loop(self, stdscr):
        stdscr.keypad(1)
        key = ""

        while key != ord("e"):
            if key == ord("\n") or key == ord(" "):
                self._next()

            if key == curses.KEY_UP:
                self.offset -= 2

            if key == curses.KEY_DOWN:
                self.offset += 2

            if key == curses.KEY_RESIZE:
                curses.resize_term(*stdscr.getmaxyx())

            if key == ord("a") :
                self.autoscroll = not self.autoscroll
                self.offset = self.pointer
            
            self._display(stdscr)
            key = stdscr.getch()

if __name__ == "__main__":
    s = Stepper("test.txt")
    curses.wrapper(s.loop)