from Token import Token
from Term import Term
from typing import Union

TOKEN_CLASS = type(Token(".")).__name__

class Expression:
    def __init__(self, term: Term, opTerms: list[Union[Term, Token]]):
        if len(opTerms) % 2 != 0:
            raise ValueError("expressions should have one less op than the number of terms")
        self.tokens = [term]+opTerms;

    def OutputString(self) -> str:
        op = False
        token_strings = []
        for t in self.tokens:
             if op and type(t).__name__ == TOKEN_CLASS:
                 raise ValueError("invalid type in expression")
             token_strings.append(t.OutputString())
             op = not op
        return f"<expression>\n  {"\n  ".join(token_strings)}\n</expression>"

class ExpressionList:
    def __init__(self, expression: Expression, more: list[Union[Token, Expression]]):
        if expression is None:
            self.expressions = []
            return
        if len(more) % 2 != 0:
            raise ValueError("expressionLists should have one less comma than the number of expressions or empty")
        self.expressions = [expression] + more
    
    def OutputString(self):
        comma = False
        token_strings = []
        if not len(self.expressions):
            return "<expressionList>\n</expressionList>"
        for t in self.expressions:
            if comma and type(t).__name__ == TOKEN_CLASS:
                raise ValueError("invalid type in expressionList")
            token_strings.append(t.OutputString())
        return f"<expressionList>\n  {"\n  ".join(token_strings)}\n</expressionList>"
