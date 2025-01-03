import sys, os
from JackTokenizer import Tokenizer
from TokenParser import TokenParser
from SymbolTable import SymbolTable
from Compiler import Compiler

class JackCompiler:
    """
    compilation orchastrator
    """
    def __init__(self, input_file: str):
        self.input_file = input_file
        if input_file.endswith("/") or input_file.endswith("\\"):
            input_file = input_file[:-1]
        path = os.path.basename(input_file).rsplit('.', 1)
        if path[1] != "jack":
            print("ERROR: file type should be .jack")
            sys.exit(1)
        elif not path[0][0].isupper():
            print(f"ERROR: file should start with a capital letter: {path[0]}.jack")
            sys.exit(1)
        self.name = path[0]
        self.output_file = input_file.replace('.jack', '.vm')
        self.tokenizer = None
        self.parser = None
        self.symbol_table = None
        self.compiler = None

    def write_output(self):
        """Writes the binary instructions to the output file."""
        output_str = self.compiler.OutputString()
        with open(self.output_file, 'w') as file:
            file.write(output_str)

    def compile(self):
        """Coordinates the jack compilation process."""
        self.tokenizer = Tokenizer(self.input_file)
        self.tokenizer.tokenize()
        self.parser = TokenParser(self.tokenizer.tokens)
        self.symbol_table = SymbolTable(self.parser.token_tree)
        self.symbol_table.generate()
        self.compiler = Compiler(self.symbol_table)
        


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer <file.jack>|<directory>")
        sys.exit(1)
    input_path = os.path.abspath(sys.argv[1])
    writer = None
    if os.path.isdir(input_path):
        name = os.path.basename(input_path)
        compilers: list[JackCompiler] = []
        print(f"Starting compilation of project: {name}")
        for filename in os.listdir(input_path):
            if not filename.endswith(".jack"):
                continue
            print(f"Compiling {filename}")
            compiler = JackCompiler(os.path.join(input_path, filename))
            compiler.compile()
            compilers.append(compiler)
        if not len(compilers):
            print("no .jack files in directory")
            sys.exit(1)
        for writer in compilers:
            writer.write_output()
        print(f"Compilation complete. Output files written in {input_path}")

    elif os.path.isfile(input_path):
        writer = JackCompiler(input_path)
        print(f"Starting compilation of {writer.name}.jack...")
        writer.compile()
        writer.write_output()
        print(f"Compilation complete. Output written to {writer.output_file}")
    else:
        print("ERROR: invalid path")
        sys.exit(1)
    if writer is None:
        print("ERROR")
        sys.exit(1)

