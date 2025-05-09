"""Memory system implementation for Tomasulo's algorithm simulator."""
from utils.config import MEMORY_SIZE

class Memory:
    """Represents the memory system in the processor."""

    def __init__(self):
        """Initialize the memory system."""
        # Initialize memory with zeros
        self.memory=[0]*MEMORY_SIZE

    def read(self, address):
        """
        Read a value from memory

        Args:
            address: memory location
        
        Returns:
            Value at the address
        Raises:
            ValueError: If the address is out of range
        """
        if address < 0 or address >= MEMORY_SIZE:
            print(f"Warning: Memory address out of range: {address}. LOAD skipped.")
            return 0
        return self.memory[address]
    

    def write(self, address, value):
        """
        Write a value to memory

        Args:
            address: memory location
            value: value to be written in memory
        
        Raises:
            ValueError: If the address is out of range
        """

        if address < 0 or address >= MEMORY_SIZE:
            print(f"Warning: Memory address out of range: {address}. STORE skipped.")
            return
        
        self.memory[address] = value

    