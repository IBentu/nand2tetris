from JackTokenizer import Tokenizer
from TokenParser import TokenParser
from SymbolTable import SymbolTable
import os


def test_by_eye():
    tokenizer = Tokenizer(os.getcwd()+"/nand2tetris/11/Square/SquareGame.jack")
    tokenizer.tokenize()
    parser = TokenParser(tokenizer.tokens)
    symbol_table = SymbolTable(parser.token_tree)
    symbol_table.generate()
    print(symbol_table)
    # assert False
