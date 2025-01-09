from JackTokenizer import Tokenizer
from TokenParser import TokenParser
from SymbolTable import SymbolTable
from Compiler import Compiler
import os

def test_for_debug():
    tokenizer = Tokenizer(os.getcwd()+"/nand2tetris/11/Pong/PongGame.jack")
    tokenizer.tokenize()
    parser = TokenParser(tokenizer.tokens)
    symbol_table = SymbolTable(parser.token_tree)
    symbol_table.generate()
    Compiler(symbol_table)
    