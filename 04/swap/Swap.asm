// This file is part of nand2tetris, as taught in The Hebrew University, and
// was written by Aviv Yaish. It is an extension to the specifications given
// [here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
// as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
// Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).

// The program should swap between the max. and min. elements of an array.
// Assumptions:
// - The array's start address is stored in R14, and R15 contains its length
// - Each array value x is between -16384 < x < 16384
// - The address in R14 is at least >= 2048
// - R14 + R15 <= 16383
//
// Requirements:
// - Changing R14, R15 is not allowed.

@R14
A=M
D=M
@R0 // R0 is the min
M=D
@R1 // R1 is the max
M=D
@R2 // is the curr index
M=0
(LOOP)
    @R2
    D=M
    @R15 // array length
    D=M-D // D=len(arr)-i
    @SWAP
    D;JLE // if D <= 0 we iterated over all the array 
    @R2
    D=M
    @R14
    A=D+M
    D=M // D = arr[head+index] 
    @CMP_MIN // check if the number is either the min (or later the max)
    0;JMP
    (CMP_RET)
    @R2
    M=M+1 // inc i
    @LOOP
    0;JMP

(CMP_MIN)
    @R3 // R3 = curr
    M=D
    @R0
    D=D-M
    @CMP_MAX
    D;JGE // curr-min >= 0 => curr >= min. so the number is not the min (or equal) => check if it's the max
    @R3
    D=M
    @R0
    M=D // min = curr
    @CMP_RET
    0;JMP

(CMP_MAX)
    @R3
    D=M
    @R1
    D=D-M
    @CMP_RET
    D;JLE // curr-max =< 0 => max >= curr. so the number is not the max (or equal) => return to main loop
    @R3
    D=M
    @R1
    M=D // max = curr
    @CMP_RET
    0;JMP

(SWAP)
    @R2
    M=0 // i = 0

    // TODO: iterate array. if num == max swap to min, if num == min swap to max.
(LOOP_TWO)
    @R2
    D=M
    @R15 // array length
    D=M-D // D=len(arr)-i
    @END
    D;JLE // if D <= 0 we iterated over all the array
    @R2
    D=M
    @R14
    D=D+M // D = head+index
    @CHECK_EXTR
    0;JMP
    (RET)
    @R2
    M=M+1
    @LOOP_TWO
    0;JMP

(CHECK_EXTR)
    @R3 // R3 = curr address
    M=D
    A=M
    D=M // D = arr[head+index]
    @R0
    D=M-D
    @ISMIN
    D;JEQ
    @R3
    A=M
    D=M
    @R1
    D=M-D
    @ISMAX
    D;JEQ
    @RET
    0;JMP

(ISMIN)
    @R1
    D=M
    @SKIP
    0;JMP
(ISMAX)
    @R0
    D=M
(SKIP)
    @R3
    A=M
    M=D
    @RET
    0;JMP

(END)
    @END
    0;JMP