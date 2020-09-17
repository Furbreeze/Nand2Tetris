
        // GLOBAL INIT CODE
        @256
        D=A
        @SP
        M=D
        
        @RET_ADDR_Sys.init_0
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @LCL
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @ARG
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THIS
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THAT
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @SP
        D=M
        @0
        D=D-A
        @5
        D=D-A
        @ARG
        M=D
        
        @SP
        D=M
        @LCL
        M=D
        
        @Sys.init
        0;JMP
        
        (RET_ADDR_Sys.init_0)
        
        (Class2.set)  // declare label for function entry
        
        @ARG  // load base addr
        D=M   // set D = base addr

        @0   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @Class2.0  // load constant into A register
        D=A   // set D = constant A    
        
        // generated pop command
        @R15  // get R15
        M=D   // temporarily store full addr

        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get value off stack

        @R15  // get R15
        A=M   // set A to R15 val
        M=D   // set RAM[fulladdr] to value off stack
        
        @ARG  // load base addr
        D=M   // set D = base addr

        @1   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @Class2.1  // load constant into A register
        D=A   // set D = constant A    
        
        // generated pop command
        @R15  // get R15
        M=D   // temporarily store full addr

        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get value off stack

        @R15  // get R15
        A=M   // set A to R15 val
        M=D   // set RAM[fulladdr] to value off stack
        
        @0  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        // Begin Return Section
        // FRAME = LCL
        @LCL // grab LCL
        D=M  // set D = LCL val
        @R15 // grab R15 (temp FRAME)
        M=D  // set R15 to LCL val
        
        // RET = *(FRAME - 5)
        @R15 // get value of R15 (FRAME)
        D=M  // set D to value of FRAME
        @5   // get constant 5
        D=D-A  // set D = FRAME - 5
        A=D  // Address to D
        D=M  // Get Value
        @R14 // get R14 (RET)
        M=D  // set R14 = D
        
        // *ARG = pop()
        @SP
        M=M-1
        A=M
        D=M
        @ARG
        A=M
        M=D
        
        // SP = ARG + 1
        @ARG
        D=M+1
        @SP
        M=D
        
        // THAT = *(FRAME - 1)
        @R15
        D=M
        @1
        D=D-A
        A=D
        D=M
        @THAT
        M=D
        
        // THIS = *(FRAME - 2)
        @R15
        D=M
        @2
        D=D-A
        A=D
        D=M
        @THIS
        M=D
        
        // ARG = *(FRAME - 3)
        @R15
        D=M
        @3
        D=D-A
        A=D
        D=M
        @ARG
        M=D
        
        // LCL = *(FRAME - 4)
        @R15
        D=M
        @4
        D=D-A
        A=D
        D=M
        @LCL
        M=D
        
        @R14
        A=M
        0;JMP
        
        (Class2.get)  // declare label for function entry
        
        @Class2.0  // load constant into A register
        D=A   // set D = constant A    
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @Class2.1  // load constant into A register
        D=A   // set D = constant A    
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        // pop y value off stack, set D equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get Value
              
        // pop x value off stack, leave M equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
            
        D=M-D  // perform arithmetic operation
            
        // push answer onto stack
        @SP
        A=M
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        // Begin Return Section
        // FRAME = LCL
        @LCL // grab LCL
        D=M  // set D = LCL val
        @R15 // grab R15 (temp FRAME)
        M=D  // set R15 to LCL val
        
        // RET = *(FRAME - 5)
        @R15 // get value of R15 (FRAME)
        D=M  // set D to value of FRAME
        @5   // get constant 5
        D=D-A  // set D = FRAME - 5
        A=D  // Address to D
        D=M  // Get Value
        @R14 // get R14 (RET)
        M=D  // set R14 = D
        
        // *ARG = pop()
        @SP
        M=M-1
        A=M
        D=M
        @ARG
        A=M
        M=D
        
        // SP = ARG + 1
        @ARG
        D=M+1
        @SP
        M=D
        
        // THAT = *(FRAME - 1)
        @R15
        D=M
        @1
        D=D-A
        A=D
        D=M
        @THAT
        M=D
        
        // THIS = *(FRAME - 2)
        @R15
        D=M
        @2
        D=D-A
        A=D
        D=M
        @THIS
        M=D
        
        // ARG = *(FRAME - 3)
        @R15
        D=M
        @3
        D=D-A
        A=D
        D=M
        @ARG
        M=D
        
        // LCL = *(FRAME - 4)
        @R15
        D=M
        @4
        D=D-A
        A=D
        D=M
        @LCL
        M=D
        
        @R14
        A=M
        0;JMP
        
        (Sys.init)  // declare label for function entry
        
        @6  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @8  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @RET_ADDR_Class1.set_0
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @LCL
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @ARG
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THIS
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THAT
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @SP
        D=M
        @2
        D=D-A
        @5
        D=D-A
        @ARG
        M=D
        
        @SP
        D=M
        @LCL
        M=D
        
        @Class1.set
        0;JMP
        
        (RET_ADDR_Class1.set_0)
        
        @5  // load base addr
        D=A   // set D = base addr

        @0   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        
        // generated pop command
        @R15  // get R15
        M=D   // temporarily store full addr

        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get value off stack

        @R15  // get R15
        A=M   // set A to R15 val
        M=D   // set RAM[fulladdr] to value off stack
        
        @23  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @15  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @RET_ADDR_Class2.set_0
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @LCL
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @ARG
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THIS
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THAT
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @SP
        D=M
        @2
        D=D-A
        @5
        D=D-A
        @ARG
        M=D
        
        @SP
        D=M
        @LCL
        M=D
        
        @Class2.set
        0;JMP
        
        (RET_ADDR_Class2.set_0)
        
        @5  // load base addr
        D=A   // set D = base addr

        @0   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        
        // generated pop command
        @R15  // get R15
        M=D   // temporarily store full addr

        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get value off stack

        @R15  // get R15
        A=M   // set A to R15 val
        M=D   // set RAM[fulladdr] to value off stack
        
        @RET_ADDR_Class1.get_0
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @LCL
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @ARG
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THIS
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THAT
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @SP
        D=M
        @0
        D=D-A
        @5
        D=D-A
        @ARG
        M=D
        
        @SP
        D=M
        @LCL
        M=D
        
        @Class1.get
        0;JMP
        
        (RET_ADDR_Class1.get_0)
        
        @RET_ADDR_Class2.get_0
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @LCL
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @ARG
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THIS
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @THAT
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        
        @SP
        D=M
        @0
        D=D-A
        @5
        D=D-A
        @ARG
        M=D
        
        @SP
        D=M
        @LCL
        M=D
        
        @Class2.get
        0;JMP
        
        (RET_ADDR_Class2.get_0)
        
        // generated label command
        (WHILE) // create label
        
        // generated goto command
        @WHILE // set address to goto label
        0;JMP  // jump to address
        
        (Class1.set)  // declare label for function entry
        
        @ARG  // load base addr
        D=M   // set D = base addr

        @0   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @Class1.0  // load constant into A register
        D=A   // set D = constant A    
        
        // generated pop command
        @R15  // get R15
        M=D   // temporarily store full addr

        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get value off stack

        @R15  // get R15
        A=M   // set A to R15 val
        M=D   // set RAM[fulladdr] to value off stack
        
        @ARG  // load base addr
        D=M   // set D = base addr

        @1   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @Class1.1  // load constant into A register
        D=A   // set D = constant A    
        
        // generated pop command
        @R15  // get R15
        M=D   // temporarily store full addr

        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get value off stack

        @R15  // get R15
        A=M   // set A to R15 val
        M=D   // set RAM[fulladdr] to value off stack
        
        @0  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        // Begin Return Section
        // FRAME = LCL
        @LCL // grab LCL
        D=M  // set D = LCL val
        @R15 // grab R15 (temp FRAME)
        M=D  // set R15 to LCL val
        
        // RET = *(FRAME - 5)
        @R15 // get value of R15 (FRAME)
        D=M  // set D to value of FRAME
        @5   // get constant 5
        D=D-A  // set D = FRAME - 5
        A=D  // Address to D
        D=M  // Get Value
        @R14 // get R14 (RET)
        M=D  // set R14 = D
        
        // *ARG = pop()
        @SP
        M=M-1
        A=M
        D=M
        @ARG
        A=M
        M=D
        
        // SP = ARG + 1
        @ARG
        D=M+1
        @SP
        M=D
        
        // THAT = *(FRAME - 1)
        @R15
        D=M
        @1
        D=D-A
        A=D
        D=M
        @THAT
        M=D
        
        // THIS = *(FRAME - 2)
        @R15
        D=M
        @2
        D=D-A
        A=D
        D=M
        @THIS
        M=D
        
        // ARG = *(FRAME - 3)
        @R15
        D=M
        @3
        D=D-A
        A=D
        D=M
        @ARG
        M=D
        
        // LCL = *(FRAME - 4)
        @R15
        D=M
        @4
        D=D-A
        A=D
        D=M
        @LCL
        M=D
        
        @R14
        A=M
        0;JMP
        
        (Class1.get)  // declare label for function entry
        
        @Class1.0  // load constant into A register
        D=A   // set D = constant A    
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @Class1.1  // load constant into A register
        D=A   // set D = constant A    
        
        A=D // Load D Val into address
        D=M // set D to value at address
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        // pop y value off stack, set D equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get Value
              
        // pop x value off stack, leave M equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
            
        D=M-D  // perform arithmetic operation
            
        // push answer onto stack
        @SP
        A=M
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        // Begin Return Section
        // FRAME = LCL
        @LCL // grab LCL
        D=M  // set D = LCL val
        @R15 // grab R15 (temp FRAME)
        M=D  // set R15 to LCL val
        
        // RET = *(FRAME - 5)
        @R15 // get value of R15 (FRAME)
        D=M  // set D to value of FRAME
        @5   // get constant 5
        D=D-A  // set D = FRAME - 5
        A=D  // Address to D
        D=M  // Get Value
        @R14 // get R14 (RET)
        M=D  // set R14 = D
        
        // *ARG = pop()
        @SP
        M=M-1
        A=M
        D=M
        @ARG
        A=M
        M=D
        
        // SP = ARG + 1
        @ARG
        D=M+1
        @SP
        M=D
        
        // THAT = *(FRAME - 1)
        @R15
        D=M
        @1
        D=D-A
        A=D
        D=M
        @THAT
        M=D
        
        // THIS = *(FRAME - 2)
        @R15
        D=M
        @2
        D=D-A
        A=D
        D=M
        @THIS
        M=D
        
        // ARG = *(FRAME - 3)
        @R15
        D=M
        @3
        D=D-A
        A=D
        D=M
        @ARG
        M=D
        
        // LCL = *(FRAME - 4)
        @R15
        D=M
        @4
        D=D-A
        A=D
        D=M
        @LCL
        M=D
        
        @R14
        A=M
        0;JMP
        