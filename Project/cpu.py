from numpy import ubyte
import sys

class CPU:
    def __init__(self):
        self.registers = [bytes(1)] * 16
        self.memory = [bytes(1)] * 256
        self.pointer = 0

        self._init_operations()

    def _init_operations(self):
        self.operations = [None] * 16

        self.operations[0] = self._load_m
        self.operations[1] = self._store
        self.operations[2] = self._jump
        self.operations[3] = self._add
        self.operations[4] = self._sub
        self.operations[5] = self._dec
        self.operations[6] = self._inc
        self.operations[7] = self._load_r
        self.operations[15] = self._stop

    def _load_m(self, i):
        self.registers[i[0] & 0x0F] = self.memory[i[1]]

    def _store(self, i):
        self.memory[i[1]] = self.registers[i[0] & 0x0F]

    def _jump(self, i):
        if self.registers[i[0] & 0x0F] == 0:
            self.pointer = int(i)
    
    def _add(self, i):
        self.registers[i[0] & 0x0F] = bytes([self.registers[i[1] >> 4][0] + self.registers[i[1] & 0x0F][0]])
    
    def _sub(self, i):
        self.registers[i[0] & 0x0F] = self.registers[i[1] >> 4] - self.registers[i[1] & 0x0F]
    
    def _dec(self, i):
        self.registers[i[0] & 0x0F] -= 1
    
    def _inc(self, i):
        self.registers[i[0] & 0x0F] += 1
        
    def _load_r(self, i):
        self.registers[i[0] & 0x0F] = bytes([i[1]])
    
    def _stop(self, i):
        print(self.registers)
        print(self.memory)
        sys.exit(0)
    
    def read(self, filename):
        with open(filename, "rb") as file:
            self.instructions = file.read()
            self.pointer = 0
        
    def next_instruction(self):
        i = self.instructions[self.pointer : self.pointer + 2]
        self.operations[i[0] >> 4](i)
        self.pointer += 2

if __name__ == "__main__":
    cpu = CPU()

    cpu.read("hello.txt")

    while True:
        cpu.next_instruction()
