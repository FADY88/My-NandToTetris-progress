// x = RAM[0]
@R0
D=M
@x
M=D

// y = RAM[1]
@R1
D=M
@y
M=D

// prod = 0
@prod
M=0

(LOOP)
// if (y == 0) goto finish
@y
D=M
@FINISH
D;JEQ

// prod = prod + x
@x
D=M
@prod
M=D+M
// y = y - 1
@y
M=M-1

@LOOP
0;JMP


(FINISH)
@prod
D=M
@R2
M=D

(END)
@END
0;JMP