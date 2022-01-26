from numpy import ubyte
import sys

class CPU:
    def __init__(self):
        self.registers = [ubyte()] * 16
        self.memory = [ubyte()] * 256
        self.pointer = ubyte(0)
        self.has_jumped = False

        self._init_operations()

    def _init_operations(self):
        self.operations = [None] * 16

        self.operations[0] = self._loadm
        self.operations[1] = self._store
        self.operations[2] = self._jump
        self.operations[3] = self._add
        self.operations[4] = self._sub
        self.operations[5] = self._dec
        self.operations[6] = self._inc
        self.operations[7] = self._loadc
        self.operations[8] = self._copy
        self.operations[15] = self._stop

    def _loadm(self, i):
        self.registers[i[0] & 0x0F] = self.memory[i[1]]

    def _store(self, i):
        self.memory[i[1]] = self.registers[i[0] & 0x0F]

    def _jump(self, i):
        if self.registers[i[0] & 0x0F] == ubyte(0):
            self.pointer = i[1]
            self.has_jumped = True
    
    def _add(self, i):
        self.registers[i[0] & 0x0F] = self.registers[i[1] >> 4] + self.registers[i[1] & 0x0F]
    
    def _sub(self, i):
        self.registers[i[0] & 0x0F] = self.registers[i[1] >> 4] - self.registers[i[1] & 0x0F]
    
    def _dec(self, i):
        self.registers[i[0] & 0x0F] -= ubyte(1)
    
    def _inc(self, i):
        self.registers[i[0] & 0x0F] += ubyte(1)
        
    def _loadc(self, i):
        self.registers[i[0] & 0x0F] = i[1]

    def _copy(self, i):
        self.registers[i[0] & 0x0F] = self.registers[i[1] >> 4]

    def _stop(self, i):
        print(self.registers)
        print(self.memory)
        sys.exit(0)
    
    def read(self, filename):
        with open(filename, "rb") as file:
            self.instructions = file.read()
            self.pointer = ubyte(0)
        
    def next_instruction(self):
        self.has_jumped = False

        i = self.instructions[self.pointer : self.pointer + 2]
        self.operations[i[0] >> 4]([ubyte(i[0]), ubyte(i[1])])
        
        if not self.has_jumped:
            self.pointer += ubyte(2)

if __name__ == "__main__":
    cpu = CPU()
    cpu.read("hello.txt")

    while True:
        cpu.next_instruction()
