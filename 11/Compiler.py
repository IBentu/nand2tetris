from SymbolTable import SymbolTable, ARG_KIND
from Term import Term, TERM_TYPE_CALL, TERM_TYPE_EXP, TERM_TYPE_INT, \
                 TERM_TYPE_KEYWORD,TERM_TYPE_STRING,TERM_TYPE_UNARY_OP, \
                 TERM_TYPE_VAR,TERM_TYPE_VAR_W_EXP
from Expression import ExpressionList, Expression
from Statement import DoStatement, ReturnStatement, LetStatement, WhileStatement, IfStatement
from Class import SubroutineDec

OP2VM_CODE = {
    "+": "add",
    "-": "sub",
    "*": "call Math.multiply 2",
    "/": "call Math.divide 2",
    "&amp;": "and",
    "|": "or",
    "&lt;": "lt",
    "&gt;": "gt",
    "=": "eq", 
}
UNARY_OP2VM_CODE = {
    "-": "neg",
    "~": "not",
    "^": "shiftleft",
    "#": "shiftright",
}

class Compiler:
    def __init__(self, symbols: SymbolTable):
        self.symbol_table = symbols
        self.className = symbols.getClass()
        self.subroutines = symbols.subroutines
        self.vm_code = self.compile()
        
    def OutputString(self) -> str:
        print(self.symbol_table)
        return '\n'.join(self.vm_code)+"\n"

    def compile(self) -> list[str]:
        ret = []
        for subroutine in self.subroutines:
            subroutine_type = subroutine.header_tokens[0].token
            if subroutine_type == "function":
                ret.extend(self.compile_function(subroutine))
            elif subroutine_type == "method":
                ret.extend(self.compile_method(subroutine))
            elif subroutine_type == "constructor":
                ret.extend(self.compile_constructor(subroutine))
            else:
                raise TypeError("invalid subroutine type")
        return ret
    
    def compile_function(self, function: SubroutineDec) -> list[str]:
        name = function.getName()
        ret = [f"function {self.className}.{name} {self.symbol_table.number_of(ARG_KIND, name)}"]
        for s in function.body.statements.statements:
            if type(s) == LetStatement:
                ret.extend(self.compile_let(s))
            elif type(s) == DoStatement:
                ret.extend(self.compile_do(s))
            elif type(s) == IfStatement:
                ret.extend(self.compile_if(s))
            elif type(s) == WhileStatement:
                ret.extend(self.compile_while(s))
            elif type(s) == ReturnStatement:
                ret.extend(self.compile_return(s))
            else:
                raise TypeError(f"invalid type of statement: {s}")
        return ret
    
    def compile_method(self, method: SubroutineDec) -> list[str]:
        pass # TODO
        
    def compile_constructor(self, constructor: SubroutineDec) -> list[str]:
        pass # TODO
    
    def compile_return(self, return_s: ReturnStatement) -> list[str]:
        ret = return_s.getExpression()
        if not len(ret):
            # if nothing is returned, we need to push some constant, since the caller ALWAYS expects a return value
            ret.append(self.push("constant", 0))
        ret.append("return")
        return ret
    
    def compile_do(self, do_s: DoStatement) -> list[str]:
        exps = do_s.getExpressionList()
        ret = self.compile_expressionList(exps)
        ret.append(f"call {do_s.getSubroutineName()} {exps.number_of_expressions()}")
        # since do does not expect anything to return, 
        # we need to pop the stack since a call ALWAYS return a value to the top of the stack
        ret.append(self.pop("temp", 0))
        return ret
    
    def compile_let(self, let_s: LetStatement) -> list[str]:
        pass # TODO

    def compile_while(self, while_s: WhileStatement) -> list[str]:
        pass # TODO
    
    def compile_if(self, if_s: IfStatement) -> list[str]:
        pass # TODO
    
    def compile_expressionList(self, exps: ExpressionList) -> list[str]:
        """
        pushes the expressions to the stack in their order
        """
        ret = []
        for exp in exps.getExpressions():
            ret.extend(self.compile_expression(exp))
        return ret
    
    def compile_expression(self, exp: Expression) -> list[str]:
        tokens = exp.parsed_tokens
        ret = self.compile_term(tokens[0])
        for i in range((len(tokens)-1)//2): # the expression tokens is always with odd length (term op term op term ...)
            ret.extend(self.compile_term(tokens[1+i+1]))
            ret.append(OP2VM_CODE[tokens[1+i].token])
        return ret
            
    def compile_term(self, term: Term) -> list[str]:
        """
        parses the term and returns the command list for pushing the term to the stack
        """
        ret = []
        if term.termType == TERM_TYPE_INT:
            ret.append(self.push("constant", term.tokens[0].token))
        elif term.termType == TERM_TYPE_EXP:
            ret = self.compile_expression(term.tokens[1])
        elif term.termType == TERM_TYPE_UNARY_OP:
            ret = self.compile_term(term.tokens[1])
            ret.append(UNARY_OP2VM_CODE[term.tokens[0].token])
        elif term.termType == TERM_TYPE_CALL:
            pass # TODO
        elif term.termType == TERM_TYPE_STRING:
            pass # TODO
        elif term.termType == TERM_TYPE_KEYWORD:
            pass # TODO
        elif term.termType == TERM_TYPE_VAR:
            pass # TODO
        elif term.termType == TERM_TYPE_VAR_W_EXP:
            pass # TODO
        else:
            raise TypeError("invalid term type")
        return ret
    
    @staticmethod
    def push(segment: str, offset: int) -> str:
        """
        pushes value from *(segment+offset) to the stack.
        segment = constant|this|that|pointer|argument|static|local|temp
        """
        if segment not in ["constant", "this", "that", "pointer", "argument", "static", "local", "temp"]:
            raise ValueError(f"invalid segment for push: {segment}")
        return f"push {segment} {offset}"

    @staticmethod
    def pop(segment, offset: int) -> str:
        """
        pops value from the stack to *(segment+offset).
        segment = this|that|pointer|argument|static|local|temp
        """
        if segment not in ["this", "that", "pointer", "argument", "static", "local", "temp"]:
            raise ValueError(f"invalid segment for pop: {segment}")
        return f"pop {segment} {offset}"
