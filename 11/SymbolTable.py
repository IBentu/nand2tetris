from Class import ClassVarDec, SubroutineDec, VarDec, ParameterList
from Token import COMMA_TOKEN, Token

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
        self.class_scope: list[Symbol] = []
        self.subroutine_scopes: dict[str, list[Symbol]] = {}
        self.curr_subroutine = ""
        self.subroutines: list[SubroutineDec] = []
    
    def generate(self):
        """
        generates the symbol table for the all scopes
        """
        self.class_scope.append(Symbol(self.tokens[1].token, "className", CLASS_KIND, 0))
        for token in self.tokens[3:-1]:
            if type(token) is ClassVarDec:
                self.class_scope.extend(self.new_symbols(token))
            else:
                self.generate_subroutine_table(token)
                self.subroutines.append(token)
        
    def generate_subroutine_table(self, subroutine: SubroutineDec):
        subroutine_symbol = self.new_symbols(subroutine)[0]
        self.class_scope.append(subroutine_symbol)
        self.curr_subroutine = subroutine_symbol.name
        self.subroutine_scopes[self.curr_subroutine] = [Symbol("this", self.class_scope[0].name, ARG_KIND, 0)] + self.new_symbols(subroutine.params)
        for var in subroutine.body.varDecs:
            self.subroutine_scopes[self.curr_subroutine].extend(self.new_symbols(var))
        self.curr_subroutine = ""
    
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
            scope_symbols = self.subroutine_scopes[self.curr_subroutine]
        else: # class scope
            scope_symbols = self.class_scope
        scope_symbols = list[Symbol](scope_symbols)
        total = 0
        for symbol in scope_symbols:
            if symbol.kind == kind:
                total += 1
        return total
        
    def getClass(self) -> str:
        if not len(self.class_scope):
            raise RuntimeError("generate the table first")
        return self.class_scope[0].name
    
    def number_of(self, kind: str, subroutine="") -> int:
        """
        returns the number of variable symbols of kind, in the given scope
        """
        if not subroutine and kind not in [FIELD_KIND, STATIC_KIND]:
            raise KeyError(f"mismatch between kind '{kind}' and class scope")
        if subroutine not in self.subroutine_scopes.keys():
            raise KeyError(f"invalid subroutine name: {subroutine}")
        if subroutine and kind not in [ARG_KIND, VAR_KIND]:
            raise KeyError(f"mismatch between kind '{kind}' and subroutine '{subroutine}' scope")
        self.curr_subroutine = subroutine
        num = self.count_kind(kind)
        self.curr_subroutine = ""
        if kind == ARG_KIND:
            num -= 1 # "this" is always an argument
        return num
    
    def get_symbol(self, varName: str, subroutine: str) -> Symbol:
        """
        returns the symboll associated with varName.
        starts by first searching the subroutine scope and if nothing was found searching the class scope
        """
        if subroutine not in self.subroutine_scopes.keys():
            raise KeyError(f"invalid subroutine: {subroutine}")
        for s in self.subroutine_scopes[subroutine]:
            if s.name == varName:
                return s
        for s in self.class_scope:
            if s.name == varName:
                return s
        raise ValueError(f"invalid varName: {varName}")
        
    def __repr__(self):
        nl = "\n"
        class_scope = nl.join(map(str, self.class_scope))
        subroutine_scopes = ""
        for subroutine_name, scope in self.subroutine_scopes.items():
            subroutine_scope = nl.join(map(str, scope))
            subroutine_scopes += f"{subroutine_name}:{nl}{subroutine_scope}{nl}" 
        return f"class scope:{nl}{class_scope}{nl}subroutine scopes:{nl}{subroutine_scopes}"
    