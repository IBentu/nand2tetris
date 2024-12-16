from Token import Token, LEXICAL_TYPE_IDENTIFIER, BRA_TOKEN, KET_TOKEN, CURLY_BRA_TOKEN, CURLY_KET_TOKEN, SEMICOLON_TOKEN
from Class import ClassVarDec, SubroutineDec, ParameterList, SubroutineBody

class TokenParser:
    def __init__(self, tokens: list[Token]):
        if not len(tokens):
            raise ValueError("token list is empty!")
        self.tokens = tokens
        self.token_tree = []
        self.token_index = 0
    
    
    def CompileClass(self):
        if self.tokens[0].token != "class":
            raise NameError("every class needs to start with 'class'")
        self.token_tree.append(self.tokens[0])
        if self.tokens[1].type != LEXICAL_TYPE_IDENTIFIER:
            raise NameError("class needs a name")
        self.token_tree.append(self.tokens[1])
        self.token_tree.append(self.tokens[2]) # append '{'
        self.token_index = 3
        varDecs = ClassVarDec.isVarDec(self.tokens[3])
        while self.token_index < len(self.tokens)-1:
            curr = self.tokens[self.token_index]
            if varDecs:
                dec_tokens = self.getTokensBetween(self.tokens, curr, SEMICOLON_TOKEN, self.token_index)
                self.token_index += len(dec_tokens)
                self.token_tree.append(ClassVarDec(dec_tokens))
                varDecs = ClassVarDec.isVarDec(self.tokens[self.token_index])
            else:
                subroutine_headers = self.getTokensBetween(self.tokens, curr ,BRA_TOKEN, self.token_index)[:-1]
                self.token_index += len(subroutine_headers)
                params_tokens = self.getTokensBetween(self.tokens, BRA_TOKEN, KET_TOKEN, self.token_index)
                self.token_index += len(params_tokens)
                subroutine_params = ParameterList(params_tokens[1:-1])
                body_tokens = self.getTokensBetween(self.tokens, CURLY_BRA_TOKEN, CURLY_KET_TOKEN, self.token_index)
                self.token_index += len(body_tokens)
                subroutine_body = SubroutineBody(body_tokens)

                self.token_tree.append(SubroutineDec(subroutine_headers, subroutine_params, subroutine_body))

        self.token_tree.append(self.tokens[-1]) # append '}'
    
    
    def OutputString(self) -> str:
        return f"<class>\n{"\n".join([t.OutputString() for t in self.token_tree])}\n</class>"
    
    
    @staticmethod
    def getTokensBetween(tokens: list[Token], bra: Token, ket: Token, start_from : int = 0) -> list[Token]:
        # returns all tokens between bra and ket (including the bra and the ket)
        index = start_from
        if tokens[index] != bra:
            raise IndexError(f"current token isn't the provided bra: provided={bra}, current={tokens[index]}")
        index += 1
        brakets_stack = [bra]
        while len(brakets_stack):
            curr = tokens[index]
            if curr == bra:
                brakets_stack.append(curr)
            elif curr == ket:
                brakets_stack.pop()
            index += 1
        return tokens[start_from:index]