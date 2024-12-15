from Token import Token, LEXICAL_TYPE_SYMBOL, COMMA_TOKEN
from Term import Term

class Expression:
    def __init__(self, tokens: list[Token]):
        self.parsed_tokens = []
        term_tokens = []
        for t in tokens:
            if t.type != LEXICAL_TYPE_SYMBOL:
                term_tokens.append(t)
            else:
                self.parsed_tokens.append(Term(term_tokens))
                term_tokens = []
                self.parsed_tokens.append(t)
        self.parsed_tokens.append(Term(term_tokens))

    def OutputString(self) -> str:
        return f"<expression>\n  {"\n  ".join([t.OutputString() for t in self.parsed_tokens])}\n</expression>"

class ExpressionList:
    def __init__(self, tokens: list[Token]): 
        self.expressions = []
        if not len(tokens):
            return
        index = 0
        expression_tokens = []
        while index < len(tokens):
            curr = tokens[index]
            if curr == COMMA_TOKEN:
                self.expressions.append(Expression(expression_tokens))
                expression_tokens = []
            else:
                expression_tokens.append(curr)
        self.expressions.append(Expression(expression_tokens))
    
    def OutputString(self) -> str:
        if not len(self.expressions):
            return "<expressionList>\n</expressionList>"
        return f"<expressionList>\n  {"\n  ".join([e.OutputString() for e in self.expressions])}\n</expressionList>"
