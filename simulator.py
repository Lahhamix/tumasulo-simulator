"""Main simulator implementation for Tomasulo's algorithm.
This module implements the core simulator for Tomasulo's algorithm, a hardware algorithm
for dynamic scheduling of instructions that allows out-of-order execution and enables
more efficient use of multiple execution units.

Key components of Tomasulo's algorithm:
Register File: Contains register values and status
Functional Units: Execute instructions
Reservation Stations: Hold instructions waiting to execute
Common Data Bus (CDB): Broadcasts results to all waiting units
Load/Store Buffers: Handle memory operations


In the Tomasulo simulator, the actual computation of results occurs through a chain of method calls that model the processor's execution pipeline. The process begins in the simulator's main `tick()` method, which calls `write_back()` to handle completed instructions. Within `write_back()`, the simulator calls `functional_units.tick()`, which iterates through all functional units and calls their individual `tick()` methods. As each functional unit's `tick()` method decrements its `cycles_left` counter, it checks if execution has completed (when `cycles_left` reaches zero). At this precise moment, the functional unit calls its `compute_result()` method, which contains the actual computation logic specific to each operation type. For example, in the ALU's `compute_result()` method, addition is performed with `rs.vj + rs.vk`, while in the LoadStore unit, memory operations are executed with `memory.read(rs.address)` or `memory.write(rs.address, rs.vk)`. The computed result then flows back up the call chain to `write_back()`, where it's broadcast on the Common Data Bus (CDB) and used to update the register file and any waiting reservation stations. This multi-step process accurately models how a real processor executes instructions over multiple clock cycles, with computation occurring only after the appropriate execution latency has elapsed.

"""
from typing import List, Dict, Optional, Tuple, Any
from components.instruction import Instruction
from components.register_file import RegisterFile
from components.functional_unit import FunctionalUnits
from components.reservation_station import ReservationStations
from components.common_data_bus import CommonDataBus
from components.memory import Memory
from utils.metrics import Metrics
from utils.parser import TraceParser

class Simulator:
    """
    Main simulator class that orchestrates the Tomasulo algorithm simulation.
    
    This class coordinates all components of the simulator and implements the
    three main stages of Tomasulo's algorithm:
    1. Issue: Decode instructions and issue them to reservation stations
    2. Execute: Execute instructions when their operands are ready
    3. Write Result: Write results to the CDB and update dependent instructions
    """
    def __init__(self):
        """Initialize the simulator's components"""
        self.memory=Memory()       #Initialize the memory system
        self.register_file= RegisterFile()         #Initialize the register file
        self.functional_units=FunctionalUnits(self.memory)    # Initialize functional units (execute instructions)
        self.reservation_stations= ReservationStations()      # Initialize reservation stations (holds instructions waiting for their operands to be available)
        self.cdb=CommonDataBus()   # Initialize the Common Data Bus (broadcasts results)
        
        self.metrics= Metrics()    #Initialize the metrics collection 


        #Program state
        self.instructions: List[Instruction] = []    #list of instructions to execute
        self.pc=0          #program counter
        self.cycle=0       #current clock cycle
        self.done=False    #whether the simulation is complete or not

    
    def load_trace(self, filename):
        """
        Load instructions from a trace file.
        
        Parses the specified trace file and loads the instructions into the simulator.
        Resets the program counter and cycle count to start a new simulation.
        
        Args:
            filename: Path to the trace file
        """

        #Parse the trace file into a list of Instruction objects
        self.instructions=TraceParser.parse_file(filename)

        #Get the total number of instructions
        self.metrics.total_instrcutions= len(self.instructions)

        #Reset the program state
        self.pc=0
        self.cycle=0
        self.done=False

    def issue(self):
        """
        Issue the next instruction if possible.
        
        This implements the first stage of Tomasulo's algorithm:
        1. Get the next instruction from the program
        2. Find an available reservation station of the appropriate type
        3. Issue the instruction to the reservation station
        4. Update the register status table
        5. Advance the program counter
        
        Returns:
            True if an instruction was issued, False otherwise
        """

        # Check if we've reached the end of the program
        if self.pc >= len(self.instructions):
            return False
        
        #Get the next instrcution from self.instructions at index=self.pc 
        instruction=self.instructions[self.pc]
        op:str= instruction.op

        # Get an available reservation station for this operation type
        rs=self.reservation_stations.get_available_station(op)

        if rs is None:
            # No available reservation station, structural hazard
            self.metrics.increment_structural_hazard_stalls()
            return False
        
        #else i.e. if rs is not None
        #Mark the reservation station as busy
        rs.busy=True
        rs.op=op
        rs.instruction=instruction

        #Record the issue cycle for the metrics
        instruction.issue_cycle=self.cycle

        #Handle arithmetic opeartions
        if op in ['ADD','SUB','MUL','DIV']:
            rs.dest=instruction.dest

            #check source operands
            for src_reg, rs_field, v_field in [(instruction.src1, 'qj', 'vj'),(instruction.src2, 'qk', 'vk')]:
                # Check if the source register is waiting for a result
                status=self.register_file.get_status(src_reg)

                if status is not None:
                    #means that register is waiting for a result from a RS
                    setattr(rs, rs_field, status)   #Set the status of the source register in the reservation station

                else:
                    # Register value is available
                    setattr(rs, rs_field, None)    # Mark the source register as not waiting (no dependency)
                    setattr(rs, v_field, self.register_file.read(src_reg))      # Load the actual value from the register file into the reservation station

            #update register status to indicate which RS will write to the destination register
            self.register_file.set_status(instruction.dest, rs.name)

        elif op=='LOAD':
            #Handle load operations
            rs.dest=instruction.dest

            #Check base register
            base_reg=instruction.base
            status=self.register_file.get_status(base_reg)

            if status is not None:

                #Base reg is waiting for a result 
                rs.qj=status
            
            else:
                #Base register is available
                rs.qj=None
                rs.vj=self.register_file.read(base_reg)
            
            #Store the offset
            rs.offset=instruction.offset

            #Update the register status
            self.register_file.set_status(instruction.dest, rs.name)

        elif op=='STORE':
            #Handle store operations
            base_reg=instruction.base
            status=self.register_file.get_status(base_reg)

            if status is not None:

                #Base reg is waiting for a result 
                rs.qj=status
            
            else:
                #Base register is available
                rs.qj=None
                rs.vj=self.register_file.read(base_reg)
            
            #check source register
            src_reg=instruction.src1
            status=self.register_file.get_status(src_reg)

            if status is not None:

                #souce reg is waiting for a result 
                rs.qk=status
            
            else:
                #souce register is available
                rs.qk=None
                rs.vk=self.register_file.read(src_reg)

            #Store the offset
            rs.offset=instruction.offset

        #Advance the program counter
        self.pc+=1
        return True
    
    def execute(self):
        """
        Start execution of ready instructions.
        
        This implements the second stage of Tomasulo's algorithm:
        1. Find reservation stations that are ready to execute (all operands available)
        2. Assign them to available functional units
        3. Start execution
        
        For LOAD/STORE instructions, calculate the effective address when execution starts.
        """
        
        #Find ready reservation stations
        for rs in self.reservation_stations.all_stations:
            #check if the RS is ready and not executing
            if rs.isReady() and not rs.executing:
                # Get an available functional unit for this opeartion type
                fu=self.functional_units.get_available(rs.op)

                if fu is not None:
                    #start execution
                    fu.start_execution(rs)
                    rs.instruction.start_cycle=self.cycle

                    #For Load/STORE, calculate the effective address
                    if rs.op in ['LOAD','STORE']:
                        rs.address=rs.vj + rs.offset

    
    def write_back(self):
        """
        Write back results from functional units to the CDB.
        
        This implements the third stage of Tomasulo's algorithm:
        1. Check for completed executions in functional units
        2. Broadcast the result on the CDB
        3. Update the register file
        4. Update dependent reservation stations
        5. Clear the completed reservation station
        """

        #Clear the CDB from the previous cycle
        self.cdb.clear()

        #Get results from the functional units
        results=self.functional_units.tick()

        if results:
            # We have at least one result
            # In a real processor, we would need arbitration if multiple units complete
            # For simplicity, we'll just take the first result
            
            rs_name, result=results[0]

            #Broadcast on the CDB
            self.cdb.broadcast(rs_name, result)

            #Get the RS
            rs=self.reservation_stations.get_station_by_name(rs_name)

            if rs is not None:
                # Record completion cycle for metrics
                rs.instruction.execute_complete_cycle = self.cycle
                rs.instruction.write_result_cycle = self.cycle

                if rs.op in ['ADD','SUB','MUL','DIV','LOAD']:
                    #write the result in resgister file if it's not a store
                    dest_reg=rs.dest
                    self.register_file.write(dest_reg, result)

                    #Clear the register status if it's still pointing to the RS
                    if self.register_file.get_status(dest_reg)==rs_name:
                        self.register_file.set_status(dest_reg,None)
                
                #Update other reservation stations waiting for this result
                self.reservation_stations.update_from_cdb(rs_name, result)

                #clear the reservation station
                rs.clear()

                #Increment completed instructions counter
                self.metrics.completed_instructions+=1


    def tick(self):
        """
        Advance the simulation by one clock cycle.
        
        This is the main simulation loop that:
        1. Increments the clock cycle counter
        2. Updates metrics
        3. Executes the three stages of Tomasulo's algorithm in reverse order
           (write_back, execute, issue) to simulate in-order completion
        4. Checks if the simulation is complete
        
        Returns:
            True if the simulation should continue, False if it's done
        """
        #Increement the clock cycle counte
        self.cycle+=1
        self.metrics.total_cycles=self.cycle

        #Update metrics
        self.metrics.update_rs_occupancy(self.reservation_stations)
        self.metrics.update_ls_buffer_utilization(self.reservation_stations)


        # Execute in reverse order to simulate in-order completion
        # This ordering ensures that:
        # 1. Results are written back before new executions start
        # 2. New executions start before new instructions are issued
        # 3. New instructions are issued only after results are written and new executions start
        self.write_back()
        self.execute()
        issued=self.issue()

        # Check if the simulation is complete
        # We're done when:
        # 1. We've issued all instructions (pc >= len(instructions))
        # 2. No more instructions can be issued (!issued)
        # 3. All reservation stations are empty
        if (not issued and self.pc>=len(self.instructions) and all(not rs.busy for rs in self.reservation_stations.all_stations)):
            return False
        
        #if one of the conditions is not satisfied
        return True
    

    def run(self):
        """
        Run the simulation until completion.
        
        Repeatedly calls tick() until the simulation is complete,
        then returns a report of the performance metrics.
        
        Returns:
            String containing the performance metrics report
        """
        #Run until the simulation is complete
        while self.tick():  #i.e. while the simulation is still executing 
            pass

        #Return the perfomance metrics report
        return self.metrics.report()
    

    def run_step(self):
        """
        Run a single step of the simulation.
        
        This is useful for debugging or for step-by-step visualization.
        
        Returns:
            (continue, state) where continue is True if the simulation should continue,
            and state is a dictionary with the current state of the simulator
        """

        #Execute one clock cycle
        continue_simulation=self.tick()

        #Create a state dictionary for visualizing or debbugging
        state: Dict[str, Any] = {
            'cycle': self.cycle,
            'pc': self.pc,
            'registers': self.register_file.registers.copy(),
            'register_status': self.register_file.status.copy(),
            'reservation_stations': [
                {
                    'name': rs.name,
                    'busy': rs.busy,
                    'op': rs.op,
                    'vj': rs.vj,
                    'vk': rs.vk,
                    'qj': rs.qj,
                    'qk': rs.qk,
                    'dest': rs.dest,
                    'executing': rs.executing,
                    'cycles_left': rs.execution_cycles_left
                }
                for rs in self.reservation_stations.all_stations if rs.busy
            ],
            'cdb': {
                'name': self.cdb.reservation_station,
                'value': self.cdb.value,
                'busy': self.cdb.busy
            }
        }
        
        return continue_simulation, state
    



                    


           




                    
            




