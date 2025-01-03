from Token import Token, BRA_TOKEN, KET_TOKEN, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN, \
                  LEXICAL_TYPE_STRING_CONSTANT, LEXICAL_TYPE_IDENTIFIER, \
                  LEXICAL_TYPE_INTEGER_CONSTANT

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
        self.termType = ""
        if len(tokens) == 1:
            self.tokens = tokens
            if tokens[0].type == LEXICAL_TYPE_IDENTIFIER:
                self.termType = TERM_TYPE_VAR
            elif tokens[0].type == LEXICAL_TYPE_STRING_CONSTANT:
                self.termType = TERM_TYPE_STRING
            elif tokens[0].token in ["true", "false", "null", "this"]:
                self.termType = TERM_TYPE_KEYWORD
            elif tokens[0].type == LEXICAL_TYPE_INTEGER_CONSTANT:
                self.termType = TERM_TYPE_INT
        elif tokens[0].token in UNARY_OPS:
            self.tokens = [tokens[0], Term(tokens[1:])]
            self.termType = TERM_TYPE_UNARY_OP
        elif tokens[0] == BRA_TOKEN: # (expression)
            self.tokens.append(BRA_TOKEN)
            self.tokens.append(Expression(tokens[1:-1]))
            self.tokens.append(KET_TOKEN)
            self.termType = TERM_TYPE_EXP
        elif tokens[1] == SQUARE_BRA_TOKEN: # varName[expression]
            self.tokens.append(tokens[0])
            self.tokens.append(SQUARE_BRA_TOKEN)
            self.tokens.append(Expression(tokens[2:-1]))
            self.tokens.append(SQUARE_KET_TOKEN)
            self.termType = TERM_TYPE_VAR_W_EXP
        elif tokens[-1] == KET_TOKEN: # subroutineCall
            self.tokens = parseSubroutineCall(tokens)
            self.termType = TERM_TYPE_CALL
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