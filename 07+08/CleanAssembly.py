import sys, os

def paths(input) -> tuple[str, str]:
    """Returns the in and out paths"""
    if input.endswith("/") or input.endswith("\\"):
        input = input[:-1]
    path = os.path.basename(input).rsplit('.', 1)
    if path[1] != "asm":
        print("ERROR: file type should be .asm")
        sys.exit(1)
    elif not path[0][0].isupper():
        print(f"ERROR: file should start with a capital letter: {path[0]}.asm")
        sys.exit(1)
    return input, input.replace(".asm", "Cleaned.asm")
    


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 CleanAssembly.py <file.asm>")
        sys.exit(1)
    try:
        infile, outfile = paths(sys.argv[1])
    except Exception as e:
        print(f"could not parse filepath: {e}")
        sys.exit(1)
    try:
        lines = []
        with open(infile) as f:
            for line in f.readlines():
                if line.startswith("//") or line=="\n" or line.startswith(" "):
                    continue
                lines.append(line)
        with open(outfile, "w") as f:
            f.writelines(lines)
    except Exception as e:
        print(f"could not manipulate files: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()