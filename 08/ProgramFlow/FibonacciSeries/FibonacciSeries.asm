
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
        
        @3  // load base addr
        D=A   // set D = base addr

        @1   // load constant index into A register
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
        
        @0  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @THAT  // load base addr
        D=M   // set D = base addr

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
        
        @1  // load constant into A register
        D=A   // set D = constant A    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @THAT  // load base addr
        D=M   // set D = base addr

        @1   // load constant index into A register
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
        
        @2  // load constant into A register
        D=A   // set D = constant A    
        
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
        
        @ARG  // load base addr
        D=M   // set D = base addr

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
        
        // generated label command
        (MAIN_LOOP_START) // create label
        
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
        
        @SP // Grab SP
        M=M-1 // Decrement SP
        A=M  // Set address to SP val
        D=M  // Set D to val at SP
        @COMPUTE_ELEMENT  // Set location of label
        D;JNE // Jump if D != 0 (true)
        
        // generated goto command
        @END_PROGRAM // set address to goto label
        0;JMP  // jump to address
        
        // generated label command
        (COMPUTE_ELEMENT) // create label
        
        @THAT  // load base addr
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
        
        @THAT  // load base addr
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
        
        // pop y value off stack, set D equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get Value
              
        // pop x value off stack, leave M equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
            
        D=M+D  // perform arithmetic operation
            
        // push answer onto stack
        @SP
        A=M
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @THAT  // load base addr
        D=M   // set D = base addr

        @2   // load constant index into A register
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
        
        @3  // load base addr
        D=A   // set D = base addr

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
        
        @1  // load constant into A register
        D=A   // set D = constant A    
        
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
            
        D=M+D  // perform arithmetic operation
            
        // push answer onto stack
        @SP
        A=M
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @3  // load base addr
        D=A   // set D = base addr

        @1   // load constant index into A register
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
        
        @1  // load constant into A register
        D=A   // set D = constant A    
        
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
        
        @ARG  // load base addr
        D=M   // set D = base addr

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
        
        // generated goto command
        @MAIN_LOOP_START // set address to goto label
        0;JMP  // jump to address
        
        // generated label command
        (END_PROGRAM) // create label
        