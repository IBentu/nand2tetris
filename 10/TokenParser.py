from Token import Token, LEXICAL_TYPES_W_ARROW, LEXICAL_TYPE_IDENTIFIER, BRA_TOKEN, KET_TOKEN, CURLY_BRA_TOKEN, CURLY_KET_TOKEN, SQUARE_BRA_TOKEN, SQUARE_KET_TOKEN, SEMICOLON_TOKEN
from Class import ClassVarDec, SubroutineDec, ParameterList, SubroutineBody

KET2BRA = {
    KET_TOKEN.token:          BRA_TOKEN,
    SQUARE_KET_TOKEN.token:   SQUARE_BRA_TOKEN,
    CURLY_KET_TOKEN.token:    CURLY_BRA_TOKEN
}

BRA2KET = {
    BRA_TOKEN.token:          KET_TOKEN,
    SQUARE_BRA_TOKEN.token:   SQUARE_KET_TOKEN,
    CURLY_BRA_TOKEN.token:    CURLY_KET_TOKEN
}

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
        strings: str = [t.OutputString() for t in self.token_tree]
        strings = ("\n".join(strings)).split("\n")
        whitespace = 1
        for i, s in enumerate(strings):
            if s.startswith("</"):
                whitespace -= 1
                strings[i] = f"{"  "*whitespace}{s}"
                continue
            lexical_type = False
            for t in LEXICAL_TYPES_W_ARROW:
                if s.startswith(t):
                    lexical_type = True
                    break
            strings[i] = f"{"  "*whitespace}{s}"
            if not lexical_type:
                whitespace += 1
        return f"<class>\n{"\n".join(strings)}\n</class>"
    
    
    @staticmethod
    def getTokensBetween(tokens: list[Token], bra: Token, ket: Token, start_from : int = 0) -> list[Token]:
        # returns all tokens between bra and ket (including the bra and the ket)
        if tokens[start_from] != bra:
            raise IndexError(f"current token isn't the provided bra: provided={bra}, current={tokens[index]}")
        brakets_stack = []
        index = start_from+1
        if ket.token in KET2BRA.keys() and KET2BRA[ket.token] != bra:
            bra = KET2BRA[ket.token]
            final_ket = False
            while not final_ket:
                curr = tokens[index]
                if curr == bra:
                    brakets_stack.append(curr)
                elif curr == ket:
                    brakets_stack.pop()
                    final_ket = len(brakets_stack) == 0
                index += 1
        else:
            brakets_stack.append(bra)
            while len(brakets_stack):
                curr = tokens[index]
                if curr == bra:
                    brakets_stack.append(curr)
                elif curr == ket:
                    brakets_stack.pop()
                index += 1
        return tokens[start_from:index]