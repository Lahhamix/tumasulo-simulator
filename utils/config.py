"""Configuration constants for the simulator."""

#Register configuration
NUM_REGISTERS=8  #R0 -> R7

#Functional Units configuration
NUM_ALU_UNITS=2
NUM_MUL_DIV_UNITS=1
NUM_LOAD_STORE_UNITS=1

#Reservation Stations configuration
NUM_ALU_RS=3      #shared for the two alus
NUM_MUL_DIV_RS=2
NUM_LOAD_BUFFER_ENTRIES=2
NUM_STORE_BUFFER_ENTRIES=2

#Latencies configuration
LATENCIES={
    'ADD':2,
    'SUB':2,
    'MUL':10,
    'DIV':20,
    'LOAD': 5,
    'STORE':5
}

#Memory Configuration
MEMORY_SIZE=1024
