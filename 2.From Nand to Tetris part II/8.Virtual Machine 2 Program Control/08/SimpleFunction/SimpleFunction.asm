// -.\08\SimpleFunction\SimpleFunction.vm
// Start of the file: .\08\SimpleFunction\SimpleFunction.vm
// function SimpleFunction.test 2
(SimpleFunction.test)
@SP
AM=M+1
A=A-1
M=0
@SP
AM=M+1
A=A-1
M=0
// push local 0
@0
D=A
@LCL
A=D+M
D=M
@SP
AM=M+1
A=A-1
M=D
// push local 1
@1
D=A
@LCL
A=D+M
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
// not
@SP
A=M-1
M=!M
// push argument 0
@0
D=A
@ARG
A=D+M
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
// push argument 1
@1
D=A
@ARG
A=D+M
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
// return
@LCL
D=M
@endFrame
M=D
@5
A=D-A
D=M
@retAddr
M=D
@SP
AM=M-1
D=M
@ARG
A=M
M=D
@ARG
D=M
@SP
M=D+1
@endFrame
D=M-1
AM=D
D=M
@THAT
M=D
@endFrame
D=M-1
AM=D
D=M
@THIS
M=D
@endFrame
D=M-1
AM=D
D=M
@ARG
M=D
@endFrame
D=M-1
AM=D
D=M
@LCL
M=D
@retAddr
A=M
0;JMP
