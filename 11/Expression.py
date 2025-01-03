from Token import Token, COMMA_TOKEN, BRA_TOKEN, KET_TOKEN, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN
from Term import Term, UNARY_OPS

OPS = ["+", "-", "*", "/", "&amp;", "|", "&lt;", "&gt;", "="]

class Expression:
    def __init__(self, tokens: list[Token]):
        self.parsed_tokens: list[Token] = []
        term_tokens = []
        bracket_stack = 0
        for t in tokens:
            if t == BRA_TOKEN or t == SQUARE_BRA_TOKEN:
                bracket_stack += 1
                term_tokens.append(t)
            elif t == KET_TOKEN or t == SQUARE_KET_TOKEN:
                bracket_stack -= 1
                term_tokens.append(t)
            elif bracket_stack or (t.token not in OPS or (t.token in UNARY_OPS and not term_tokens)):
                term_tokens.append(t)
            else:
                self.parsed_tokens.append(Term(term_tokens))
                term_tokens = []
                self.parsed_tokens.append(t)
        self.parsed_tokens.append(Term(term_tokens))

    def OutputString(self) -> str:
        nl = '\n'
        return f"<expression>{nl}{nl.join([t.OutputString() for t in self.parsed_tokens])}{nl}</expression>"

    def __eq__(self, other):
        try:
            return self.parsed_tokens == other.parsed_tokens
        except:
            return False
    
    def __repr__(self):
        return f"expression{self.parsed_tokens}"


class ExpressionList:
    def __init__(self, tokens: list[Token]): 
        self.tokens = []
        if not len(tokens):
            return
        expression_tokens = []
        for curr in tokens:
            if curr == COMMA_TOKEN:
                self.tokens.append(Expression(expression_tokens))
                self.tokens.append(curr)
                expression_tokens = []
            else:
                expression_tokens.append(curr)
        self.tokens.append(Expression(expression_tokens))
    
    def OutputString(self) -> str:
        if not len(self.tokens):
            return "<expressionList>\n</expressionList>"
        nl = '\n'
        return f"<expressionList>{nl}{nl.join([e.OutputString() for e in self.tokens])}{nl}</expressionList>"
    
    def __eq__(self, other):
        try:
            return self.tokens == other.tokens
        except:
            return False
    
    def __repr__(self):
        return f"expressionList{self.tokens}"
    
    def number_of_expressions(self) -> int:
        if not len(self.tokens):
            return 0
        return 1 + (len(self.tokens)-1)//2
    
    def getExpressions(self) -> list[Expression]:
        ret = []
        comma = False
        for t in self.tokens:
            if not comma:
                ret.append(t)
            comma = not comma
        return ret
