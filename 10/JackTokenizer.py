from Token import Token

class Tokenizer:
    def __init__(self, input):
        self.infile = open(input, "rb")
        self.tokens: list[Token] = []
        self.tokenStrings: list[str] = []
        self.errors = []
        self.line = 1
    
    def tokenize(self):
        while not self.done():
            t = self.nextToken()
            if t is None:
                continue
            self.tokenStrings.append(t.OutputString())
            self.tokens.append(t)
        if len(self.errors):
            print(f"Errors tokenizing:\n{"\n".join(self.errors)}")
            exit(1)
    
    def nextToken(self) -> Token:
        token = ""
        char = self.readChar()
        if char in Token.symbols:
            return Token(char)
        quote = char == "\""
        if quote:
            char = self.readChar()
        while True:
            if quote:
                if char == "\"":
                    break
            else:
                if not len(char) or char in "	 ":
                    break
                if char == "\n":
                    self.line += 1
                    break
                if char in Token.symbols:
                    self.infile.seek(-1, 1)
                    break
            token += char
            char = self.readChar()
        try:
            if quote:
                token = f"\"{token}\""
            return Token(token)
        except Exception as e:
            self.errors.append(f"line {self.line}: {type(e).__name__}: {e.args[0]}")
            return None
    
    # checks if we are at EOF and advance the start of the next token
    def done(self) -> bool:
        while True:
            char = self.readChar()
            if not len(char):
                self.infile.close()
                return True
            if char == "\n":
                self.line += 1
                continue
            if char =="\r":
                continue
            if char in "	 ":
                continue
            if char == "/": # remove comments
                next = self.readChar()
                if next == "/": # single line
                    while next != "\n":
                        next = self.readChar()
                    self.line += 1
                    continue
                if next == "*": # multi line
                    while True:
                        c = self.readChar()
                        if c == "\n":
                            self.line += 1
                        elif c == "*":
                            if self.readChar() == "/":
                                break
                            self.infile.seek(-1, 1)
                    continue
                else:
                    self.infile.seek(-1, 1)   
            self.infile.seek(-1, 1) # return the file pointer to the curr char
            return False

    def readChar(self) -> str:
        return self.infile.read(1).decode("utf-8")
            
                
