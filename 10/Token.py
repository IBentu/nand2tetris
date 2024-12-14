

LEXICAL_TYPE_KEYWORD = "keyword"
LEXICAL_TYPE_SYMBOL = "symbol"
LEXICAL_TYPE_INTEGER_CONSTANT = "integerConstant"
LEXICAL_TYPE_STRING_CONSTANT = "stringConstant"
LEXICAL_TYPE_IDENTIFIER = "identifier"

class InvalidTokenException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class InvalidIntegerException(Exception):
    def __init__(self, *args):
        super().__init__(*args)
class InvalidStringException(Exception):
    def __init__(self, *args):
        super().__init__(*args)

        
class Token:
    keywords = ["class", "constructor", "function", "method", 
                "field", "static", "var", "int", "char", 
                "boolean", "void", "true", "false", "null",
                "this", "let", "do", "if", "else", "while", 
                "return"]
    
    symbols = ["{", "}", "(", ")", "[", "]", ".", ",", ";", 
               "+", "-", "*", "/", "&", '|', "<", ">", "=", 
               "~", "^", "#"]
    
    def __init__(self, token):
        self.type, self.token = Token.classify(token)
    
    def classify(token: str) -> tuple[str, any]:
        # returns the token type + the raw token (as an int/ no )
        if token in Token.keywords:
            return LEXICAL_TYPE_KEYWORD, token
        if token in Token.symbols:
            return LEXICAL_TYPE_SYMBOL, Token.convert_symbol(token)
        try:
            token_int = int(token)
            if 0 <= token_int <= 32767:
                return LEXICAL_TYPE_INTEGER_CONSTANT, token_int
            raise InvalidIntegerException("integer out of allowed range [-32767, 32767]")
        except Exception as _:
            pass
        if token.startswith("\"") and token.endswith("\""):
            token = token[1:-1]
            if not("\n" in token or "\"" in token):
                return LEXICAL_TYPE_STRING_CONSTANT, token
            raise InvalidStringException("newline or \" in string literal")
        if token[0].isdigit():
            raise InvalidStringException("identifier starts with a digit")
        for c in token:
            if not (c.isalnum() or c == "_"):
                raise InvalidStringException(f"identifier contains invalid char: '{repr(c)}'")
        return LEXICAL_TYPE_IDENTIFIER, token
    
            
    def OutputString(self) -> str:
        return f"<{self.type}> {self.token} </{self.type}>"
    
    def __repr__(self):
        return self.OutputString()
    
    # converts symbols: ">" = "&gt", "<" = "&lt", "&" = "&amp"
    def convert_symbol(symbol: str) -> str:
        if symbol == ">":
            return "&gt;"
        if symbol == "<":
            return "&lt;"
        if symbol == "&":
            return "&amp;"
        return symbol

    def __eq__(self, other):
        return self.type == other.type and self.token == other.token
        
        
        
    
    