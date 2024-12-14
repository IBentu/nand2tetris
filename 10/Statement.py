from Token import Token
from TokenParser import TokenParser

LET_TOKEN = Token("let")
IF_TOKEN = Token("if")
ELSE_TOKEN = Token("else")
WHILE_TOKEN = Token("while")
DO_TOKEN = Token("do")
RETURN_TOKEN = Token("return")
SEMICOLON_TOKEN = Token(";")
KET_TOKEN = Token("}")

class Statement:
    def __init__(self):
        pass
    
class Statements:
    def __init__(self, tokens: list[Token]):
        self.statements: list[Statement] = []
        index = 0
        while index < len(tokens):
            curr = tokens[index]
            if curr == LET_TOKEN:
                let_tokens = TokenParser.getTokensBetween(tokens, LET_TOKEN, SEMICOLON_TOKEN, index)
                index += len(let_tokens)
                self.statements.append(LetStatement(let_tokens))
            elif curr == IF_TOKEN:
                if_tokens = TokenParser.getTokensBetween(tokens, IF_TOKEN, KET_TOKEN, index) #TODO...
                index += len(if_tokens)
                else_tokens_lists = []
                curr = tokens[index]
                while curr == ELSE_TOKEN:
                    else_tokens = TokenParser.getTokensBetween(tokens, curr, KET_TOKEN, index)
                    index += len(else_tokens)
                    else_tokens_lists.append(else_tokens)
                self.statements.append(IfStatement(if_tokens, else_tokens))
            elif curr == WHILE_TOKEN:
                while_tokens = TokenParser.getTokensBetween(tokens, WHILE_TOKEN, KET_TOKEN, index)
                index += len(while_tokens)
                self.statements.append(WhileStatement(while_tokens))
            elif curr == DO_TOKEN:
                do_tokens = TokenParser.getTokensBetween(tokens, DO_TOKEN,  SEMICOLON_TOKEN, index)
                index += len(do_tokens)
                self.statements.append(DoStatement(do_tokens))
            elif curr == RETURN_TOKEN:
                return_tokens = TokenParser.getTokensBetween(tokens, RETURN_TOKEN, KET_TOKEN, index)
                index += len(return_tokens)
                self.statements.append(ReturnStatement(return_tokens))
    
    def OutputString(self) -> str:
        if len(self.statements):
            return f"<statements>\n  {"\n  ".join([s.OutputString() for s in self.statements])}\n</statements>"
        return "<statements>\n</statements>"

class LetStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__()
        # TODO: implement
    
    def OutputString(self) -> str:
        pass

class IfStatement(Statement):
    def __init__(self, if_tokens: list[Token], else_tokens: list[list[Token]] = []):
        super().__init__()
        # TODO: implement
    
    def OutputString(self) -> str:
        pass

class WhileStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__()
        # TODO: implement

    def OutputString(self) -> str:
        pass

class DoStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__()
        # TODO: implement

    def OutputString(self) -> str:
        pass

class ReturnStatement(Statement):
    def __init__(self, tokens: list[Token]):
        super().__init__()
        # TODO: implement

    def OutputString(self) -> str:
        pass