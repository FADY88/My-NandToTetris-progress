// push constant 111
@111
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 333
@333
D=A
@SP
AM=M+1
A=A-1
M=D
// push constant 888
@888
D=A
@SP
AM=M+1
A=A-1
M=D
// pop static 8
@SP
AM=M-1
D=M
@StaticT.8
M=D
// pop static 3
@SP
AM=M-1
D=M
@StaticT.3
M=D
// pop static 1
@SP
AM=M-1
D=M
@StaticT.1
M=D
// push static 3
@StaticT.3
D=M
@SP
AM=M+1
A=A-1
M=D
// push static 1
@StaticT.1
D=M
@SP
AM=M+1
A=A-1
M=D
// sub
@SP
AM=M-1
D=M
A=A-1
M=M-D
// push static 8
@StaticT.8
D=M
@SP
AM=M+1
A=A-1
M=D
// add
@SP
AM=M-1
D=M
A=A-1
M=D+M
