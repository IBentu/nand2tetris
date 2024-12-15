from Token import Token, BRA_TOKEN, KET_TOKEN, SEMICOLON_TOKEN, VAR_TOKEN
from Expression import ExpressionList
from Statement import Statements
from TokenParser import TokenParser

class ClassVarDec:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
    
    def OutputString(self) -> str:
        return f"<classVarDec>\n  {"\n  ".join([t.OutputString() for t in self.tokens])}\n</classVarDec>"
    
    @staticmethod
    def isVarDec(token: Token) -> bool:
        return token.token in ["static", "field"]

class ParameterList:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens    
    def OutputString(self) -> str:
        if len(self.tokens):
            return f"<parameterList>\n  {"\n  ".join([s.OutputString() for s in self.statements])}\n</parameterList>"
        return "<parameterList>\n</parameterList>"

class SubroutineBody:
    def __init__(self, tokens: list[Token]):
        index = 1 # tokens start with '{'
        self.varDecs: list[VarDec] = []
        while VarDec.isVarDec(tokens[index]):
            var_tokens = TokenParser.getTokensBetween(tokens, VAR_TOKEN, SEMICOLON_TOKEN, index)
            index += len(var_tokens)
            self.varDecs.append(VarDec(var_tokens))

        self.statements = Statements(tokens[index:-1]) # tokens ends with '}'

    def OutputString(self) -> str:
        if len(self.varDecs):
            return f"<subroutineBody>\n{"  \n".join([v.OutputString() for v in self.varDecs])}\n  {self.statements.OutputString}\n</subroutineBody>"
        return f"<subroutineBody>\n  {self.statements.OutputString}\n</subroutineBody>"

class SubroutineDec:
    def __init__(self, header_tokens: list[Token], parameters: ParameterList, body: SubroutineBody):
        self.header_tokens = header_tokens
        self.params = parameters
        self.body = body
        
    def OutputString(self) -> str:
        return f"<subroutineDec>\n  {"\n  ".join([t.OutputString() for t in self.header_tokens])}  \n{Token("(").OutputString()}  \n{self.params.OutputString()}  \n{Token(")").OutputString()}  \n{self.body.OutputString()}\n</subroutineDec>"


class VarDec:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def OutputString(self) -> str:
        return f"<varDec>\n{"\n  ".join([t.Outputstring() for t in self.tokens])}\n</varDec>"
    
    @staticmethod
    def isVarDec(token: Token) -> bool:
        return token.token == "var"


def parseSubroutineCall(tokens: list[Token]) -> list[Token]:
    ret = []
    index = 0
    while tokens[index] != BRA_TOKEN:
        ret.append(tokens[index])
        index += 1
    expressions_tokens = TokenParser.getTokensBetween(tokens, BRA_TOKEN, KET_TOKEN, index)
    ret.append(BRA_TOKEN)
    ret.append(ExpressionList(expressions_tokens[1:-1]))
    ret.append(KET_TOKEN)
    return ret