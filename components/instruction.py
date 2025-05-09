"""Instruction representation for Tomasulo's algorithm simulator."""
from utils.config import LATENCIES

class Instruction:
    """Represents an instruction in the simulation"""

    def __init__(self, op, dest=None, src1=None, src2=None, offset=None, base=None):
        """
        Initialize an instruction.
        
        Args:
            op: Operation (ADD, SUB, MUL, DIV, LOAD, STORE)
            dest: Destination register (None for STORE)
            src1: First source register (or source for STORE)
            src2: Second source register (None for LOAD/STORE)
            offset: Memory offset for LOAD/STORE (None for arithmetic operations)
            base: Base register for LOAD/STORE (None for arithmetic operations)
        """
        self.op=op
        self.dest=dest
        self.src1=src1
        self.src2=src2
        self.offset=offset
        self.base=base

        #Execution tracking
        self.issue_cycle=None  #Cycle when the instruction was issued
        self.start_cycle=None  #Cycle when execution started
        self.execute_complete_cycle=None  #Cycle when execution completed
        self.write_result_cycle=None      #Cycle when result was written

    def get_latency(self):
        """Return the latency for this instruction type"""
        return LATENCIES[self.op]  #return the value (latency) of the op from LATENCIES dictionnary
    
    def is_arithmetic(self):
        """Check if this is an arithmetic instruction
           Return True if the operation is arithmetic(ADD, SUB, DIV, MUL)
           Return False otherwise
        """

        return self.op in ['ADD', 'SUB','MUL','DIV']
    
    def is_memory_op(self):
        """Check if this is a memory operation
           Return True if op is a memory operation (LOAD, STORE)
           Return False otherwise
        """

        return self.op in ['LOAD','STORE']
    
    def __str__(self):
        """Return string representation of the instruction"""

        if self.is_arithmetic():
            return f"{self.op} {self.dest} , {self.src1} , {self.src2}"
        elif self.op=='LOAD':
            return f"{self.op} {self.dest} , {self.offset} ({self.base})"
        elif self.op=='STORE':
            return f"{self.op} {self.offset} ({self.base}), {self.src1} "
        else:
            return "The instruction is unknown"
        

    @classmethod
    def parse(cls, instruction_str):
        """
        Parse an instruction string into an Instruction object.
        
        Args:
            instruction_str: String representation of the instruction
            
        Returns:
            Instruction object
        """
        
        # Remove leading/trailing spaces and split the string by spaces
        parts = instruction_str.strip().split()
        
        # The first part is the operation (e.g., ADD, LOAD, etc.), converted to uppercase
        op = parts[0].upper()
        
        # Handle arithmetic operations: ADD, SUB, MUL, DIV
        if op in ['ADD', 'SUB', 'MUL', 'DIV']:
            # Join the remaining parts, remove spaces, then split by commas
            operands = ' '.join(parts[1:]).replace(' ', '').split(',')
            
            # Extract destination and source operands
            dest = operands[0]
            src1 = operands[1]
            src2 = operands[2]
            
            # Create and return a new Instruction object
            return cls(op, dest, src1, src2)
            
        # Handle LOAD operation
        elif op == 'LOAD':
            # Join the remaining parts, remove spaces, then split by commas
            operands = ' '.join(parts[1:]).replace(' ', '').split(',')
            
            # Destination register
            dest = operands[0]
            
            # Memory reference part: OFFSET(BASE)
            mem_ref = operands[1]
            offset_base = mem_ref.split('(')
            
            # Extract offset and base register
            offset = int(offset_base[0])           # Offset as integer
            base = offset_base[1].rstrip(')')       # Base register, removing the closing parenthesis
            
            # Create and return a new Instruction object
            return cls(op, dest, offset=offset, base=base)
            
        # Handle STORE operation
        elif op == 'STORE':
            # Join the remaining parts, remove spaces, then split by commas
            operands = ' '.join(parts[1:]).replace(' ', '').split(',')
            
            # Memory reference part: OFFSET(BASE)
            mem_ref = operands[0]
            offset_base = mem_ref.split('(')
            
            # Extract offset and base register
            offset = int(offset_base[0])           # Offset as integer
            base = offset_base[1].rstrip(')')       # Base register, removing the closing parenthesis
            
            # Source register
            src1 = operands[1]
            
            # Create and return a new Instruction object
            return cls(op, src1=src1, offset=offset, base=base)
            
        # If the operation is unknown, raise an error
        else:
            raise ValueError(f"Unknown operation: {op}")


            
