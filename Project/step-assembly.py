import os
import curses
import sys

from cpu import CPU
from assembler import Assembler

class StepAssembly:
    """
    The StepAssembly class allows the read an assembly file and call the
    instructions step by step
    """
    def __init__(self, filename, start=0):
        """
        Loads the file, assembles it, and loads the assembled code into the CPU
        
        :param filename: The name of the file to assemble
        :param start: The address to start the program at, defaults to 0 (optional)
        """
        self.assembler = Assembler(start)
        self.cpu = CPU()
        self.offset = 0
        self.start = start
        self.autoscroll = True

        pre, ext = os.path.splitext(filename)
        output = f"{pre}.o"

        self.assembler.assemble(filename, output)
        self.cpu.load(output, start)
        self.pointer = self.cpu.pointer

    def _hex(self, x):
        """
        Convert a number to a hexadecimal string
        
        :param x: The number to be converted to hexadecimal
        :return: The hexadecimal representation of the bytes
        """
        return bytes([x]).hex().upper()

    def _display_registers(self, stdscr):
        """
        Display the registers of the CPU
        
        :param stdscr: the window object
        """
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
        """
        Return the label name for the current address
        
        :param a: The address of the current instruction
        :return: The current label
        """
        width = 4

        for key, value in self.assembler.labels.items():
            if value == a:
                s = key.replace(":", "")
                s = s[:width - 1]
                s += ":"

                return s.ljust(width, " ")

        return " " * width

    def _current_instruction(self, a):
        """
        Return the current instruction
        
        :param a: The address of the current instruction
        :return: The current instruction being executed.
        """
        if a - self.start < 0:
            return ""

        try:
            return self.assembler.instructions[(a - self.start) // 2][0]

        except IndexError:
            return ""

    def _display_instructions(self, stdscr):
        """
        Display the current instruction and memory address
        
        :param stdscr: the window object
        """
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
        """
        Display the memory of the CPU
        
        :param stdscr: the window object
        """
        y, x = stdscr.getmaxyx()
        START_X = x - 47
        START_Y = (y - 22) // 2

        s = ""

        for i in range(16):
            s += f"X{self._hex(i)[1]} "

        stdscr.addstr(START_Y + 2, START_X, s)

        for i in range(16):
            s = f"{self._hex(i * 16)[0]}X"
            stdscr.addstr(START_Y + i + 4, START_X - 4, s)

            for j in range(16):
                m = i * 16 + j
                s = f"{self._hex(self.cpu.memory[m])}"

                if m == self.cpu.current_memory:
                    stdscr.addstr(START_Y + i + 4, START_X + j * 3, s, curses.A_STANDOUT)

                else:
                    stdscr.addstr(START_Y + i + 4, START_X + j * 3, s)

    def _display(self, stdscr):
        """
        Display the registers, instructions, and memory
        
        :param stdscr: the window object
        """
        y, x = stdscr.getmaxyx()

        stdscr.erase()
        self._display_registers(stdscr)
        self._display_instructions(stdscr)
        self._display_memory(stdscr)
        stdscr.addstr(y - 2, x - 38, "SPACE/ENTER: next instruction, Q: quit")
        stdscr.addstr(y - 1, x - 38, "A: toggle autoscroll, ARROWS: scroll")
        stdscr.refresh()

    def _next(self):
        """
        Call the next instruction on the CPU and update the pointer
        """
        self.cpu.next_instruction()
        self.pointer = self.cpu.pointer

    def loop(self, stdscr):
        """
        The main loop of the program, wait for a key and display the CPU
        
        :param stdscr: the window object
        """
        stdscr.keypad(1)
        key = ""

        while key != ord("q"):
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
    if len(sys.argv) < 2:
        print("Need at least one argument, the file to run")
        sys.exit(1)

    if sys.argv[1] in ("--help", "-h"):
        print("Run the given assembly file step by step")
        print("\tFirst argument: the file")
        print("\tSecond arguement (optional): the starting pointer")
        sys.exit(0)

    try:
        try:
            p = int(sys.argv[2], 16)

            if p % 2 != 0:
                print("Starting pointer must be pair")
                sys.exit(1)

            s = StepAssembly(sys.argv[1], p)

        except ValueError:
                print("Starting pointer must be a number")
                sys.exit(1)
    
    except IndexError:
        s = StepAssembly(sys.argv[1])

    try:
        curses.wrapper(s.loop)

    except KeyboardInterrupt:
        sys.exit()