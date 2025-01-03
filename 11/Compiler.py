from SymbolTable import SymbolTable

class Compiler:
    def __init__(self, symbols: SymbolTable):
        self.symbols = symbols
        self.vm_code = self.compile()
        
    def compile(self) -> list[str]:
        # TODO: sigh...
        pass
    
    def OutputString(self) -> str:
        return '\n'.join(self.vm_code)