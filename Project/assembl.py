import sys
import os
import re

class Assembl:
    def __init__(self, filename):
        self._init_operations()
        self.instructions = []

        with open(filename) as file:
            self._read_instr(file)

    def _init_operations(self):
        self.operations = []

        reg = r"([A-R])"
        byte = r"([0-9A-F]{2})"
        label = r"([A-Z]+:)"

        self.operations.append((f"LOADM {reg} {byte}", self._loadm))
        self.operations.append((f"STORE {reg} {byte}", self._store))
        self.operations.append((f"JUMPZ {reg} {label}", self._jumpz))
        self.operations.append((f"ADD {reg} {reg} {reg}", self._add))
        self.operations.append((f"SUB {reg} {reg} {reg}", self._sub))
        self.operations.append((f"DEC {reg}", self._dec))
        self.operations.append((f"INC {reg}", self._inc))
        self.operations.append((f"LOADC {reg} {byte}", self._loadc))
        self.operations.append((f"COPY {reg} {reg}", self._copy))
        self.operations.append((f"STOP", self._stop))
        self.operations.append((f"{label}", self._label))

    def _loadm(self, op, line):
        match = re.match(op, line)
        reg = ord(match.group(1)) - ord("A")
        mem = int(match.group(2), 16)

        self.instructions.append((line, bytes([reg, mem])))

    def _store(self, op, line):
        match = re.match(op, line)
        reg = ord(match.group(1)) - ord("A")
        reg += 0x10
        mem = int(match.group(2), 16)

        self.instructions.append((line, bytes([reg, mem])))

    def _jumpz(self, op, line):
        pass

    def _add(self, op, line):
        match = re.match(op, line)
        reg1 = ord(match.group(1)) - ord("A")
        reg2 = ord(match.group(2)) - ord("A")
        reg3 = ord(match.group(3)) - ord("A")
        
        reg1 += 0x30
        reg3 += reg2 << 4
        
        self.instructions.append((line, bytes([reg1, reg3])))

    def _sub(self, op, line):
        match = re.match(op, line)
        reg1 = ord(match.group(1)) - ord("A")
        reg2 = ord(match.group(2)) - ord("A")
        reg3 = ord(match.group(3)) - ord("A")
        
        reg1 += 0x40
        reg3 += reg2 << 4
        
        self.instructions.append((line, bytes([reg1, reg3])))

    def _dec(self, op, line):
        match = re.match(op, line)
        reg = ord(match.group(1)) - ord("A")
        reg += 0x50
        
        self.instructions.append((line, bytes([reg, 0x00])))

    def _inc(self, op, line):
        match = re.match(op, line)
        reg = ord(match.group(1)) - ord("A")
        reg += 0x60
        
        self.instructions.append((line, bytes([reg, 0x00])))

    def _loadc(self, op, line):
        match = re.match(op, line)
        reg = ord(match.group(1)) - ord("A")
        reg += 0x70
        const = int(match.group(2), 16)

        self.instructions.append((line, bytes([reg, const])))

    def _copy(self, op, line):
        match = re.match(op, line)
        reg1 = ord(match.group(1)) - ord("A")
        reg2 = ord(match.group(2)) - ord("A")
        
        reg1 += 0x80
        reg2 <<= 4
        
        self.instructions.append((line, bytes([reg1, reg2])))

    def _stop(self, op, line):
        self.instructions.append((line, bytes([0xF0, 0x00])))

    def _label(self, op, line):
        pass

    def _read_instr(self, file):
        for line in file:
            line = line.strip()

            if line:
                [op[1](op[0], line) for op in self.operations if re.match(op[0], line)]

if __name__ == "__main__":
    a = Assembl("test.txt")
    print(a.instructions)
