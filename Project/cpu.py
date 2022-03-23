from numpy import ubyte

class CPU:
    """
    The CPU class simulate a CPU with 16 registers, 256 bytes of memory and 9 instructions
    """
    def __init__(self):
        """
        Initialize the registers, memory, and other variables
        """
        self.registers = [ubyte()] * 16
        self.memory = [ubyte()] * 256
        self.pointer = ubyte(0)
        self.current_memory = None
        self.has_jumped = False
        self.last_result = None
        self.is_stopped = False

        self._init_operations()

    def _init_operations(self):
        """
        The operations list is populated with the functions that will be
        called when the operations are executed
        """
        self.operations = [None] * 16

        self.operations[0] = self._loadm
        self.operations[1] = self._store
        self.operations[2] = self._jumpz
        self.operations[3] = self._add
        self.operations[4] = self._sub
        self.operations[5] = self._dec
        self.operations[6] = self._inc
        self.operations[7] = self._loadc
        self.operations[15] = self._stop

    def _loadm(self, i):
        """
        Load the value in the memory address into the specified register
        
        :param i: The instruction to be executed
        """
        self.registers[i[0] & 0x0F] = self.memory[i[1]]
        self.current_memory = i[1]
        self.last_result = self.registers[i[0] & 0x0F]

    def _store(self, i):
        """
        Store the value in the register into memory
        
        :param i: The instruction to be executed
        """
        self.memory[i[1]] = self.registers[i[0] & 0x0F]
        self.current_memory = i[1]
        self.last_result = self.memory[i[1]]

    def _jumpz(self, i):
        """
        Jump to the memory if the last value is zero
        
        :param i: The instruction to be executed
        """
        if self.last_result == ubyte(0):
            self.pointer = i[1]
            self.has_jumped = True
    
    def _add(self, i):
        """
        Add the last two registers into the first one
        
        :param i: The instruction to be executed
        """
        self.registers[i[0] & 0x0F] = self.registers[i[1] >> 4] + self.registers[i[1] & 0x0F]
        self.last_result = self.registers[i[0] & 0x0F]
    
    def _sub(self, i):
        """
        Substract the last two registers into the first one
        
        :param i: The instruction to be executed
        """
        self.registers[i[0] & 0x0F] = self.registers[i[1] >> 4] - self.registers[i[1] & 0x0F]
        self.last_result = self.registers[i[0] & 0x0F]
    
    def _dec(self, i):
        """
        Decrease the specified register
        
        :param i: The instruction to be executed
        """
        self.registers[i[0] & 0x0F] -= ubyte(1)
        self.last_result = self.registers[i[0] & 0x0F]
    
    def _inc(self, i):
        """
        Increase the specified register
        
        :param i: The instruction to be executed
        """
        self.registers[i[0] & 0x0F] += ubyte(1)
        self.last_result = self.registers[i[0] & 0x0F]
        
    def _loadc(self, i):
        """
        Load a constant into the specified register
        
        :param i: The instruction to be executed
        """
        self.registers[i[0] & 0x0F] = i[1]
        self.last_result = self.registers[i[0] & 0x0F]

    def _stop(self, i):
        """
        Stop the program
        
        :param i: The instruction to be executed
        """
        self.is_stopped = True
    
    def load(self, filename, start=0):
        """
        Load the contents of the file into memory starting at the given address
        
        :param filename: the name of the file to load
        :param start: the starting address of the program, defaults to 0 (optional)
        """
        with open(filename, "rb") as file:
            instr = file.read()
            instr = instr[:256 - start]
            self.memory[start:len(instr)] = instr
            self.pointer = ubyte(start)
        
    def next_instruction(self):
        """
        Read the next two bytes of memory and execute the instruction
        """
        if self.is_stopped:
            return

        self.has_jumped = False
        self.current_memory = None

        i = self.memory[self.pointer : self.pointer + 2]
        self.operations[i[0] >> 4]([ubyte(i[0]), ubyte(i[1])])
        
        if not self.has_jumped and not self.is_stopped:
            self.pointer += ubyte(2)
