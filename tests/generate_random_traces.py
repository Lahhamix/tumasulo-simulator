import os
import random

# Directory to save the generated trace files
TRACE_DIR = os.path.join(os.path.dirname(__file__), 'sample_traces')

# Ensure the directory exists
os.makedirs(TRACE_DIR, exist_ok=True)

MEMORY_SIZE = 1024
REGISTERS = [f'R{i}' for i in range(8)]

INSTRUCTIONS = [
    'ADD {dest}, {src1}, {src2}',
    'SUB {dest}, {src1}, {src2}',
    'MUL {dest}, {src1}, {src2}',
    'DIV {dest}, {src1}, {src2}',
    'LOAD {dest}, {offset}({base})',
    'STORE {offset}({base}), {src}'
]


def generate_valid_offset(base_val):
    # Pick an offset so that base_val + offset is in [0, MEMORY_SIZE-1]
    min_offset = -base_val
    max_offset = MEMORY_SIZE - 1 - base_val
    # Clamp to a reasonable range for variety
    min_offset = max(min_offset, -32)
    max_offset = min(max_offset, 32)
    if min_offset > max_offset:
        min_offset, max_offset = 0, 0
    return random.randint(min_offset, max_offset)


def generate_trace_file(filename, num_instructions=10):
    # Simulate a register file: R0=0, R1-R7 random
    reg_values = [0] + [random.randint(1, 100) for _ in range(1, 8)]
    lines = []
    for _ in range(num_instructions):
        instr_type = random.choice(INSTRUCTIONS)
        if instr_type.startswith('LOAD'):
            dest = random.choice(REGISTERS[1:])  # Don't load into R0
            base_idx = random.randint(0, 7)
            base_val = reg_values[base_idx]
            offset = generate_valid_offset(base_val)
            # Update the destination register with a random value (simulate load)
            reg_values[int(dest[1:])] = random.randint(1, 100)
            line = f'LOAD {dest}, {offset}({REGISTERS[base_idx]})'
        elif instr_type.startswith('STORE'):
            src_idx = random.randint(1, 7)
            base_idx = random.randint(0, 7)
            base_val = reg_values[base_idx]
            offset = generate_valid_offset(base_val)
            line = f'STORE {offset}({REGISTERS[base_idx]}), {REGISTERS[src_idx]}'
        elif instr_type.startswith('DIV'):
            dest_idx = random.randint(1, 7)
            src1_idx = random.randint(0, 7)
            src2_idx = random.randint(1, 7)  # Never divide by R0
            dest = REGISTERS[dest_idx]
            src1 = REGISTERS[src1_idx]
            src2 = REGISTERS[src2_idx]
            reg_values[dest_idx] = reg_values[src1_idx] // reg_values[src2_idx] if reg_values[src2_idx] != 0 else 0
            line = instr_type.format(dest=dest, src1=src1, src2=src2)
        else:
            dest_idx = random.randint(1, 7)
            src1_idx = random.randint(0, 7)
            src2_idx = random.randint(0, 7)
            dest = REGISTERS[dest_idx]
            src1 = REGISTERS[src1_idx]
            src2 = REGISTERS[src2_idx]
            # Simulate the result (for future loads/stores)
            if instr_type.startswith('ADD'):
                reg_values[dest_idx] = reg_values[src1_idx] + reg_values[src2_idx]
            elif instr_type.startswith('SUB'):
                reg_values[dest_idx] = reg_values[src1_idx] - reg_values[src2_idx]
            elif instr_type.startswith('MUL'):
                reg_values[dest_idx] = reg_values[src1_idx] * reg_values[src2_idx]
            line = instr_type.format(dest=dest, src1=src1, src2=src2)
        lines.append(line)
    with open(os.path.join(TRACE_DIR, filename), 'w') as f:
        for line in lines:
            f.write(line + '\n')


def main():
    for i in range(1, 6):
        filename = f'trace_random_{i}.txt'
        generate_trace_file(filename, num_instructions=random.randint(8, 15))
    print(f"Generated 5 random trace files in {TRACE_DIR}")


if __name__ == '__main__':
    main() 