"""Represents a reservation station in Tomasulo's algorithm. """

from utils.config import NUM_ALU_RS, NUM_MUL_DIV_RS, NUM_LOAD_BUFFER_ENTRIES, NUM_STORE_BUFFER_ENTRIES
from components.instruction import Instruction
from typing import Optional
class ReservationStation:
    """
    Base class for all reservation stations.
    """
    def __init__(self, name, op=None, vj=None, vk=None, qj=None, qk=None, busy=False):
        """
        Initialize a reservation station.
        
        Args:
            name: Name of the reservation station (e.g., "Add1", "Mult2")
            op: Operation to perform (e.g., "ADD", "SUB", "MULT")
            vj: Value of the first operand, if available
            vk: Value of the second operand, if available
            qj: Name of the reservation station that will produce the first operand, if not available
            qk: Name of the reservation station that will produce the second operand, if not available
            busy: True if the reservation station is currently in use
        """
        self.name = name
        self.op = op  #Operation type
        self.vj = vj  #value of first operand
        self.vk = vk  #value of second operand
        self.qj = qj  #reservation station producing first operand
        self.qk = qk  #reservation station producing ssecond operand
        self.busy = busy
        
        
        self.functional_unit=None               
        self.dest=None              #destination register
        self.instruction: Optional[Instruction] = None      #instruction being executed
        self.offset=None             #memory offset for LOAD/STORE
        self.address=None            #computed memory address for LOAD/STORE
        self.executing = False  # Whether the instruction is currently executing
        self.execution_cycles_left = 0  # Cycles left for execution

    def isReady(self):
        """
        Check if this station is ready to execute

        Returns:
            True if RS is ready to execute
            False otherwise
        """

        return self.busy and not self.executing and self.qj is None and self.qk is None # Return True only if:
                                                                                        # - the unit is busy,
                                                                                        # - it is NOT currently executing an instruction,
                                                                                        # - and it has no pending operands
    
    def clear(self):
        """Clear reservation station"""
        self.functional_unit=None
        self.busy=False
        self.op=None                
        self.vj=None                
        self.vk=None                
        self.qj=None                
        self.qk=None                
        self.dest=None              
        self.instruction=None       
        self.address=None            
        self.executing = False  
        self.execution_cycles_left = 0  

    def update_operand(self, reservation_station_name, value):
        """
        Update operands if they are waiting for a result from the specified reservation station.
        
        Args:
            reservation_station_name: Name of the reservation station that produced a result
            value: The result value
            
        Returns:
            True if any operand was updated, False otherwise
        """
        updated=False

        if self.qj==reservation_station_name:
            self.qj=None
            self.vj=value
            updated=True

        if self.qk==reservation_station_name:
            self.qk=None
            self.vk=value
            updated=True

        return updated
    
class ALUReservationStation(ReservationStation):
    """Reservation station for ALU operations (ADD, SUB)."""
    def __init__(self, name):
        """
        Initialize an ALU reservation station.
        
        Args:
            name: Name of the reservation station
        """
        super().__init__(name)

class MulDivReservationStation(ReservationStation):
    """Reservation station for MUL/DIV operations."""
    def __init__(self, name):
        """
        Initialize a MUL/DIV reservation station.
        
        Args:
            name: Name of the reservation station
        """
        super().__init__(name)

class LoadBuffer(ReservationStation):
    """Load buffer for LOAD operations."""
    def __init__(self, name):
        """
        Initialize a load buffer.
        
        Args:
            name: Name of the load buffer
        """
        super().__init__(name)
        # For load buffer, we only need vj (base register) and address (offset)
        self.vk = None  # Not used
        self.qk = None  # Not used

class StoreBuffer(ReservationStation):
    """Store buffer for STORE operations."""
    def __init__(self, name):
        """
        Initialize a store buffer.
        
        Args:
            name: Name of the store buffer
        """
        super().__init__(name)
        # For store buffer, we need vj (base register), vk (value to store), and address (offset)

class ReservationStations:
    """
    Manages all reservation stations in the processor.
    """
    def __init__(self):
        """Initialize all reservation stations."""
        # Create ALU reservation stations
        self.alu_stations = [ALUReservationStation(f"ALU{i+1}") for i in range(NUM_ALU_RS)]
        
        # Create MUL/DIV reservation stations
        self.mul_div_stations = [MulDivReservationStation(f"MUL{i+1}") for i in range(NUM_MUL_DIV_RS)]
        
        # Create load buffers
        self.load_buffers = [LoadBuffer(f"LOAD{i+1}") for i in range(NUM_LOAD_BUFFER_ENTRIES)]
        
        # Create store buffers
        self.store_buffers = [StoreBuffer(f"STORE{i+1}") for i in range(NUM_STORE_BUFFER_ENTRIES)]
        
        # All stations for easy iteration
        self.all_stations = (
            self.alu_stations + 
            self.mul_div_stations + 
            self.load_buffers + 
            self.store_buffers
        )
    
    def get_station_by_name(self, name):
        """
        Get a reservation station by name.
        
        Args:
            name: Name of the reservation station
            
        Returns:
            The reservation station, or None if not found
        """
        for station in self.all_stations:
            if station.name == name:
                return station
        return None
    
    def get_available_station(self, op):
        """
        Get an available reservation station for the given operation.
        
        Args:
            op: Operation (ADD, SUB, MUL, DIV, LOAD, STORE)
            
        Returns:
            Available reservation station or None if none available
        """
        if op in ['ADD', 'SUB']:
            for station in self.alu_stations:
                if not station.busy:
                    return station   #return RS that is available
        elif op in ['MUL', 'DIV']:
            for station in self.mul_div_stations:
                if not station.busy:
                    return station
        elif op == 'LOAD':
            for entry in self.load_buffers:
                if not entry.busy:
                    return entry
        elif op == 'STORE':
            for entry in self.store_buffers:
                if not entry.busy:
                    return entry
        return None
    
    def update_from_cdb(self, cdb_name, cdb_value):
        """
        Update reservation stations with a value from the CDB.
        
        Args:
            cdb_name: Name of the reservation station that produced the result
            cdb_value: Value produced
        """
        for station in self.all_stations:
            if station.qj == cdb_name:
                station.qj = None
                station.vj = cdb_value

            if station.qk == cdb_name:
                station.qk = None
                station.vk = cdb_value


