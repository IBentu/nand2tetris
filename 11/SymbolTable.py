from Class import ClassVarDec, SubroutineDec, VarDec, ParameterList
from Token import COMMA_TOKEN

CLASS_KIND = "class"
STATIC_KIND = "static"
FIELD_KIND = "this"

SUBROUTINE_KIND = "subroutine"
ARG_KIND = "argument"
VAR_KIND = "local"


class Symbol:
    def __init__(self, name: str, symbol_type: str, kind: str, index: int):
        self.name = name
        self.symbol_type = symbol_type
        self.kind = kind
        self.index = index
    
    def __repr__(self):
        return f"[name: {self.name}, type: {self.symbol_type}, kind: {self.kind}, index: {self.index}]"
    
    def __str__(self):
        return self.__repr__()

class SymbolTable:
    def __init__(self, tokens: list):
        self.tokens = tokens
        class_scope: list[Symbol] = []
        subroutine_scope: dict[str, list[Symbol]] = {}
        self.scopes = [class_scope, subroutine_scope]
        self.curr_subroutine = ""
    
    def __repr__(self):
        nl = "\n"
        class_scope = nl.join(map(str, self.scopes[0]))
        subroutine_scopes = ""
        for subroutine_name, scope in self.scopes[1].items():
            subroutine_scope = nl.join(map(str, scope))
            subroutine_scopes += f"{subroutine_name}:{nl}{subroutine_scope}{nl}" 
        return f"class scope:{nl}{class_scope}{nl}subroutine scopes:{nl}{subroutine_scopes}"
    
    def new_symbols(self, token) -> list[Symbol]:
        """
        returns a new symbol based on the variable type and scope
        """
        ret = []
        if type(token) is ClassVarDec:
            tokens = list(token.tokens)
            if tokens[0].token == "field":
                kind = FIELD_KIND
            elif tokens[0].token == "static":
                kind = STATIC_KIND
            else:
                raise TypeError(f"invalid class variable kind: {tokens[0].token}")
            symbol_type = tokens[1].token
            comma = True
            for token in tokens[2:-1]:
                comma = not comma
                if comma:
                    continue
                ret.append(Symbol(token.token, symbol_type, kind, self.count_kind(kind)+len(ret)))
        elif type(token) is SubroutineDec:
            tokens = token.header_tokens
            ret.append(Symbol(tokens[2].token, tokens[1].token, SUBROUTINE_KIND, self.count_kind(SUBROUTINE_KIND))) # currently symbol type is subroutine return type, maybe will change
        elif type(token) is ParameterList:
            tokens = token.tokens
            if len(tokens):
                isType = True
                for t in tokens:
                    if isType:
                        symbol_type = t.token
                        isType = False
                    elif t == COMMA_TOKEN:
                        isType = True
                    else:
                        ret.append(Symbol(t.token, symbol_type, ARG_KIND, len(ret)+1)) # the first arg (index 0) is always "this"
        elif type(token) is VarDec:
            tokens = list(token.tokens)
            kind = VAR_KIND
            symbol_type = tokens[1].token
            comma = True
            for token in tokens[2:-1]:
                comma = not comma
                if comma:
                    continue
                ret.append(Symbol(token.token, symbol_type, kind, self.count_kind(kind)+len(ret)))
        else:
            raise TypeError("invalid declation kind")
        return ret
        
    def count_kind(self, kind: str) -> int:
        """
        returns the number of defined variables in the current scope with the given kind
        """
        if self.curr_subroutine: # subroutine scope
            scope_symbols = self.scopes[1][self.curr_subroutine]
        else: # class scope
            scope_symbols = self.scopes[0]
        scope_symbols = list[Symbol](scope_symbols)
        total = 0
        for symbol in scope_symbols:
            if symbol.kind == kind:
                total += 1
        return total
    
    def generate(self):
        """
        generates the symbol table for the all scopes
        """
        self.scopes[0].append(Symbol(self.tokens[1].token, "className", CLASS_KIND, 0))
        for token in self.tokens[3:-1]:
            if type(token) is ClassVarDec:
                self.scopes[0].extend(self.new_symbols(token))
            else:
                self.generate_subroutine_table(token)
        
    def generate_subroutine_table(self, subroutine: SubroutineDec):
        subroutine_symbol = self.new_symbols(subroutine)[0]
        self.scopes[0].append(subroutine_symbol)
        self.curr_subroutine = subroutine_symbol.name
        self.scopes[1][self.curr_subroutine] = [Symbol("this", self.scopes[0][0].name, ARG_KIND, 0)] + self.new_symbols(subroutine.params)
        for var in subroutine.body.varDecs:
            self.scopes[1][self.curr_subroutine].extend(self.new_symbols(var))
        self.curr_subroutine = ""