import sys

COMP_MAP = { # "M" = "A"
    "0": "101010",
    "1": "111111",
    "-1": "111010",
    "D": "001100",
    "A": "110000", 
    "!D": "001101",
    "!A": "110001",
    "-D": "001111",
    "-A": "110011",
    "D+1": "011111",
    "A+1": "110111",
    "D-1": "001110",
    "A-1": "110010",
    "D+A": "000010",
    "D-A": "010011",
    "A-D": "000111",
    "D&A": "000000",
    "D|A": "010101"
}
DEST_MAP = {
    "M": "001",
    "D": "010",
    "DM": "011",
    "MD": "011",
    "A": "100",
    "AM": "101",
    "MA": "101",
    "AD": "110",
    "DA": "110",
    "ADM": "111",
    "AMD": "111",
    "DAM": "111",
    "MAD": "111",
    "DMA": "111",
    "MDA": "111"
}
JUMP_MAP = {
    "JGT": "001",
    "JEQ": "010",
    "JGE": "011",
    "JLT": "100",
    "JNE": "101",
    "JLE": "110",
    "JMP": "111"
}

class Assembler:
    def __init__(self, input_file):
        self.input_file = input_file
        self.output_file = input_file.replace('.asm', '.hack')
        self.symbol_table = self.initialize_symbol_table()
        self.instructions = []
        self.binary_instructions = []
        self.next_variable_address = 16  # starting address for non-predefined variables

    def initialize_symbol_table(self):
        """Initializes the symbol table with predefined Hack symbols."""
        symbol_table = {
            'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4,
            'SCREEN': 16384, 'KBD': 24576
        }
        for i in range(16):
            symbol_table[f'R{i}'] = i
        return symbol_table

    def parse_file(self):
        """Reads the input file and strips out comments and whitespace."""
        with open(self.input_file, 'r') as file:
            for line in file:
                clean_line = self.clean_line(line)
                if clean_line:
                    self.instructions.append(clean_line)

    def clean_line(self, line):
        """Removes comments and whitespace from a line."""
        line = line.split('//')[0]  # remove comments
        return line.strip()  # remove whitespace

    def first_pass(self):
        """First pass to record label symbols in the symbol table."""
        current_address = 0
        for instruction in self.instructions:
            if instruction.startswith('(') and instruction.endswith(')'):
                label = instruction[1:-1]
                self.symbol_table[label] = current_address
            else:
                current_address += 1

    def second_pass(self):
        """Second pass to translate A and C instructions to binary."""
        for instruction in self.instructions:
            if instruction.startswith('('):
                continue  # skip labels
            elif instruction.startswith('@'):
                self.binary_instructions.append(self.translate_a_instruction(instruction))
            else:
                self.binary_instructions.append(self.translate_c_instruction(instruction))

    def translate_a_instruction(self, instruction):
        """Translates an A-instruction to binary."""
        symbol = instruction[1:]
        if symbol.isdigit():
            address = int(symbol)
        else:
            address = self.get_symbol_address(symbol)
        return f'0{address:015b}'

    def translate_c_instruction(self, instruction):
        """Translates a C-instruction to binary."""
        a = "0"
        dest = "000"
        jump = "000"
        if "=" in instruction:
            split = instruction.split("=")
            dest = DEST_MAP[split[0]]
            instruction = split[1]
        if ";"  in instruction:
            split = instruction.split(";")
            jump = JUMP_MAP[split[1]]
            instruction = split[0]
        if "M" in instruction:
            a = "1"
            instruction = instruction.replace("M", "A")
        comp = COMP_MAP[instruction]
        return "111"+a+comp+dest+jump
        

    def get_symbol_address(self, symbol):
        """Gets the address for a symbol, adding it to the symbol table if necessary."""
        if symbol not in self.symbol_table:
            self.symbol_table[symbol] = self.next_variable_address
            self.next_variable_address += 1
        return self.symbol_table[symbol]

    def write_output(self):
        """Writes the binary instructions to the output file."""
        instructions = "\n".join(self.binary_instructions)
        with open(self.output_file, 'w') as file:
            file.write(instructions)

    def assemble(self):
        """Coordinates the assembly process."""
        self.parse_file()
        self.first_pass()
        self.second_pass()
        self.write_output()


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 Assembler.py <file.asm>")
        sys.exit(1)

    input_file = sys.argv[1]
    assembler = Assembler(input_file)
    assembler.assemble()
    print(f"Assembly complete. Output written to {assembler.output_file}")
