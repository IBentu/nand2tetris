from Token import Token, LET_TOKEN, IF_TOKEN, ELSE_TOKEN, WHILE_TOKEN,\
                  DO_TOKEN, RETURN_TOKEN, SEMICOLON_TOKEN, BRA_TOKEN, \
                  KET_TOKEN, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN,\
                  CURLY_BRA_TOKEN, CURLY_KET_TOKEN, EQ_TOKEN
from Expression import Expression

class Statement:
    def __init__(self, name, tokens):
        self.tokens = tokens
        self.name = name
    
    def token_parser(self, tokens: list[Token], bra: Token, ket: Token, start_from : int = 0) -> list[Token]:
        from TokenParser import TokenParser
        return TokenParser.getTokensBetween(tokens, bra, ket, start_from)
    
    def OutputString(self) -> str:
        return f"<{self.name}>\n{"\n".join([t.OutputString() for t in self.tokens])}\n</{self.name}>"
    
    def __repr__(self):
        return f"{self.name}{self.tokens}"
    
    def __eq__(self, other):
        try:
            return self.name == other.name and self.tokens == other.tokens
        except:
            return False
    
class Statements:
    def __init__(self, tokens: list[Token]):
        self.statements: list[Statement] = []
        if not len(tokens):
            return
        parser = Statement("", None)
        index = 0
        while index < len(tokens):
            curr = tokens[index]
            if curr == LET_TOKEN:
                let_tokens = parser.token_parser(tokens, LET_TOKEN, SEMICOLON_TOKEN, index)
                index += len(let_tokens)
                self.statements.append(LetStatement(let_tokens))
            elif curr == IF_TOKEN:
                if_tokens = parser.token_parser(tokens, IF_TOKEN, CURLY_KET_TOKEN, index)
                index += len(if_tokens)
                if index >= len(tokens):
                    self.statements.append(IfStatement(if_tokens))
                    continue
                else_tokens_lists = []
                curr = tokens[index]
                while curr == ELSE_TOKEN:
                    else_tokens = parser.token_parser(tokens, curr, CURLY_KET_TOKEN, index)
                    index += len(else_tokens)
                    else_tokens_lists.append(else_tokens)
                    if index >= len(tokens):
                        break
                    curr = tokens[index]
                self.statements.append(IfStatement(if_tokens, else_tokens_lists))
            elif curr == WHILE_TOKEN:
                while_tokens = parser.token_parser(tokens, WHILE_TOKEN, CURLY_KET_TOKEN, index)
                index += len(while_tokens)
                self.statements.append(WhileStatement(while_tokens))
            elif curr == DO_TOKEN:
                do_tokens = parser.token_parser(tokens, DO_TOKEN,  SEMICOLON_TOKEN, index)
                index += len(do_tokens)
                self.statements.append(DoStatement(do_tokens))
            elif curr == RETURN_TOKEN:
                return_tokens = parser.token_parser(tokens, RETURN_TOKEN, SEMICOLON_TOKEN, index)
                index += len(return_tokens)
                self.statements.append(ReturnStatement(return_tokens))
    
    def OutputString(self) -> str:
        if len(self.statements):
            return f"<statements>\n{"\n".join([s.OutputString() for s in self.statements])}\n</statements>"
        return "<statements>\n</statements>"
    
    def __eq__(self, other):
        try:
            return self.statements == other.statements
        except:
            return False
    
    def __repr__(self):
        return f"statements{self.statements}"

class LetStatement(Statement):
    def __init__(self, tokens: list[Token]):
        parsed: list = tokens[:2]
        index = 2
        if tokens[2] == SQUARE_BRA_TOKEN:
            parsed.append(SQUARE_BRA_TOKEN)
            expression_tokens = self.token_parser(tokens, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN, 2)
            index += len(expression_tokens)
            index_expression = Expression(expression_tokens[1:-1])
            parsed.append(index_expression)
            parsed.append(SQUARE_KET_TOKEN)
        parsed.append(EQ_TOKEN)
        expression_tokens = self.token_parser(tokens, EQ_TOKEN, SEMICOLON_TOKEN, index)
        parsed.append(Expression(expression_tokens[1:-1]))
        parsed.append(SEMICOLON_TOKEN)
        super().__init__("letStatement", parsed)
            
class IfStatement(Statement):
    def __init__(self, if_tokens: list[Token], else_tokens_lists: list[list[Token]] = []):
        parsed: list = [IF_TOKEN, BRA_TOKEN]
        expression_tokens = self.token_parser(if_tokens, BRA_TOKEN, KET_TOKEN, 1)
        parsed.append(Expression(expression_tokens[1:-1]))
        parsed.append(KET_TOKEN)
        index = len(expression_tokens) + 1
        parsed.append(CURLY_BRA_TOKEN)
        parsed.append(Statements(if_tokens[index+1:-1]))
        parsed.append(CURLY_KET_TOKEN)
        for else_tokens in else_tokens_lists:
            parsed.append(ELSE_TOKEN)
            parsed.append(CURLY_BRA_TOKEN)
            parsed.append(Statements(else_tokens[2:-1]))
            parsed.append(CURLY_KET_TOKEN)       
        super().__init__("ifStatement", parsed)

class WhileStatement(Statement):
    def __init__(self, tokens: list[Token]):
        parsed = []
        parsed.append(tokens[0])
        expression_tokens = self.token_parser(tokens, BRA_TOKEN, KET_TOKEN, 1)
        parsed.append(BRA_TOKEN)
        parsed.append(Expression(expression_tokens[1:-1]))
        parsed.append(KET_TOKEN)
        statements_tokens =  self.token_parser(tokens, CURLY_BRA_TOKEN, CURLY_KET_TOKEN, len(expression_tokens)+1)
        parsed.append(CURLY_BRA_TOKEN)
        parsed.append(Statements(statements_tokens[1:-1]))
        parsed.append(CURLY_KET_TOKEN)
        super().__init__("whileStatement", parsed)

class DoStatement(Statement):
    def __init__(self, tokens: list[Token]):
        from Class import parseSubroutineCall
        parsed = []
        parsed.append(DO_TOKEN)
        parsed.extend(parseSubroutineCall(tokens[1:-1]))
        parsed.append(SEMICOLON_TOKEN)
        super().__init__("doStatement", parsed)

class ReturnStatement(Statement):
    def __init__(self, tokens: list[Token]):
        if len(tokens) > 2:
            parsed = [RETURN_TOKEN, Expression(tokens[1:-1]), SEMICOLON_TOKEN]
        else:
            parsed = tokens
        super().__init__("returnStatement", parsed)
