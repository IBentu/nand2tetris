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
                                 ALL_ARITHMETIC_LOGICAL_OPS

class Translator:
    def __init__(self, input_file: str):
        self.input_file = input_file
        if input_file.endswith("/") or input_file.endswith("\\"):
            input_file = input_file[:-1]
        path = os.path.basename(input_file).rsplit('.', 1)
        if path[1] != "vm":
            print("ERROR: file type should be .vm")
            sys.exit(1)
        elif not path[0][0].isupper():
            print(f"ERROR: file should start with a capital letter: {path[0]}.vm")
            sys.exit(1)
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
                if clean_line:
                    self.instructions.append(clean_line)

    def clean_line(self, line: str):
        """Removes comments and whitespace from a line."""
        line = line.split('//')[0]  # remove comments
        return line.strip()  # remove whitespace
    
    def clean_instructions(self):
        if not self.asm_instructions:
            raise Exception("no assembly code to clean!")
        cleaned = []
        for line in self.asm_instructions:
            if line.startswith("//") or line=="\n" or line.startswith(" "):
                continue
            cleaned.append(line)
        self.asm_instructions = cleaned

    
    def write_output(self):
        """Writes the binary instructions to the output file."""
        instructions = "\n".join(self.asm_instructions)
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
        """
        # inifinite loop should be implemented in Sys.init
        self.asm_instructions.append("\n".join([
                                                f"({self.name}.END)",
                                                f"@{self.name}.END",
                                                "0;JMP"
                                                ]))
        """
        
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python3 VMTranslator.py <file.vm>")
        sys.exit(1)
    input_path = sys.argv[1]
    if os.path.isdir(input_path):
        if input_path.endswith("/") or input_path.endswith("\\"):
            input_path = input_path[:-1]
        name = os.path.basename(input_path)
        translators = []
        print(f"Starting VM translation of project {name}")
        for filename in os.listdir(input_path):
            if not filename.endswith(".vm"):
                continue
            print(f"Translating {filename}")
            translator = Translator(os.path.join(input_path, filename))
            translator.translate()
            translators.append(translator)
        if not len(translators):
            print("no .vm files in directory")
            sys.exit(1)
        writer = translators[0]
        for t in translators[1:]:
            writer.asm_instructions.extend(t.asm_instructions)
        output = f"{input_path}/{name}.asm"
        writer.output_file = f"{input_path}/{name}.asm"
        writer.asm_instructions.insert(0, bootstrap()) # add the bootstrap code to the start
        writer.clean_instructions() # remove comments and whitespace
        writer.write_output()
        print(f"VM translation complete. Output written to {output}")
    elif os.path.isfile(input_path):
        translator = Translator(input_path)
        print(f"Starting VM translation of {translator.name}.vm...")
        translator.translate()
        translator.asm_instructions.insert(0, bootstrap()) # add the bootstrap code to the start
        translator.clean_instructions() # remove comments and whitespace
        translator.write_output()
        print(f"VM translation complete. Output written to {translator.output_file}")
    else:
        print("ERROR: invalid path")
        sys.exit(1)
