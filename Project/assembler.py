import re
import sys
from tracemalloc import start

class Assembler:
    def __init__(self, start=0):
        self._init_operations()
        self.instructions = []
        self.labels = {}
        self.start = start

    def _init_operations(self):
        self.operations = []

        reg = r"([A-R])"
        byte = r"([0-9A-F]{2})"
        label = r"([A-Z]+:)"

        self.operations.append((f"LOADM {reg} {byte}", self._loadm))
        self.operations.append((f"STORE {reg} {byte}", self._store))
        self.operations.append((f"JUMPZ {label}", self._jumpz))
        self.operations.append((f"ADD {reg} {reg} {reg}", self._add))
        self.operations.append((f"SUB {reg} {reg} {reg}", self._sub))
        self.operations.append((f"DEC {reg}", self._dec))
        self.operations.append((f"INC {reg}", self._inc))
        self.operations.append((f"LOADC {reg} {byte}", self._loadc))
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
        self.instructions.append((line, None))

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

    def _stop(self, op, line):
        self.instructions.append((line, bytes([0xF0, 0x00])))

    def _label(self, op, line):
        match = re.match(op, line)
        label = match.group(1)
        self.labels[label] = len(self.instructions) * 2 + self.start

    def _read_instr(self, file):
        for i, line in enumerate(file):
            line = line.strip()
            line = line.upper()

            if line:
                if not [op[1](op[0], line) for op in self.operations if re.fullmatch(op[0], line)]:
                    print(f"Line {i + 1} not reconized")
                    sys.exit(1)

        self._create_jumps()

    def _create_jumps(self):
        jump_op = self.operations[2]

        for i, instr in enumerate(self.instructions):
            if instr[1] is None:
                match = re.match(jump_op[0], instr[0])
                label = match.group(1)
                mem = self.labels[label]

                self.instructions[i] = (instr[0], bytes([0x20, mem]))

    def _write_instr(self, file):
        for instr in self.instructions:
            file.write(instr[1])

    def assemble(self, input_filename, output_filename):
        self.instructions.clear()
        self.labels.clear()
        
        with open(input_filename) as file:
            self._read_instr(file)

        with open(output_filename, "wb+") as file:
            self._write_instr(file)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Need 2 arguments, the source and the destination")
        sys.exit(1)

    a = Assembler()
    a.assemble(sys.argv[1], sys.argv[2])
