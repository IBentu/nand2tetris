LEXICAL_TYPE_KEYWORD = "keyword"
LEXICAL_TYPE_SYMBOL = "symbol"
LEXICAL_TYPE_INTEGER_CONSTANT = "integerConstant"
LEXICAL_TYPE_STRING_CONSTANT = "stringConstant"
LEXICAL_TYPE_IDENTIFIER = "identifier"

LEXICAL_TYPES = [LEXICAL_TYPE_STRING_CONSTANT, LEXICAL_TYPE_IDENTIFIER, LEXICAL_TYPE_INTEGER_CONSTANT, LEXICAL_TYPE_SYMBOL, LEXICAL_TYPE_KEYWORD]
LEXICAL_TYPES_W_ARROW = [f"<{l}>" for l in LEXICAL_TYPES]
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
            if not('\n' in token or "\"" in token):
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
        return f"'{self.token}'"

    
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
        try:
            return self.type == other.type and self.token == other.token
        except:
            return False
     
LET_TOKEN = Token("let")
IF_TOKEN = Token("if")
ELSE_TOKEN = Token("else")
WHILE_TOKEN = Token("while")
DO_TOKEN = Token("do")
RETURN_TOKEN = Token("return")
VAR_TOKEN = Token("var")
COMMA_TOKEN = Token(",")
SEMICOLON_TOKEN = Token(";")
BRA_TOKEN = Token("(")
KET_TOKEN = Token(")")
SQUARE_BRA_TOKEN = Token("[")
SQUARE_KET_TOKEN = Token("]")
CURLY_BRA_TOKEN = Token("{")
CURLY_KET_TOKEN = Token("}")
EQ_TOKEN = Token("=")
    
    