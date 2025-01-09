from Token import Token, BRA_TOKEN, KET_TOKEN, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN

UNARY_OPS = ["-", "~", "#", "^"]

TERM_TYPE_INT = "integerConstant"
TERM_TYPE_STRING = "stringConstant"
TERM_TYPE_KEYWORD = "keywordConstant"
TERM_TYPE_VAR = "varName"
TERM_TYPE_VAR_W_EXP = "varName[expression]"
TERM_TYPE_CALL = "subroutineCall"
TERM_TYPE_EXP = "(expression)"
TERM_TYPE_UNARY_OP = "unaryOp term"


class Term:
    def __init__(self, tokens: list[Token]):
        from Class import parseSubroutineCall
        from Expression import Expression
        self.tokens = []
        if len(tokens) == 1:
            self.tokens = tokens
        elif tokens[0].token in UNARY_OPS:
            self.tokens = [tokens[0], Term(tokens[1:])]
        elif tokens[0] == BRA_TOKEN: # (expression)
            self.tokens.append(BRA_TOKEN)
            self.tokens.append(Expression(tokens[1:-1]))
            self.tokens.append(KET_TOKEN)
        elif tokens[1] == SQUARE_BRA_TOKEN: # varName[expression]
            self.tokens.append(tokens[0])
            self.tokens.append(SQUARE_BRA_TOKEN)
            self.tokens.append(Expression(tokens[2:-1]))
            self.tokens.append(SQUARE_KET_TOKEN)
        elif tokens[-1] == KET_TOKEN: # subroutineCall
            self.tokens = parseSubroutineCall(tokens)
        else:
            raise Exception("invalid term tokens", tokens)
        
    def OutputString(self) -> str:
        nl = "\n"
        return f"<term>{nl}{nl.join([t.OutputString() for t in self.tokens])}{nl}</term>"

    def __repr__(self):
        return f"term{self.tokens}"

    def __eq__(self, other):
        try:
            return self.tokens == other.tokens
        except:
            return False