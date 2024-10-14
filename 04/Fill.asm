 // This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// addr = curr address in screen
// the screen pixels are in the range 16384-24576
@SCREEN
D=A
@addr
M=D

(LOOP)
    @KBD
    D=M
    @BLACK // if a key is pressed RAM[KBD] != 0
    D;JNE
    (WHITE)
        @color
        M=0
        @DRAW
        0;JMP
    (BLACK)
        @color
        M=-1
(DRAW)
    @color
    D=M
    @addr
    A=M // @addr is a pointer
    M=D // RAM[addr] = color
    @addr
    M=M+1 // inc addr
    D=M
    @24576 // check if max_screen_pixel (24576) - addr >= 0 and jump to @LOOP if yes
    D=A-D
    @LOOP
    D;JGE
    @SCREEN // otherwise, reset @addr
    D=A
    @addr
    M=D
    @LOOP
    0;JMP