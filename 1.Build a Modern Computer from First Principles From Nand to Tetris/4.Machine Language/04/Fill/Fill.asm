// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

// R0 = 0
// end = address of KBD
// LOOP:
//   arr = screen
//   if (KBD == 0) goto WHITE
//     // black
//     R0 = -1
//     goto COLOR
//   WHITE:
//     R0 = 0
//
//     COLOR
//       if (RAM[arr] == R0) goto LOOP
//       if (arr == end) goto LOOP
// 
//       RAM[arr] = R0
//       arr = arr + 16
//       goto COLOR

@R0
M=0
@KBD
D=A
@end
M=D
(LOOP)
  // arr = screen
  @SCREEN
  D=A
  @arr
  M=D
// if (KBD == 0) goto WHITE
  @KBD
  D=M
  @WHITE
  D;JEQ
// Black
  @R0
  M=-1
  @COLOR
  0;JMP

  (WHITE)
    @R0
    M=0

  (COLOR)
    // if (RAM[arr] == R0) goto LOOP
    @R0
    D=M
    @arr
    A=M
    D=M-D
    @LOOP
    D;JEQ
    
    // if (arr == end) goto LOOP
    @arr
    D=M
    @end
    D=M-D
    @LOOP
    D;JEQ
//   RAM[arr] = R0
    @R0
    D=M
    @arr
    A=M
    M=D
//   arr = arr + 1
    @arr
    M=M+1
//   goto COLOR
    @COLOR
    0;JMP