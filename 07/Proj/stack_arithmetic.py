#!/usr/bin/python3.6

import enum
import sys


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
    def __init__(self, filename, codewriter):
        self.current_command = ""
        self.current_index = 0
        self.current_command_type = 0
        self.file_list = []
        self.code_writer = code_writer

        with open(filename) as file:
            self.file_list = file.readlines()

    def hasMoreCommands(self):
        return self.current_index < len(self.file_list)

    def advance(self):
        current_command = self.file_list[self.current_index]

        # remove ALL whitespace
        current_command = current_command.split()
        current_command = " ".join(current_command)

        # remove comments
        comment_index = current_command.find("//")
        if comment_index >= 0:
            current_command = current_command[0:comment_index]

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
        return arg2

    def parse(self):
        while self.hasMoreCommands():
            self.advance()
            command_type = self.commandType()

            if command_type in [Command.C_POP, Command.C_PUSH, Command.C_FUNCTION, Command.C_CALL]:
                segment = self.arg1()
                index = self.arg2()
                self.code_writer.writePushPop(command_type, segment, index)
            elif command_type == Command.C_ARITHMETIC:
                arithmetic_command = self.current_command
                self.code_writer.writeArithmetic(arithmetic_command)

        self.code_writer.close()


class CodeWriter:
    def __init__(self, filename):
        self.output_filename = "./out.asm"
        self.file = open(self.output_filename, "w")
        self.writeBoilerPlate()
        self.internal_jump_counters = {
            "eq": 0,
            "lt": 0,
            "gt": 0
        }

    def setFilename(self, filename):
        self.current_vm_filename = filename

    def writeArithmetic(self, command):
        arithmetic_mapping = {
            "add": "D+M",
            "sub": "M-D",
            "neg": "-M",
            "not": "!M",
            "and": "D&M",
            "or": "D|M",
            "eq": "D;JEQ",
            "lt": "D;JLT",
            "gt": "D;JGT"
        }

        output = ""

        # Grab x input if necessary
        if command not in ["neg", "not"]:
            output += """      
        // pop x value off stack, set D equal to it
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        D=M   // get Value
            """

        # Grab y input
        output += """
        // pop y value off stack, leave as M
        @SP   // get SP
        M=M-1 // decrement SP for "pop"
        A=M   // set A to value of SP
        """

        command_specific_val = arithmetic_mapping[command]

        if command in ["lt", "gt", "eq"]:
            return_address = "RET_ADDRESS_" + command.upper() + str(self.internal_jump_counters[command])

            output += """
        D=M-D // subtract y from x
        @R15  // grab R15
        M=-1  // set R15 to -1 (true)
        @{}  // set label for jump
        {}  // D;Jump if condition
        @R15  // grab R15
        M=0  // set R15 to 0 (false)
        ({})  // Jump label
        @R15  // grab value from if / else
        D=M   // set D to true / false
            """.format(return_address, command_specific_val, return_address)

            self.internal_jump_counters[command] += 1
        else:
            output += """
        D={}  // perform arithmetic operation
            """.format(command_specific_val)

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

    def writeBoilerPlate(self):
        self.file.write("""
        // BOILERPLATE TO INITIALIZE STACK
        @256  // load constant 256 into SP
        D=A   // set D to constant 256
        @SP   // get SP
        M=D   // set SP to 256 (first entry in Stack)
        """)

    def writePushPop(self, command, segment, index):
        output = """
        // generated push command
        @{}   // load constant into A register
        D=A   // set D to constant in A register
        
        @SP   // get SP
        A=M   // set A to SP
        M=D   // set Stack Value to Constant
        @SP   // get SP
        M=M+1 // increment SP
        """.format(index)

        self.file.write(output)

    def close(self):
        self.file.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("[+] Missing required argument filename")

    file_name = sys.argv[1]
    code_writer = CodeWriter(file_name)
    parser = Parser(file_name, code_writer)
    parser.parse()
