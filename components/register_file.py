"""Represents the register file and register status table."""
import random
from utils.config import NUM_REGISTERS

class RegisterFile:
    """Represents the register file in the processor.
    Tracks both the actual values and the status of each register."""

    def __init__(self):
        """Initialize the register file."""
        # Initialize R0 to 0, R1-R7 to random values between 1 and 100
        self.registers = [0] + [random.randint(1, 100) for _ in range(1, NUM_REGISTERS)]

        # Status indicates which reservation station will write to this register
        # None means the register is not waiting for any result
        self.status = [None] * NUM_REGISTERS
    
    def get_register_index(self, reg_name):
         """
        Convert register name (e.g., 'R1') to index (e.g., 1).
        
        Args:
            reg_name: Register name (e.g., 'R1')
            
        Returns:
            Register index (e.g., 1)
            
        Raises:
            ValueError: If the register name is invalid or if the register index is not between 0 and 7
        """
         if not reg_name.startswith('R'):
             raise ValueError(f"Inavalid register name:{reg_name}")
         
         index=int(reg_name[1:])

         if index<0 or index>=NUM_REGISTERS:
             raise ValueError(f'Register index out of range:{index}')
         
         return index
    
    def read(self, reg_name):
        """
        Read the value of a register.
        
        Args:
            reg_name: Register name (e.g., 'R1')
            
        Returns:
            The value of the register
        """
        index=self.get_register_index(reg_name)
        return self.registers[index]     #content of registers[index]
    
    def write(self, reg_name, value):
         """
        Writes the value of a register.
        
        Args:
            reg_name: Register name (e.g., 'R1')
            value: the value to write in the register
        Returns:
            Doesn't return
        """
         index=self.get_register_index(reg_name)
         self.registers[index]=value

    def get_status(self, reg_name):
        """
        Get the status of a register.
        
        Args:
            reg_name: Register name (e.g., 'R1')
            
        Returns:
            The reservation station that will write to this register, or None
        """
        index=self.get_register_index(reg_name)
        return self.status[index]
    
    def set_status(self, reg_name, reservation_station):
        """
        Set the status of a register

        Args:
            reg_name: Register name (e.g. 'R2')
            reservation_station: Reservation station name (e.g., 'ALU1') or None
        """
        index=self.get_register_index(reg_name)
        self.status[index]=reservation_station

    def clear_status(self, reservation_station):
        """
        Clear the status of all registers that were waiting for a specific reservation station.
        Args:
            reg_name: Register name (e.g. 'R2')
    
        """
        for i in range(NUM_REGISTERS):
            if self.status[i]==reservation_station:
                self.status[i]=[None]

    def is_available(self, reg_name):
        """
        Check if a register is available
         Args:
            reg_name: Register name (e.g. 'R2')

        Returns:
                True if register is available
                False otherwise
    
        """  
        index=self.get_register_index(reg_name)
        return self.status[index] is None




         
        

        