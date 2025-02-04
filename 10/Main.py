import sys, os
from JackTokenizer import Tokenizer
from TokenParser import TokenParser

class Analyzer:
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
        self.output_file = input_file.replace('.jack', '.xml')
        self.tokenizer = None
        self.parser = None        

    def write_output(self):
        """Writes the binary instructions to the output file."""
        output_str = self.parser.OutputString()
        with open(self.output_file, 'w') as file:
            file.write(output_str)
    def write_output_tokens(self):
        """Writes the binary instructions to the output file."""
        with open(self.output_file.replace(".xml", "_tokens.xml"), 'w') as file:
            nl = '\n'
            file.write(f"<tokens>{nl}  {(nl+'  ').join(self.tokenizer.tokenStrings)}{nl}</tokens>{nl}")

    def analyze(self):
        """Coordinates the jack Analyzing process."""
        self.tokenizer = Tokenizer(self.input_file)
        self.tokenizer.tokenize()
        self.parser = TokenParser(self.tokenizer.tokens)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: JackAnalyzer <file.jack>|<directory>")
        sys.exit(1)
    input_path = os.path.abspath(sys.argv[1])
    writer = None
    if os.path.isdir(input_path):
        name = os.path.basename(input_path)
        analyzers: list[Analyzer] = []
        print(f"Starting analyzing of project: {name}")
        for filename in os.listdir(input_path):
            if not filename.endswith(".jack"):
                continue
            print(f"Analyzing {filename}")
            analyzer = Analyzer(os.path.join(input_path, filename))
            analyzer.analyze()
            analyzers.append(analyzer)
        if not len(analyzers):
            print("no .jack files in directory")
            sys.exit(1)
        for writer in analyzers:
            writer.write_output()
        print(f"Analyzing complete. Output files written in {input_path}")

    elif os.path.isfile(input_path):
        writer = Analyzer(input_path)
        print(f"Starting anazlyzing of {writer.name}.jack...")
        writer.analyze()
        writer.write_output()
        print(f"Analyzing complete. Output written to {writer.output_file}")
    else:
        print("ERROR: invalid path")
        sys.exit(1)
    if writer is None:
        print("ERROR")
        sys.exit(1)

