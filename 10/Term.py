from Token import Token, LEXICAL_TYPE_SYMBOL, BRA_TOKEN, KET_TOKEN, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN

class Term:
    def __init__(self, tokens: list[Token]):
        from Class import parseSubroutineCall
        from Expression import Expression
        self.tokens = []
        if len(tokens) == 1 or tokens[0].type == LEXICAL_TYPE_SYMBOL:
            self.tokens = tokens
        elif tokens[0] == BRA_TOKEN: # (expression)
            self.tokens.append(BRA_TOKEN)
            self.tokens.append(Expression(tokens[1:-1]))
            self.tokens.append(KET_TOKEN)
        elif tokens[1] == SQUARE_BRA_TOKEN: # varName[expression]
            self.tokens.append(tokens[0])
            self.tokens.append(SQUARE_BRA_TOKEN)
            self.tokens.append(Expression(tokens[1:-1]))
            self.tokens.append(SQUARE_KET_TOKEN)
        elif tokens[-1] == KET_TOKEN: # subroutineCall
            self.tokens = parseSubroutineCall(tokens)
        
    def OutputString(self) -> str:
        return f"<term>\n  {"\n  ".join([t.OutputString() for t in self.tokens])}\n</term>"

    def __repr__(self):
        return self.OutputString()