// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Mult.asm

// Multiplies R0 and R1 and stores the result in R2.
// (R0, R1, R2 refer to RAM[0], RAM[1], and RAM[2], respectively.)
// The algorithm is based on repetitive addition.

// init R2 = 0 and move R0 value to R3 
@2
M=0
@0
D=M
@3
M=D
@LOOP
D;JGT // if R0 > 0 jump to LOOP
// otherwise, jump to END
@END
0;JMP

(LOOP)
    // get R1
    @1
    D=M
    // add to R2
    @2
    M=D+M
    // dec R3
    @3
    M=M-1
    // iterate if R3 > 0
    D=M
    @LOOP
    D;JGT

(END)
    @END
    0;JMP