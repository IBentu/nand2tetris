from Token import Token

class Symbol:
    def __init__(self, name, type, kind, index):
        self.name = name
        self.type = type
        self.kind = kind
        self.index = index

class SymbolTable:
    
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.class_scope: list[Symbol] = []
        self.subroutine_scope: dict[str, list[Symbol]] = {}
    
    def generate(self):
        pass