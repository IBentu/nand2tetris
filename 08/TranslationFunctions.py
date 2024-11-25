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
        call_instruction("", "Sys.init", 0, "bootstrap"),
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
    return instr+push_segment(segment, offset)
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
def push_segment(segment: str, offset: str) -> str:
    """Returns the Hack instructions for pushing the data from the provided segment"""
    return "\n".join([
        offset_pointer_in_D(segment, offset),
        "// D=RAM[D]",
        "A=D",
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
    return instr+pop_other(segment, offset)
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
def pop_other(segment: str, offset: str) -> str:
    """Returns the Hack instructions for popping the data to the provided segment"""
    return "\n".join([
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


#### arithmetic and logical operations ####
ALL_ARITHMETIC_LOGICAL_OPS = ["add", "sub", "and", "or", "eq", "gt", "lt", "neg", "not"]
UNARY_OPS_MAP = {
    "neg": "M=-M",
    "not": "M=!M",
    "shiftleft": "M=M<<",
    "shiftright": "M=M>>"
}
BINARY_OPS_MAP = {
    "add": lambda _: "D=D+M",
    "sub": lambda _: "D=D-M",
    "and": lambda _: "D=D&M",
    "or": lambda _: "D=D|M",
    "eq": lambda num: comparison_op("JEQ", num),
    "gt": lambda num: comparison_op("JGT", num),
    "lt": lambda num: comparison_op("JLT", num),
}
def comparison_op(jump_condition: str, jump_num: str) -> str:
    """Returns the instruction strings (concat-ed) of the comparison, with the result stored in the D register."""
    return "\n".join([
        "D=D-M",
        f"@YES.{str(jump_num)}",
        f"D;{jump_condition}",
        f"(NO.{str(jump_num)})",
        "   D=0",
        f"  @END.{str(jump_num)}",
        "   0;JMP",
        f"(YES.{str(jump_num)})",
        "   D=-1",
        f"(END.{str(jump_num)})"
    ])
def arithmetic_logical_instruction(op: str, jump_num: int) -> str:
    """Returns the operation's instructions string"""
    if op in UNARY_OPS_MAP.keys():
        return "\n".join([
        DEC_STACK,
        "@SP",
        "A=M",
        UNARY_OPS_MAP[op],
        INC_STACK
    ])
    if op in BINARY_OPS_MAP.keys():
        return "\n".join([
        f"\n/// {op} ///",
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "@R15",
        "M=D",
        DEC_STACK,
        TAKE_FROM_STACK_TO_D,
        "@R15",
        # D has the first pushed number, M has the second pushed number
        BINARY_OPS_MAP[op](jump_num), # => D=D<op>M
        INSERT_D_TO_STACK,
        INC_STACK
    ])
    raise Exception("invalid op")
    

#### branching ####
def label(name: str, funcname: str) -> str:
    """returns a label instruction"""
    return f"({funcname}${name})"
def goto_instruction(label: str, funcname: str) -> str:
    return f"@{funcname}${label}\n0;JMP"
def if_goto_instruction(label: str, funcname: str) -> str:
    return "\n".join([
        "/// if-goto ///",
        DEC_STACK, # popping stack
        TAKE_FROM_STACK_TO_D,
        f"@{funcname}${label}",
        "D;JNE"
    ])


#### functions ####
def call_instruction(caller: str, callee: str, argsNum: int, return_tag: int|str) -> str:
    """Returns instructions for calling function func with argsNum arguments. return address and segment pointers are pushed to stack while the ARG and LCL segments are updated"""
    return "\n".join([
        f"\n/// call {callee} {argsNum} ///",
        # push return address
        push_constant(f"{caller}$ret.{return_tag}"),        
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
        "@"+callee,
        "0;JMP",
        f"({caller}$ret.{return_tag})",
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