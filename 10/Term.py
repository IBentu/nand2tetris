from Token import Token

class Term:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        
    def OutputString(self) -> str:
        return f"<term>\n  {"\n  ".join([t.OutputString() for t in self.tokens])}\n</term>"

    def __repr__(self):
        return self.OutputString()