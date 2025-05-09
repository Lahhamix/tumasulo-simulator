"""Functional unit implementation for Tomasulo's algorithm simulator."""

from utils.config import LATENCIES, NUM_ALU_UNITS, NUM_MUL_DIV_UNITS, NUM_LOAD_STORE_UNITS
from components.reservation_station import ReservationStation
from typing import Optional
from components.memory import Memory

class FunctionalUnit:
    """
    Base class for all functional units.
    """
    def __init__(self, name, supported_ops):
        """
        Initialize a functional unit.
        
        Args:
            name: Name of the functional unit
            supported_ops: List of operations supported by this unit
        """
        self.name=name
        self.supported_ops=supported_ops
        self.busy = False
        self.reservation_station: Optional[ReservationStation] = None  # Current reservation station being processed
        self.cycles_left = 0

    def can_accept(self,op): 
         """
        Check if the functional unit can accept the operation.
        
        Args:
            op: Operation to check
            
        Returns:
            True if the unit can accept the operation, False otherwise
        """
         return op in self.supported_ops and not self.busy
    
    def start_execution(self, reservation_station:ReservationStation):
        """
        Start executing an instruction from a reservation station.
        
        Args:
            reservation_station: Reservation station with the instruction to execute
        """
        self.busy=True
        self.reservation_station=reservation_station
        self.cycles_left=LATENCIES[reservation_station.op]
        reservation_station.executing=True
        reservation_station.execution_cycles_left = self.cycles_left

    def tick(self):
         """
        Advance the functional unit by one cycle.
        
        Returns:
            (rs_name, result) if execution completed, None otherwise
        """
         if not self.busy:
             return None
         
         self.cycles_left -=1
         self.reservation_station.execution_cycles_left -=1

         if self.cycles_left>0:
             return None

         elif self.cycles_left<=0:
            #Execution is complete
            result=self.compute_result()
            rs_name=self.reservation_station.name

            #reset the functional unit
            self.busy=False
            self.reservation_station.executing=False
            self.reservation_station=None

            return (rs_name, result)
         
    def compute_result(self):
        """
        Compute the result of the operation.
        To be implemented by subclasses.
        
        Returns:
            Result of the operation
        """
        raise NotImplementedError("Subclasses must implement compute_result")
        
class ALU(FunctionalUnit):
    """Arithmetic Logic Unit for ADD and SUB operations."""
    
    def __init__(self, name):
         """
        Initialize an ALU.
        
        Args:
            name: Name of the ALU
        """
         
         super().__init__(name, ['ADD','SUB'])

    def compute_result(self):
        """
        Compute the result of the ALU operation.
        
        Returns:
            Result of the operation

        Raises:
            ValueError: if the operation is different than ADD or SUB
        """
        rs=self.reservation_station

        if rs.op=='ADD':
            return rs.vj+rs.vk
        elif rs.op=='SUB':
            return rs.vj-rs.vk
        else:
            raise ValueError(f"The operation is unsupported in ALU:{rs.op}")
        
class MulDiv(FunctionalUnit):
    """Multiplication/Division Unit for MUL and DIV operations."""
    
    def __init__(self, name):
         """
        Initialize a MUL/DIV unit.
        
        Args:
            name: Name of the MUL/DIV unit
        """
         
         super().__init__(name, ['MUL','DIV'])

    def compute_result(self):
        """
        Compute the result of the MUL or DIV operation.
        
        Returns:
            Result of the operation

        Raises:
            ZeroDivisionError: if the seconf opearnd is zero in DIV operation
            ValueError: if the operation is different than MUL or DIV
        """
        rs=self.reservation_station

        if rs.op=='MUL':
            return rs.vj*rs.vk
        elif rs.op=='DIV':
            if rs.vk==0:
                print(f"Warning: Division by zero in instruction {rs.instruction}")
                return 0
            return rs.vj//rs.vk    # integer division
        else:
            raise ValueError(f"The operation is unsupported in MUL/DIV unit:{rs.op}")
        

class LoadStore(FunctionalUnit):
    """Load/Store Unit for LOAD and STORE operations."""

    def __init__(self,name, memory:Memory):
        """
        Initialize a LOAD/STORE unit.
        
        Args:
            name: Name of the LOAD/STORE unit
            memory: Memory instance
        """
        super().__init__(name, ['LOAD','STORE'])
        self.memory=memory

    def compute_result(self):
         """
        Compute the result of the LOAD or STORE operation.
        
        Returns:
            Result of the operation (Value for load, None for store)

        Raises:
            ValueError: if the operation is different than LOAD or STORE
        """
         rs=self.reservation_station
         if rs.op=='LOAD':
            # For LOAD, return the value from memory
            return self.memory.read(rs.address)       #read method in Memory class; reads from memory[rs.address]
         
         elif rs.op=='STORE':
            # For STORE, write the value to memory and return None
            self.memory.write(rs.address, rs.vk)      #write method in Memory class; writes to memory[rs.address]
            return None
         
         else:
             raise ValueError(f"Unsuuported operation in LoadStore:{rs.op}")


class FunctionalUnits:
    """
    Manages all functional units in the processor.
    """

    def __init__(self,memory:Memory):
        """
        Initialize all functional units.
        
        Args:
            memory: Memory instance for LOAD/STORE units
        """

        #Create ALUS
        self.alus=[ALU(f"ALU{i+1}") for i in range(NUM_ALU_UNITS)]

        #Create MUL/DIV unit
        self.mul_divs=[MulDiv(f"MULDIV{i+1}") for i in range(NUM_MUL_DIV_UNITS)]

         #Create LOAD/STORE unit
        self.load_stores=[LoadStore(f"LOADSTORE{i+1}", memory) for i in range(NUM_LOAD_STORE_UNITS)]

        #all units for easy iteration
        self.all_units=self.alus+ self.mul_divs + self.load_stores

    def get_available(self,op):
        """
        Get an available functional unit for the given operation.
        
        Args:
            op: Operation (ADD, SUB, MUL, DIV, LOAD, STORE)
            
        Returns:
            Available functional unit or None if none available
        """
        for unit in self.all_units:
            if unit.can_accept(op):
                return unit
        return None
    
    def tick(self):
         """
        Advance all functional units by one cycle.
        
        Returns:
            List of (rs_name, result) tuples for completed executions
        """
         
         results=[]
         for unit in self.all_units:
             result=unit.tick()
             if result is not None:
                 results.append(result)
         return results

        
             
    


