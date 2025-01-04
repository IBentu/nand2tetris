from SymbolTable import SymbolTable, VAR_KIND
from Term import Term, TERM_TYPE_CALL, TERM_TYPE_EXP, TERM_TYPE_INT, \
                 TERM_TYPE_KEYWORD,TERM_TYPE_STRING,TERM_TYPE_UNARY_OP, \
                 TERM_TYPE_VAR,TERM_TYPE_VAR_W_EXP
from Expression import ExpressionList, Expression
from Statement import DoStatement, ReturnStatement, LetStatement, WhileStatement, IfStatement, Statements
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

BUILTIN_TYPES = ["int", "char", "boolean"]

class Compiler:
    def __init__(self, symbols: SymbolTable):
        self.symbol_table = symbols
        self.className = symbols.getClass()
        self.subroutines = symbols.subroutines
        self.if_labels = 0
        self.while_labels = 0
        self.curr_subroutine = ""
        self.vm_code = self.compile()
        
    def OutputString(self) -> str:
        return '\n'.join(self.vm_code)+"\n"

    def compile(self) -> list[str]:
        ret = []
        for subroutine in self.subroutines:
            self.curr_subroutine = subroutine.getName()
            subroutine_type = subroutine.header_tokens[0].token
            if subroutine_type == "function":
                ret.extend(self.compile_function(subroutine))
            elif subroutine_type == "method":
                ret.extend(self.compile_method(subroutine))
            elif subroutine_type == "constructor":
                ret.extend(self.compile_constructor(subroutine))
            else:
                raise TypeError(f"invalid subroutine type {subroutine_type}")
        return ret
    
    def compile_function(self, function: SubroutineDec) -> list[str]:
        name = function.getName()
        ret = [f"function {self.className}.{name} {self.symbol_table.number_of(VAR_KIND, name)}"]
        return ret + self.compile_statements(function.body.statements)
    
    def compile_method(self, method: SubroutineDec) -> list[str]:
        pass # TODO now
        
    def compile_constructor(self, constructor: SubroutineDec) -> list[str]:
        pass # TODO now
    
    def compile_statements(self, statements: Statements) -> list[str]:
        ret = []
        for s in statements.statements:
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
    
    def compile_return(self, return_s: ReturnStatement) -> list[str]:
        ret = []
        exp = return_s.getExpression()
        if not len(exp):
            # if nothing is returned, we need to push some constant, since the caller ALWAYS expects a return value
            ret.append(self.push("constant", 0))
        else:
            ret = self.compile_expression(exp[0])
        ret.append("return")
        return ret
    
    def compile_do(self, do_s: DoStatement) -> list[str]:
        exps = do_s.getExpressionList()
        ret = self.compile_expressionList(exps)
        ret.append(f"call {do_s.getSubroutineName()} {exps.number_of_expressions()}")
        # since do does not expect anything to return, 
        # we need to pop the stack because call ALWAYS has a return value at the top of the stack
        ret.append(self.pop("temp", 0))
        return ret

    def compile_if(self, if_s: IfStatement) -> list[str]:
        ret = self.compile_expression(if_s.expression)
        ret.append(f"if-goto IF_TRUE{self.if_labels}")
        ret.append(f"goto IF_FALSE{self.if_labels}")
        ret.append(f"label IF_TRUE{self.if_labels}")
        ret.extend(self.compile_statements(if_s.statements))
        ret.append(f"goto IF_END{self.if_labels}")
        ret.append(f"label IF_FALSE{self.if_labels}")
        if len(if_s.else_statements):
            ret.extend(self.compile_statements(if_s.else_statements[0]))
        ret.append(f"label IF_END{self.if_labels}")
        self.if_labels += 1
        return ret

    def compile_while(self, while_s: WhileStatement) -> list[str]:
        ret = [f"label WHILE_START{self.while_labels}"]
        ret.extend(self.compile_expression(while_s.expression))
        ret.append("not")
        ret.append(f"if-goto WHILE_END{self.while_labels}")
        ret.extend(self.compile_statements(while_s.statements))
        ret.append(f"goto WHILE_START{self.while_labels}")
        ret.append(f"label WHILE_END{self.while_labels}")
        self.while_labels += 1
        return ret
    
    def compile_let(self, let_s: LetStatement) -> list[str]:
        ret = self.compile_expression(let_s.value)
        var = self.symbol_table.get_symbol(let_s.varName.token, self.curr_subroutine)
        if var.symbol_type in BUILTIN_TYPES:
            ret.append(self.pop(var.kind, var.index))
        else:
            pass # TODO:
        return ret

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
        elif term.termType == TERM_TYPE_KEYWORD:
            keyword = term.tokens[0].token
            if keyword == "true":
                ret = [self.push("constant", 0), "not"]
            elif keyword == "false" or keyword == "null":
                ret.append(self.push("constant", 0)) 
            elif keyword == "this":
                ret.append(self.push("local", 0)) 
            else:
                raise ValueError(f"invalid term keyword {keyword.token}")
        elif term.termType == TERM_TYPE_VAR:
            var = self.symbol_table.get_symbol(term.tokens[0].token, self.curr_subroutine)
            ret.append(self.push(var.kind, var.index))
        elif term.termType == TERM_TYPE_CALL:
            for i, t in enumerate(term.tokens):
                if type(t) is ExpressionList:
                    exps = t
                    break
            ret = self.compile_expressionList(exps)
            subroutineTokens = term.tokens[:i-1]
            if len(subroutineTokens) == 1:
                # subroutineName
                subroutineName = f"{self.className}.{subroutineTokens[0].token}"
            else:
                try:
                    # varName.subroutineName
                    var = self.symbol_table.get_symbol(subroutineTokens[0])
                    # TODO: now
                except:
                    # className.subroutineName
                    subroutineName = "".join(map(lambda x: x.token, subroutineTokens))
            ret.append(f"call {subroutineName} {exps.number_of_expressions()}")
        elif term.termType == TERM_TYPE_STRING:
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
