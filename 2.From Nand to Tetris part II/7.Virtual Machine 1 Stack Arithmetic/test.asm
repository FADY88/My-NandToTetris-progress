// push constant 1
@1
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 2
@2
D=A
@SP
AM=M+1
A=A-1
M=D
// and
@SP
AM=M-1
D=M
A=A-1
M=D&M
