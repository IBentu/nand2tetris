from Token import Token, BRA_TOKEN, KET_TOKEN, SEMICOLON_TOKEN, VAR_TOKEN, CURLY_BRA_TOKEN, CURLY_KET_TOKEN, LEXICAL_TYPE_IDENTIFIER
from Expression import ExpressionList
from Statement import Statements

def CompileClass(tokens: list[Token]) -> list:
    from TokenParser import TokenParser as parser
    token_tree = []
    if tokens[0].token != "class":
        raise NameError("every class needs to start with 'class'")
    token_tree.append(tokens[0])
    if tokens[1].type != LEXICAL_TYPE_IDENTIFIER:
        raise NameError("class needs a name")
    token_tree.append(tokens[1])
    token_tree.append(tokens[2]) # append '{'
    token_index = 3
    varDecs = ClassVarDec.isVarDec(tokens[3])
    while token_index < len(tokens)-1:
        curr = tokens[token_index]
        if varDecs:
            dec_tokens = parser.getTokensBetween(tokens, curr, SEMICOLON_TOKEN, token_index)
            token_index += len(dec_tokens)
            token_tree.append(ClassVarDec(dec_tokens))
            varDecs = ClassVarDec.isVarDec(tokens[token_index])
        else:
            subroutine_headers = parser.getTokensBetween(tokens, curr ,BRA_TOKEN, token_index)[:-1]
            token_index += len(subroutine_headers)
            params_tokens = parser.getTokensBetween(tokens, BRA_TOKEN, KET_TOKEN, token_index)
            token_index += len(params_tokens)
            subroutine_params = ParameterList(params_tokens[1:-1])
            body_tokens = parser.getTokensBetween(tokens, CURLY_BRA_TOKEN, CURLY_KET_TOKEN, token_index)
            token_index += len(body_tokens)
            subroutine_body = SubroutineBody(body_tokens)
            token_tree.append(SubroutineDec(subroutine_headers, subroutine_params, subroutine_body))
    token_tree.append(tokens[-1]) # append '}'
    return token_tree
    

class ClassVarDec:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
    
    def OutputString(self) -> str:
        nl = '\n'
        return f"<classVarDec>{nl}{nl.join([t.OutputString() for t in self.tokens])}{nl}</classVarDec>"
    
    @staticmethod
    def isVarDec(token: Token) -> bool:
        return token.token in ["static", "field"]
    
    def __repr__(self):
        return f"classVarDec{self.tokens}"
    
    def __eq__(self, other):
        try:
            return self.tokens == other.tokens
        except:
            return False

class ParameterList:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens    
    def OutputString(self) -> str:
        if len(self.tokens):
            nl = '\n'
            return f"<parameterList>{nl}{nl.join([t.OutputString() for t in self.tokens])}{nl}</parameterList>"
        return "<parameterList>\n</parameterList>"
    
    def __repr__(self):
        return f"parameterList{self.tokens}"

    def __eq__(self, other):
        try:
            return self.tokens == other.tokens
        except:
            return False
    
class SubroutineBody:
    def __init__(self, tokens: list[Token]):
        from TokenParser import TokenParser
        index = 1 # tokens start with '{'
        self.varDecs: list[VarDec] = []
        while VarDec.isVarDec(tokens[index]):
            var_tokens = TokenParser.getTokensBetween(tokens, VAR_TOKEN, SEMICOLON_TOKEN, index)
            index += len(var_tokens)
            self.varDecs.append(VarDec(var_tokens))
        self.statements = Statements(tokens[index:-1]) # tokens ends with '}'

    def OutputString(self) -> str:
        nl = '\n'
        if len(self.varDecs):
            return f"<subroutineBody>{nl}{CURLY_BRA_TOKEN.OutputString()}{nl}{nl.join([v.OutputString() for v in self.varDecs])}{nl}{self.statements.OutputString()}{nl}{CURLY_KET_TOKEN.OutputString()}{nl}</subroutineBody>"
        return f"<subroutineBody>{nl}{CURLY_BRA_TOKEN.OutputString()}{nl}{self.statements.OutputString()}{nl}{CURLY_KET_TOKEN.OutputString()}{nl}</subroutineBody>"
    
    def __repr__(self):
        return f"subroutineBody[vars:{self.varDecs},statements:{self.statements}]"
    
    def __eq__(self, other):
        try:
            return self.varDecs == other.VarDecs and self.statements == other.statements
        except:
            return False

class SubroutineDec:
    def __init__(self, header_tokens: list[Token], parameters: ParameterList, body: SubroutineBody):
        self.header_tokens = header_tokens
        self.params = parameters
        self.body = body
        
    def getName(self) -> str:
        return self.header_tokens[2].token

    def OutputString(self) -> str:
        nl = '\n'
        return f"<subroutineDec>{nl}{nl.join([t.OutputString() for t in self.header_tokens])}{nl}{BRA_TOKEN.OutputString()}{nl}{self.params.OutputString()}{nl}{KET_TOKEN.OutputString()}{nl}{self.body.OutputString()}{nl}</subroutineDec>"
    
    def __repr__(self):
        return f"subroutineDec[headers:{self.header_tokens},params:{self.params},body:{self.body}]"

    def __eq__(self, other):
        try:
            return self.header_tokens == other.header_tokens and self.params == other.params and self.body == other.body
        except:
            return False

class VarDec:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens

    def OutputString(self) -> str:
        nl = '\n'
        return f"<varDec>{nl}{nl.join([t.OutputString() for t in self.tokens])}{nl}</varDec>"
    
    @staticmethod
    def isVarDec(token: Token) -> bool:
        return token.token == "var"
    
    def __repr__(self):
        return f"verDec{self.tokens}"
    
    def __eq__(self, other):
        try:
            return self.tokens == other.tokens
        except:
            return False


def parseSubroutineCall(tokens: list[Token]) -> list[Token]:
    from TokenParser import TokenParser
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