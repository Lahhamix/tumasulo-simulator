"""Common Data Bus implementation for Tomasulo's algorithm simulator."""

class CommonDataBus:
    """
    Represents the Common Data Bus (CDB) in the processor.
    """

    def __init__(self):
        """
        Initializse the Common Data Bus
        """
        self.reservation_station=None   # name of the RS that produced the result
        self.value=None   #the result 
        self.busy=None     #if the CDB is busy for a given cycle

    def broadcast(self, reservation_station, value):
        """
        Broadcast a value on the CDB

        Args:
            name: Name of the reservation station that produced the result
            value: Value to broadcast
            
        Returns:
            True if broadcast successful, False if CDB is busy
        """
        if self.busy==True:
            return False
        
        self.reservation_station=reservation_station
        self.value=value
        self.busy=True
        return True
    
    def clear(self):
        """
        Clear the CDB for the next cycle
        """
        self.reservation_station=None   
        self.value=None    
        self.busy=None
