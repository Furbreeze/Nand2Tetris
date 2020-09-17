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
        else:
            return Command.C_COMMENT

    def arg1(self):
        arg1 = self.current_command.split()[1]
        return arg1

    def arg2(self):
        arg2 = self.current_command.split()[2]
        try:
            arg2 = int(arg2)
        except:
            print("{} cannot be converted to int".format(arg2))

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

    def setFilename(self, filename):
        filename = filename.replace('.vm','')
        self.current_vm_filename = filename

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

        if segment == "constant":
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
        A=D
        D=M
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

        if command_type in [Command.C_POP, Command.C_PUSH, Command.C_FUNCTION, Command.C_CALL]:
            segment = parser.arg1()
            index = parser.arg2()
            code_writer.writePushPop(command_type, segment, index)
        elif command_type == Command.C_ARITHMETIC:
            arithmetic_command = parser.current_command
            code_writer.writeArithmetic(arithmetic_command)


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
