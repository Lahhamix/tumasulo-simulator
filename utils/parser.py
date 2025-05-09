"""Instruction trace parser for Tomasulo's algorithm simulator."""

from components.instruction import Instruction

class TraceParser:
    """
    Parser for instruction trace files.
    This class provides functionality to parse a file containing a list of instructions
    and return them as a list of Instruction objects.
    """

    @staticmethod
    def parse_file(filename):
        """
        Parses a trace file and converts its lines into a list of Instruction objects.

        Args:
            filename: Path to the trace file to be parsed.
            
        Returns:
            List of Instruction objects parsed from the file.
        """
        # List to store the parsed Instruction objects
        instructions = []

        # Open the file in read mode
        with open(filename, 'r') as f:
            # Enumerate over each line in the file, starting line numbers from 1
            for line_num, line in enumerate(f, 1):
                # Remove leading and trailing whitespace from the line
                line = line.strip()

                # Skip empty lines or lines that are comments (starting with '#')
                if not line or line.startswith('#'):
                    continue

                try:
                    # Attempt to parse the line into an Instruction object, the method is defined in Intruction class
                    instruction = Instruction.parse(line)

                    # Add the successfully parsed instruction to the list
                    instructions.append(instruction)

                except ValueError as e:
                    # If parsing fails, print an error message along with the line number and content
                    print(f"Error parsing line {line_num}: {e}")
                    print(f"Line: {line}")

        # Return the list of successfully parsed instructions
        return instructions
