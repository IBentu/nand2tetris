from TokenParser import TokenParser
from Token import Token as t
from Expression import Expression, ExpressionList
from Statement import LetStatement, IfStatement, ReturnStatement, Statements, DoStatement, WhileStatement
from Term import Term
from Class import SubroutineBody, SubroutineDec, CompileClass, ParameterList

def convert2tokens(string: str) -> list[t]:
    strings = string.split(" ")
    return [t(s) for s in strings]


BRACKETS = convert2tokens("[ ( { [ ( { } ) ] } ) ]")
def test_Parser():
    parse = TokenParser.getTokensBetween
    assert parse(BRACKETS, t("("), t(")"), 1) == BRACKETS[1:-1]
    assert parse(BRACKETS, t("["), t("]"), 3) == BRACKETS[3:-3]
    assert parse([t("a"), *BRACKETS], t("a"), t("}")) == [t("a")] + BRACKETS[:10]
    assert parse(IF, t("if"), t("}")) == IF
    assert parse(ELSE, t("else"), t("}")) == ELSE
    assert parse(IF_ELSE_IN_IF, t("if"), t("}")) == IF_ELSE_IN_IF

FUNC_CALL = [t("Test"), t("."), t("foo"), t("("), t(")")]
EXPRESSION_TERM = [t("("), t("#"), t("x"), t(")")]
EXPRESSION_TERM2 = convert2tokens("( - j )")
VAR_WITH_EXP = [t("a"), t("["), t("i"), t("]")]
def test_Term():
    assert Term([t("1")]).tokens == [t("1")]
    assert Term([t("Hi")]).tokens == [t("Hi")]
    assert Term([t("^"),t("1")]).tokens == [t("^"),Term([t("1")])]
    assert Term([t("false")]).tokens == [t("false")]
    assert Term([t("\"nice\"")]).tokens == [t("\"nice\"")]
    assert Term(VAR_WITH_EXP).tokens == [t("a"), t("["), Expression([t("i")]), t("]")]
    assert Term([t("bar"), t("("), t(")")]).tokens == [t("bar"), t("(") , ExpressionList([]), t(")")]
    assert Term(FUNC_CALL).tokens == [*(FUNC_CALL[:4]), ExpressionList([]), FUNC_CALL[4]]
    assert Term(EXPRESSION_TERM).tokens == [t("("), Expression(EXPRESSION_TERM[1:-1]), t(")")]
    assert Term(EXPRESSION_TERM2).tokens == [t("("), Expression(EXPRESSION_TERM2[1:-1]), t(")")]


MATH_PROB = [t("a"), t("+"), t("b"), t("/"),t("("), t("2"), t("*"), *FUNC_CALL, t(")")]
EXP = convert2tokens("i * ( - j )")
EXP2 = convert2tokens("- ( a - b ) * a [ ( a / - b ) ]")
EXP3 = convert2tokens("size - 2")
def test_Expression():
    assert Expression([t("#"), t("x")]).parsed_tokens == [Term([t("#"), t("x")])]
    assert Expression([t("a")]).parsed_tokens == [Term([t("a")])]
    assert Expression([t("a")]).parsed_tokens == [Term([t("a")])]
    assert Expression([t("a")]).parsed_tokens == [Term([t("a")])]
    assert Expression([*FUNC_CALL, t("+"), *EXPRESSION_TERM]).parsed_tokens == [Term(FUNC_CALL), t("+"), Term(EXPRESSION_TERM)]
    assert Expression(MATH_PROB).parsed_tokens == [Term(MATH_PROB[0:1]), MATH_PROB[1], Term(MATH_PROB[2:3]), MATH_PROB[3], Term(MATH_PROB[4:])]
    assert Expression(EXPRESSION_TERM).parsed_tokens == [Term(EXPRESSION_TERM)]
    assert Expression(EXP).parsed_tokens == [Term([t("i")]), t("*"), Term(EXP[2:])]
    assert Expression(EXP2).parsed_tokens == [Term(EXP2[:6]), EXP2[6], Term(EXP2[7:])]
    assert Expression(EXP3).parsed_tokens == [Term(EXP3[:1]), EXP3[1], Term(EXP3[2:])]
    
def test_ExpressionList():
    assert ExpressionList([]).tokens == []
    assert ExpressionList(EXPRESSION_TERM).tokens == [Expression(EXPRESSION_TERM)]
    assert ExpressionList([*EXPRESSION_TERM, t(","), *MATH_PROB]).tokens == [Expression(EXPRESSION_TERM), t(","), Expression(MATH_PROB)]

LET = [t("let"), t("a"), t("="), t("1"), t(";")]
LET2 = convert2tokens("let i = i * ( - j ) ;")
LET3 = convert2tokens("let size = size + 2 ;")
LET_WITH_EXP = [t("let"), *VAR_WITH_EXP, t("="), t("0"), t(";")]
IF = [t("if"), t("("), *EXPRESSION_TERM, t(")"), t("{"), *LET, t("}")]
ELSE = [t("else"), t("{"), *LET_WITH_EXP, t("}")]
DO = [t("do"), *FUNC_CALL, t(";")]
IF_ELSE_IN_IF = convert2tokens("if ( a ) { if ( b ) { let a = false ; } else { let a = ( ~ x ) ; } }")
IF_ELSE = convert2tokens("if ( false ) { let s = \"string_constant\" ; let s = null ; let a [ 1 ] = a [ 2 ] ; } else { let i = i * ( - j ) ; let j = j / ( - 2 ) ; let i = i | j ; }")
def test_Statements():
    assert Statements([]).statements == []
    assert LetStatement(LET).tokens == [*(LET[:3]), Expression(LET[3:-1]), LET[-1]]
    assert LetStatement(LET2).tokens == [*(LET2[:3]), Expression(LET2[3:-1]), LET2[-1]]
    assert LetStatement(LET3).tokens == [*(LET3[:3]), Expression(LET3[3:-1]), LET3[-1]]
    assert LetStatement(LET_WITH_EXP).tokens == [t("let"), t("a"), t("["), Expression([t("i")]), t("]"), t("="), Expression([t("0")]), t(";")]
    assert ReturnStatement(convert2tokens("return ;")).tokens == convert2tokens("return ;")
    assert ReturnStatement(convert2tokens("return ( a + b ) ;")).tokens == [t("return"), Expression(convert2tokens("( a + b )")) ,t(";")]
    assert IfStatement(IF).tokens == [t("if"), t("("), Expression(EXPRESSION_TERM),  t(")"), t("{"), Statements(LET), t("}")]
    assert IfStatement(IF, [ELSE]).tokens == [t("if"), t("("), Expression(EXPRESSION_TERM),  t(")"), t("{"), Statements(LET), t("}"), t("else"), t("{"), Statements(LET_WITH_EXP), t("}")]
    assert IfStatement(IF, [ELSE, ELSE]).tokens == [t("if"), t("("), Expression(EXPRESSION_TERM),  t(")"), t("{"), Statements(LET), t("}"), t("else"), t("{"), Statements(LET_WITH_EXP), t("}"), t("else"), t("{"), Statements(LET_WITH_EXP), t("}")]
    assert Statements(IF).statements == [IfStatement(IF)]
    assert Statements([*IF, *ELSE, *ELSE]).statements == [IfStatement(IF, [ELSE, ELSE])]
    assert DoStatement(DO).tokens == [t("do"), *(FUNC_CALL[:4]), ExpressionList([]), FUNC_CALL[4], t(";")]
    assert Statements([*LET, *LET, *DO, *IF, *ELSE, *ELSE, *DO]).statements == [LetStatement(LET), LetStatement(LET), DoStatement(DO), IfStatement(IF, [ELSE, ELSE]), DoStatement(DO)]
    assert Statements(IF_ELSE).statements[0] == IfStatement(IF_ELSE[:27], [IF_ELSE[27:]])
    assert Statements(IF_ELSE_IN_IF).statements[0] == IfStatement(IF_ELSE_IN_IF)

BASIC_CLASS = convert2tokens("class Test { method void incSize ( ) { if ( ( ( y + size ) < 254 ) & ( ( x + size ) < 510 ) ) { do erase ( ) ; let size = size + 2 ; do draw ( ) ; } return ; } }")
BASIC_CLASS2 = convert2tokens("class Test2 { method void decSize ( ) { if ( size > 2 ) { do erase ( ) ; let size = size - 2 ; do draw ( ) ; } return ; } }")
def test_SubroutineBody():
    body = SubroutineBody(BASIC_CLASS[8:-1])
    assert body.varDecs == []
    assert body.statements == Statements(BASIC_CLASS[9:-2])
    body = SubroutineBody(BASIC_CLASS2[8:-1])
    assert body.varDecs == []
    assert body.statements == Statements(BASIC_CLASS2[9:-2])

