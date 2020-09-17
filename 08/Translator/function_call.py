#!/usr/bin/python3.6

import enum
import sys
import os
import glob


class Command(enum.Enum):
    C_COMMENT = 0
    C_ARITHMETIC = 1
    C_PUSH = 2
    C_POP = 3
    C_LABEL = 4
    C_GOTO = 5
    C_IF = 6
    C_FUNCTION = 7
    C_RETURN = 8
    C_CALL = 9


class Parser:
    def __init__(self, filename):
        self.current_command = ""
        self.current_index = 0
        self.current_command_type = 0
        self.file_list = []

        with open(filename) as file:
            self.file_list = file.readlines()

    def hasMoreCommands(self):
        return self.current_index < len(self.file_list)

    def advance(self):
        current_command = self.file_list[self.current_index]

        # remove comments
        comment_index = current_command.find("//")
        if comment_index >= 0:
            current_command = current_command[0:comment_index]

        # remove ALL whitespace
        current_command = current_command.split()
        current_command = " ".join(current_command)

        self.current_command = current_command
        self.current_index += 1
        return

    def commandType(self):
        if len(self.current_command) == 0:
            return Command.C_COMMENT

        comm = self.current_command.split()[0]

        if comm == "push":
            return Command.C_PUSH
        elif comm == "pop":
            return Command.C_POP
        elif comm in ["add", "sub", "neg", "and", "not", "eq", "gt", "lt", "or"]:
            return Command.C_ARITHMETIC
        elif comm == "label":
            return Command.C_LABEL
        elif comm == "if-goto":
            return Command.C_IF
        elif comm == "goto":
            return Command.C_GOTO
        elif comm == "return":
            return Command.C_RETURN
        elif comm == "call":
            return Command.C_CALL
        elif comm == "function":
            return Command.C_FUNCTION
        else:
            return Command.C_COMMENT

    def arg1(self):
        arg_list = self.current_command.split()

        try:
            arg1 = arg_list[1]
        except:
            arg1 = ""

        return arg1

    def arg2(self):
        arg_list = self.current_command.split()
        try:
            arg2 = arg_list[2]
            arg2 = int(arg2)
        except:
            arg2 = 0

        return arg2


class CodeWriter:
    def __init__(self, filestream):
        self.file = filestream
        self.current_vm_filename = ""
        self.internal_jump_counters = {
            "eq": 0,
            "lt": 0,
            "gt": 0
        }
        self.func_name_return_counters = {}

        self.writeInit()

    def setFilename(self, filename):
        filename = filename.replace('.vm', '')
        self.current_vm_filename = filename

    def writeInit(self):
        output = """
        // GLOBAL INIT CODE
        @256
        D=A
        @SP
        M=D
        """
        self.file.write(output)
        self.writeCall("Sys.init", 0)

    def writeLabel(self, label):
        output = """
        // generated label command
        ({}) // create label
        """.format(label)

        self.file.write(output)

    def writeGoto(self, label):
        output = """
        // generated goto command
        @{} // set address to goto label
        0;JMP  // jump to address
        """.format(label)

        self.file.write(output)

    def writeIf(self, label):
        output = """
        @SP // Grab SP
        M=M-1 // Decrement SP
        A=M  // Set address to SP val
        D=M  // Set D to val at SP
        @{}  // Set location of label
        D;JNE // Jump if D != 0 (true)
        """.format(label)

        self.file.write(output)

    def writeFunction(self, func_name, num_locals):
        # declare a label for function entry
        output = """
        ({})  // declare label for function entry
        """.format(func_name)

        self.file.write(output)
        while num_locals > 0:
            self.writePushPop(Command.C_PUSH, "constant", 0)
            num_locals -= 1

    def writeCall(self, func_name, num_args):
        # create output
        output = ""

        # create guid / label for ret address
        try:
            func_name_ret_count = self.func_name_return_counters[func_name]
        except:
            self.func_name_return_counters[func_name] = 0
            func_name_ret_count = 0

        self.func_name_return_counters[func_name] += 1
        func_ret_label = "RET_ADDR_{}_{}".format(func_name, str(func_name_ret_count))

        # push return label onto stack
        output += """
        @{}
        D=A
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """.format(func_ret_label)

        # push various addresses onto stack
        for temp_label in ["LCL", "ARG", "THIS", "THAT" ]:
            output += """
        @{}
        D=M
        @SP
        A=M
        M=D
        @SP
        M=M+1
        """.format(temp_label)

        # Reposition ARG
        # ARG = SP - num_args - 5
        output += """
        @SP
        D=M
        @{}
        D=D-A
        @5
        D=D-A
        @ARG
        M=D
        """.format(str(num_args))

        # Reposition LCL
        # LCL = SP
        output += """
        @SP
        D=M
        @LCL
        M=D
        """

        # goto f
        output += """
        @{}
        0;JMP
        """.format(func_name)

        # declare return label for return address
        output += """
        ({})
        """.format(func_ret_label)

        self.file.write(output)

    def writeReturn(self):
        output = ""

        # Set temp var FRAME to LCL (R15)
        # FRAME = LCL
        output += """
        // Begin Return Section
        // FRAME = LCL
        @LCL // grab LCL
        D=M  // set D = LCL val
        @R15 // grab R15 (temp FRAME)
        M=D  // set R15 to LCL val
        """

        # Set temp var RET to LCL - 5 (R14)
        # RET = *(FRAME - 5)
        output += """
        // RET = *(FRAME - 5)
        @R15 // get value of R15 (FRAME)
        D=M  // set D to value of FRAME
        @5   // get constant 5
        D=D-A  // set D = FRAME - 5
        A=D  // Address to D
        D=M  // Get Value
        @R14 // get R14 (RET)
        M=D  // set R14 = D
        """

        # Reposition return address for caller
        # *ARG = pop()
        output += """
        // *ARG = pop()
        @SP
        M=M-1
        A=M
        D=M
        @ARG
        A=M
        M=D
        """

        # Restore SP of caller
        # SP = ARG + 1
        output += """
        // SP = ARG + 1
        @ARG
        D=M+1
        @SP
        M=D
        """

        # Restore THAT of caller
        # THAT = *(FRAME-1)
        output += """
        // THAT = *(FRAME - 1)
        @R15
        D=M
        @1
        D=D-A
        A=D
        D=M
        @THAT
        M=D
        """

        # Restore THIS of caller
        # THIS = *(FRAME-2)
        output += """
        // THIS = *(FRAME - 2)
        @R15
        D=M
        @2
        D=D-A
        A=D
        D=M
        @THIS
        M=D
        """

        # Restore ARG of caller
        # ARG = *(FRAME-3)
        output += """
        // ARG = *(FRAME - 3)
        @R15
        D=M
        @3
        D=D-A
        A=D
        D=M
        @ARG
        M=D
        """

        # Restore LCL of caller
        # LCL = *(FRAME-4)
        output += """
        // LCL = *(FRAME - 4)
        @R15
        D=M
        @4
        D=D-A
        A=D
        D=M
        @LCL
        M=D
        """

        # Goto return-address (in the caller's code)
        # goto RET
        output += """
        @R14
        A=M
        0;JMP
        """

        self.file.write(output)

    def writeArithmetic(self, command):
        arithmetic_mapping = {
            "add": "M+D",  # X+Y
            "sub": "M-D",  # X-Y
            "neg": "-D",   # -Y
            "not": "!D",   # !Y
            "and": "M&D",  # X&Y
            "or": "M|D",   # X|Y
            "eq": "D;JEQ",  # (X-Y); JEQ
            "lt": "D;JLT",  # (X-Y); JLT
            "gt": "D;JGT"  # (X-Y); JGT
        }

        output = ""
        is_unary = command in ["lt", "gt", "eq"]
        has_x_input = command not in ["neg", "not"]
        mapped_command = arithmetic_mapping[command]

        # commands are x+y, x-y
        # stack is always [0,x,y]
        # code always arranges D=Y, M=X

        # Grab y input
        output += """
        // pop y value off stack, set D equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get Value
        """

        # Grab x input if necessary
        if has_x_input:
            output += """      
        // pop x value off stack, leave M equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
            """

        if is_unary:
            # templating label
            # ex: "RET_ADDRESS_GT0"
            return_address = "RET_ADDRESS_"
            return_address += command.upper()
            return_address += str(self.internal_jump_counters[command])

            # increment counter
            self.internal_jump_counters[command] += 1

            output += """
        D=M-D // x - y
        @R15  // grab R15
        M=-1  // set R15 to -1 (true)
        @{}  // set jump address
        {}  // D;Jump if condition
        @R15  // grab R15
        M=0  // set R15 to 0 (false)
        ({})  // Jump lable
        @R15  // grab value from if / else
        D=M   // set D to true / false
            """.format(return_address, mapped_command, return_address)
        else:
            output += """
        D={}  // perform arithmetic operation
            """.format(mapped_command)

        # Answer will be stored in D, push onto stack
        output += """
        // push answer onto stack
        @SP
        A=M
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        """

        self.file.write(output)

    def writePushPop(self, command, segment, index):
        segment_mapping = {
            "local": "LCL",
            "argument": "ARG",
            "this": "THIS",
            "that": "THAT",
            "pointer": "3",
            "temp": "5",
            "static": (self.current_vm_filename + "." + str(index)),
            "constant": index
        }

        is_pop = command == Command.C_POP
        base_addr = segment_mapping[segment]
        loaded_from_constant = segment in ["temp", "pointer", "constant"]

        if loaded_from_constant:
            first_assignment = "D=A"
        else:
            first_assignment = "D=M"

        if segment == "constant" or segment == "static":
            addressing_segment = """
        @{}  // load constant into A register
        D=A   // set D = constant A    
        """.format(base_addr)
        else:
            addressing_segment = """
        @{}  // load base addr
        {}   // set D = base addr

        @{}   // load constant index into A register
        D=D+A // add offset to base addr, D now full addr
        """.format(base_addr, first_assignment, index)

        if is_pop:
            push_pop_segment = """
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
        """
        else:
            if segment != "constant":
                addressing_segment += """
        A=D // Load D Val into address
        D=M // set D to value at address
        """
            push_pop_segment = """
        // generated push command
        @SP    // get SP
        A=M    // address to SP
        M=D    // set stack variable
        @SP    // get SP
        M=M+1  // increment SP
        """

        output = addressing_segment + push_pop_segment

        self.file.write(output)

    def close(self):
        self.file.close()


def parse(code_writer: CodeWriter, parser: Parser):
    while parser.hasMoreCommands():
        parser.advance()
        command_type = parser.commandType()
        arg1 = parser.arg1()
        arg2 = parser.arg2()

        if command_type == Command.C_POP or command_type == Command.C_PUSH:
            code_writer.writePushPop(command_type, arg1, arg2)
        elif command_type == Command.C_ARITHMETIC:
            code_writer.writeArithmetic(parser.current_command)
        elif command_type == Command.C_LABEL:
            code_writer.writeLabel(arg1)
        elif command_type == Command.C_GOTO:
            code_writer.writeGoto(arg1)
        elif command_type == Command.C_IF:
            code_writer.writeIf(arg1)
        elif command_type == Command.C_FUNCTION:
            code_writer.writeFunction(arg1, arg2)
        elif command_type == Command.C_CALL:
            code_writer.writeCall(arg1, arg2)
        elif command_type == Command.C_RETURN:
            code_writer.writeReturn()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[+] Missing required argument filename")
        print("[+] Please provide either filename or directory")
        sys.exit()

    file_name = sys.argv[1]

    if not os.path.exists(file_name):
        print("[+] File not found at {}".format(file_name))
        sys.exit()

    abs_path = os.path.abspath(file_name)
    is_dir = os.path.isdir(abs_path)

    if not is_dir and not abs_path.endswith('.vm'):
        print("[+] Provided file must be a .vm file")

    if ".vm" in abs_path:
        output_filename = abs_path[0:-3]
    else:
        output_filename = abs_path.split('/')
        output_filename.append(output_filename[-1])
        output_filename = '/'.join(output_filename)

    output_filename += ".asm"
    filestream = open(output_filename, "w")

    # create single code_writer
    code_writer = CodeWriter(filestream)

    if is_dir:
        glob_search = abs_path + '/*.vm'
        file_list = glob.glob(glob_search)

        for globbed_filename in file_list:
            code_writer_filename = globbed_filename.split('/')[-1]
            code_writer.setFilename(code_writer_filename)
            parser = Parser(globbed_filename)
            parse(code_writer, parser)
    else:
        code_writer_filename = abs_path.split('/')[-1]
        code_writer.setFilename(code_writer_filename)
        parser = Parser(file_name)
        parse(code_writer, parser)

    code_writer.close()
