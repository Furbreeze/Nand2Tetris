
        @7  // load base addr
        D=A   // set D = base addr    
        
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        
        @8  // load base addr
        D=A   // set D = base addr    
        
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
        