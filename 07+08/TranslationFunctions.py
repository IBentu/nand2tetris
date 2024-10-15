jump_counter = -1
return_counter = -1
# useful instructions
INC_STACK = "\n".join([
    "// SP++",
    "@SP",
    "M=M+1"
])
DEC_STACK = "\n".join([
    "// SP--",
    "@SP",
    "M=M-1",
])
INSERT_D_TO_STACK = "\n".join([
    "// RAM[SP]=D",
    "@SP",
    "A=M",
    "M=D",
])
TAKE_FROM_STACK_TO_D = "\n".join([ # !!! I ASSUME THAT A=@SP !!!
    "// D=RAM[SP]",
    "A=M",
    "D=M",
])
def offset_pointer_in_D(segment: str, offset: str) -> str:
    """creates an instruction string that offsets the pointer stored in SEG_MAP[segment] and stores the resulting address in the D register"""
    return "\n".join([
        "// D=RAM[segment]+offset",
        "@"+offset,
        "D=A",
        SEG_POINTERS[segment], # this is the segment pointer
        "D=D+M"
    ])

def bootstrap() -> str:
    return "\n".join([
        "/// BOOTSTRAP CODE ///",
        "@256",
        "D=A",
        "@SP",
        "M=D",
        call_instruction("Sys.init"),
        "/// END BOOSTRAP ///\n"
    ])
#### stack operations ####
SEG_POINTERS = {
    "local": "@LCL",
    "argument": "@ARG",
    "this": "@THIS",
    "that": "@THAT",
}

 # push   
def push_instruction(segment: str, offset: str, static_name: str) -> str:
    """Returns the Hack instructions for pushing the data at the offset in the relevant segment"""
    instr = f"\n/// push {segment} {offset} ///\n"
    if segment == "constant":
        return instr+push_constant(offset)
    if segment == "static":
        return instr+push_static(static_name, offset)
    if segment == "pointer":
        if offset == "0": # this=0
            return instr+push_pointer("this")
        elif offset == "1": # that=1
            return instr+push_pointer("that")
        else:
            raise Exception("invalid syntax")
    if segment == "temp":
        return instr+push_temp(offset)
    return "\n".join([
        instr[:-1], # I don't want to include the \n
        offset_pointer_in_D(segment, offset),
        "// D=RAM[D]",
        "A=D",
        "D=M",
        INSERT_D_TO_STACK,
        INC_STACK
    ])
def push_constant(const: str) -> str:
        """Returns the Hack instructions for pushing the constant"""
        return "\n".join([
            "// D="+const,
            "@"+const,
            "D=A",
            INSERT_D_TO_STACK,
            INC_STACK
        ])
def push_static(name: str, index: str) -> str:
    """Returns the Hack instructions for pushing as static @name.index"""
    return "\n".join([
        f"// D=RAM[@{name}.{index}]",
        f"@{name}.{index}",
        "D=M",
        INSERT_D_TO_STACK,
        INC_STACK
    ])
def push_pointer(segment) -> str:
    """Returns the Hack instructions for pushing the pointer of @segment to the stack"""
    return "\n".join([
        "// D=@segment",
        SEG_POINTERS[segment],
        "D=M",
        INSERT_D_TO_STACK,
        INC_STACK
    ])
def push_temp(offset: str) -> str:
    """Returns the Hack instructions for pushing the data in the R5+offset to the stack"""
    return "\n".join([
        "// @(5+offset)",
        "@"+str(int(offset)+5),
        "D=M",
        INSERT_D_TO_STACK,
        INC_STACK
    ])

# pop
def pop_instruction(segment: str, offset: str, static_name: str) -> str:
    """Returns the Hack instructions for popping the data in the stack to the offset in the relevant segment"""
    instr = f"\n/// pop {segment} {offset} ///\n"
    if segment == "static":
        return instr+pop_static(static_name, offset)
    if segment == "pointer":
        if offset == "0": # this=0
            return instr+pop_pointer("this")
        elif offset == "1": # that=1
            return instr+pop_pointer("that")
        else:
            raise Exception("invalid syntax")
    if segment == "temp":
        return instr+pop_temp(offset)
    return "\n".join([
        instr[:-1],
        offset_pointer_in_D(segment, offset),
        "// @address=D",
        "@address",
        "M=D",
        DEC_STACK, # => A=@SP
        TAKE_FROM_STACK_TO_D,
        "// RAM[address]=D",
        "@address",
        "A=M",
        "M=D"   
    ])
def pop_static(name: str, index: str) -> str:
    """Returns the Hack instructions for popping the data in the stack to var @name.index"""
    return "\n".join([
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "// RAM[@name.index]=D",
        f"@{name}.{index}",
        "M=D"
    ])
def pop_pointer(segment: str) -> str:
    """Returns the Hack instructions for popping the data in the stack to the pointer of @segment to the stack"""
    return "\n".join([
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "// @segment=D",
        SEG_POINTERS[segment],
        "M=D"
    ])
def pop_temp(offset: str) -> str:
    """Returns the Hack instructions for popping the data in the stack to R5+offset"""
    return "\n".join([
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "@"+str(int(offset)+5),
        "M=D"
    ])


#### arithmetic and logical operations ####
OPS_MAP = { # maps from op string to function for formatting comp part of the instruction string
    "add": lambda: "D=D+M",
    "sub": lambda: "D=D-M",
    "eq": lambda: "D=D-M\n"+comparison_op("JEQ"),
    "gt": lambda: "D=D-M\n"+comparison_op("JGT"),
    "lt": lambda: "D=D-M\n"+comparison_op("JLT"),
    "and": lambda: f"D=D&M",
    "or": lambda: f"D=D|M",
}
def comparison_op(jump_condition: str) -> str:
    """Returns the instruction strings (concat-ed) of the comparison, with the result stored in the D register."""
    global jump_counter
    jump_counter += 1
    return "\n".join([
        f"@YES{str(jump_counter)}",
        f"D;{jump_condition}",
        f"(NO{str(jump_counter)})",
        "   D=0",
        f"  @END.{str(jump_counter)}",
        "   0;JMP",
        f"(YES{str(jump_counter)})",
        "   D=-1",
        f"(END.{str(jump_counter)})"
    ]) 

def arithmetic_logical_instruction(op: str) -> str:
    if op == "neg":
        return neg_op()
    if op == "not":
        return not_op()
    return "\n".join([
        f"\n/// {op} ///",
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "@temp",
        "M=D",
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "@temp",
        # D has the first pushed number, M has the second pushed number
        OPS_MAP[op](), # => D=D<op>M
        INSERT_D_TO_STACK,
        INC_STACK
    ])
def neg_op() -> str:
    return "\n".join([
        "\n/// neg ///",
        DEC_STACK,
        "@SP",
        "A=M",
        "M=-M",
        INC_STACK
    ])
def not_op() -> str:
    return "\n".join([
        "\n/// not ///",
        DEC_STACK,
        "@SP",
        "A=M",
        "M=!M",
        INC_STACK
    ])
    
#### branching ####

def label(name: str, funcname: str) -> str:
    """returns a label instruction"""
    return f"({funcname}${name})"
def goto_instruction(label: str, funcname: str) -> str:
    return f"@{funcname}${label}\n0;JMP"
def if_goto_instruction(label: str, funcname: str) -> str:
    if funcname: # in case the label is inside a function
        funcname = funcname+"$"
    return "\n".join([
        "/// if-goto ///",
        DEC_STACK, # popping stack
        TAKE_FROM_STACK_TO_D,
        f"@{funcname}${label}",
        "D;JNE"
    ])
    
#### functions ####
def call_instruction(funcname: str, argsNum=0) -> str:
    global return_counter
    return_counter += 1
    """Returns instructions for calling function func with argsNum arguments. return address and segment pointers are pushed to stack while the ARG and LCL segments are updated"""
    return "\n".join([
        f"\n/// call {funcname} {argsNum} ///",
        # push return address
        push_constant(f"{funcname}$ret.{return_counter}"),        
        # push segment pointers
        push_pointer("local"),
        push_pointer("argument"),
        push_pointer("this"),
        push_pointer("that"),
        # rebase ARG and LCL pointers
        "// rebase ARG = SP - 5 - #ofArgs",
        "@SP",
        "D=M",
        f"@{argsNum+5}",
        "D=D-A", 
        "@ARG",
        "M=D",
        "// rebase LCL = SP",
        "@SP",
        "D=M", 
        "@LCL",
        "M=D",
        # jump to callee and add return label
        "@"+funcname,
        "0;JMP",
        f"({funcname}$ret.{return_counter})",
    ])
def function_instruction(funcname: str, varsNum: int) -> str:
    """Returns instructions for defining function func with varsNum local variables in @LCL initialized to 0"""
    instr = [f"({funcname})", "// init local vars"] # add function label
    for _ in range(varsNum): # init local variables to 0
        instr.append(push_constant("0"))
    return "\n".join(instr)
def return_instruction() -> str: 
    """Returns instructions for returning from a function call, with the return value in the stack of the caller"""
    return "\n".join([
        "\n/// return clause ///",
        "// R13 = frame end address",
        "@LCL",
        "D=M",
        "@R13", # frame end address
        "M=D",
        "// R14 = return ADDRESS = RAM[frame end address - 5]",
        "@5",
        "A=D-A",
        "D=M",
        "@R14",
        "M=D",
        "// RAM[@ARG] = return VALUE",
        DEC_STACK,
        TAKE_FROM_STACK_TO_D, # ret value is on top of the stack by convention
        "@ARG",
        "A=M",
        "M=D",
        "// SP=ARG+1",
        "@ARG",
        "D=M+1",
        "@SP",
        "M=D",
        
        "// pop stack segments pointers",
        value_of_offsetted_R13_address(1),
        "@THAT",
        "M=D",
        
        value_of_offsetted_R13_address(2),
        "@THIS",
        "M=D",
        
        value_of_offsetted_R13_address(3),
        "@ARG",
        "M=D",
        
        value_of_offsetted_R13_address(4),
        "@LCL",
        "M=D",
        
        "// jump to caller function",
        "@R14",
        "A=M",
        "0;JMP"
    ])
def value_of_offsetted_R13_address(offset: int) -> str:
    """Returns instructions for offsetting the address in @R13 by -offset. putting the value of RAM[@R13-offset] in D"""
    if offset < 1: raise Exception("invalid offset")
    if offset == 1: # optimization
        ls = [
            "@R13",
            "A=M-1",
            "D=M"
        ]
    else:
        ls = [
            "@R13",
            "D=M",
            "@"+str(offset),
            "A=D-A",
            "D=M"
        ]
    return "\n".join(ls)