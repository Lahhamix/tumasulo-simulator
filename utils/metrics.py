"""Metrics collection for Tomasulo's algorithm simulator."""
from components import reservation_station

class Metrics:
    """
    Collects and reports performance metrics for the simulation.
    """

    def __init__(self):
        """Initialize metrics collection."""

        self.total_cycles=0
        self.total_instrcutions=0
        self.completed_instructions=0

        #RS occupancy tracking
        self.rs_busy_cycles=0
        self.total_rs_cycles=0

        #LOAD/STORE buffer utilization tracking
        self.ls_buffer_busy_cycles=0
        self.total_ls_buffer_cycles=0

        #Structural hazard tracking
        self.structural_hazard_stalls = 0

    def update_rs_occupancy(self, reservation_stations):
         """
        Update reservation station occupancy metrics.
        
        Args:
            reservation_stations: ReservationStations object
        """
         
         # Count busy ALU and MUL/DIV stations
         for station in reservation_stations.alu_stations + reservation_stations.mul_div_stations:
            if station.busy:
                self.rs_busy_cycles += 1

         # Update total cycles
         self.total_rs_cycles += len(reservation_stations.alu_stations) + len(reservation_stations.mul_div_stations)
         
    def update_ls_buffer_utilization(self, reservation_stations):
        """
        Update load/store buffer utilization metrics.
        
        Args:
            reservation_stations: ReservationStations object
        """
        # Count busy load and store buffers
        for buffer in reservation_stations.load_buffers + reservation_stations.store_buffers:
            if buffer.busy:
                self.ls_buffer_busy_cycles += 1
        
        # Update total cycles
        self.total_ls_buffer_cycles += len(reservation_stations.load_buffers) + len(reservation_stations.store_buffers)

    def increment_structural_hazard_stalls(self):
        """Increment the structural hazard stalls."""
        self.structural_hazard_stalls += 1

    def report(self):
        """
        Generate a report of the collected metrics.
        
        Returns:
            String containing the metrics report
        """
        # Calculate derived metrics
        ipc = self.completed_instructions / self.total_cycles if self.total_cycles > 0 else 0
        rs_occupancy_percent = (self.rs_busy_cycles / self.total_rs_cycles * 100) if self.total_rs_cycles > 0 else 0
        ls_buffer_utilization_percent = (self.ls_buffer_busy_cycles / self.total_ls_buffer_cycles * 100) if self.total_ls_buffer_cycles > 0 else 0
        stall_percent = (self.structural_hazard_stalls / self.total_cycles * 100) if self.total_cycles > 0 else 0
        
        # Format the report
        report = "=== Performance Metrics ===\n"
        report += f"Total execution time: {self.total_cycles} cycles\n"
        report += f"Instructions per cycle (IPC): {ipc:.2f}\n"
        report += f"Average reservation station occupancy: {rs_occupancy_percent:.2f}%\n"
        report += f"Load/store buffer utilization: {ls_buffer_utilization_percent:.2f}%\n"
        report += f"Structural hazard stalls: {self.structural_hazard_stalls} cycles ({stall_percent:.2f}%)\n"
        
        return report