(INIT)  
    @SCREEN
    D=A

    @0
    M=D

(CK_INPUT)
    @KBD
    D=M

    @BLACK
    D;JGT

    @WHITE
    D;JEQ

    @CK_INPUT
    0;JMP

(BLACK)
    @1
    M=-1

    @FILL
    0;JMP

(WHITE)
    @1
    M=0

    @FILL
    0;JMP

(FILL)
    @1
    D=M
    
    @0
    A=M
    M=D

    @0
    D=M+1
    @KBD
    D=A-D

    @0
    M=M+1
    A=M

    @FILL
    D;JGT

    @INIT
    0;JMP