import sys, os
from TranslationFunctions import bootstrap,\
                                 push_instruction,\
                                 pop_instruction,\
                                 arithmetic_logical_instruction,\
                                 label,\
                                 goto_instruction,\
                                 if_goto_instruction,\
                                 call_instruction,\
                                 function_instruction,\
                                 return_instruction,\
                                 ALL_ARITHMETIC_LOGICAL_OPS, nl

class Translator:
    def __init__(self, input_file: str):
        self.input_file = input_file
        if input_file.endswith("/") or input_file.endswith("\\"):
            input_file = input_file[:-1]
        path = os.path.basename(input_file).rsplit('.', 1)
        if path[1] != "vm":
            print("ERROR: file type should be .vm")
            sys.exit(1)
        #elif not path[0][0].isupper() and path[0][0].isdigit():
        #    print(f"ERROR: file should start with a capital letter: {path[0]}.vm")
        #    sys.exit(1)
        self.name = path[0]
        self.output_file = input_file.replace('.vm', '.asm')
        self.instructions = []
        self.asm_instructions = []
        self.curr_function = ""
        self.num_of_returns = 0
        self.num_of_jumps = 0

    def parse_file(self):
        """Reads the input file and strips out comments and whitespace."""
        with open(self.input_file, 'r') as file:
            for line in file:
                clean_line = self.clean_line(line)
                if len(clean_line):
                    self.instructions.append(clean_line)

    def clean_line(self, line: str):
        """Removes comments and whitespace from a line."""
        line = line.split('//')[0]  # remove comments
        return line.strip()  # remove whitespace
    
    def clean_instructions(self):
        if not self.asm_instructions:
            return
            raise Exception("no assembly code to clean!")
        cleaned = []
        self.asm_instructions = (nl.join(self.asm_instructions)).split(nl)
        for line in self.asm_instructions:
            if line.startswith("//") or set(line).issubset(set([" ", "/", nl])):
                continue
            cleaned.append(line)
        self.asm_instructions = cleaned        
    
    def write_output(self):
        """Writes the binary instructions to the output file."""
        instructions = nl.join(self.asm_instructions)
        with open(self.output_file, 'w') as file:
            file.write(instructions)

    
    def translate(self):
        """Coordinates the VM translation process."""
        self.parse_file()
        for i, instruction in enumerate(self.instructions):
            try:
                args = instruction.split(" ")
                if args[0] == "label":
                    self.asm_instructions.append(label(args[1], self.curr_function))
                elif args[0] == "goto":
                    self.asm_instructions.append(goto_instruction(args[1], self.curr_function))
                elif args[0] == "if-goto":
                    self.asm_instructions.append(if_goto_instruction(args[1], self.curr_function))
                elif args[0] == "call":
                    self.asm_instructions.append(call_instruction(caller=self.curr_function, callee=args[1], argsNum=int(args[2]), return_tag=self.num_of_returns))
                    self.num_of_returns += 1
                elif args[0] == "function":
                    self.curr_function = args[1]
                    self.asm_instructions.append(function_instruction(args[1], int(args[2])))
                elif args[0] == "return":
                    self.asm_instructions.append(return_instruction())
                elif args[0] == "push":
                    self.asm_instructions.append(push_instruction(args[1], args[2], self.name))
                elif args[0] == "pop":
                    self.asm_instructions.append(pop_instruction(args[1], args[2], self.name))
                elif args[0] in ALL_ARITHMETIC_LOGICAL_OPS: # arithmetic/logical operation instruction
                    self.asm_instructions.append(arithmetic_logical_instruction(args[0], self.num_of_jumps))
                    if args[0] in ["lt", "eq", "gt"]: # in case we do a comparison op
                        self.num_of_jumps += 1
            except Exception as e:
                print(f"failed on line {i+1}: {e}")
                sys.exit(1)
        
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: VMTranslator <file.vm>||<directory>")
        sys.exit(1)
    input_path = os.path.abspath(sys.argv[1])
    writer = None
    if os.path.isdir(input_path):
        name = os.path.basename(input_path)
        translators = []
        print(f"Starting VM translation of project: {name}")
        for filename in os.listdir(input_path):
            if not filename.endswith(".vm"):
                continue
            print(f"Translating {filename}")
            translator = Translator(os.path.join(input_path, filename))
            translator.translate()
            translators.append(translator)
        if not len(translators):
            print("no .vm files in directory")
            writer = Translator("Write.vm")
        else:
            writer = translators[0]
            for t in translators[1:]:
                writer.asm_instructions.extend(t.asm_instructions)
        writer.output_file = f"{input_path}/{name}.asm"
    elif os.path.isfile(input_path):
        writer = Translator(input_path)
        print(f"Starting VM translation of {writer.name}.vm...")
        writer.translate()
    else:
        print("ERROR: invalid path")
        sys.exit(1)
    if writer is None:
        print("ERROR")
        sys.exit(1)

    writer.asm_instructions.insert(0, bootstrap()) # add the bootstrap code to the start
    writer.clean_instructions() # remove comments and whitespace
    writer.write_output()
    print(f"VM translation complete. Output written to {writer.output_file}")
