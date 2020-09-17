#!/usr/bin/python3.7

import enum
import sys

class Command(enum.Enum):
    A_COMMAND = 1
    C_COMMAND = 2
    L_COMMAND = 3


class Parser:
    # opens the input file and gets ready to parse
    def __init__(self, input_file_path):
        self.file_list = open(input_file_path, "r").readlines()
        self.current_index = 0
        self.current_command = ""
        self.output = []

    # does the input have any more commands
    def hasMoreCommands(self):
        return self.current_index < len(self.file_list)

    # read next command from input, make current command
    # only call if hasMoreCommands() is true
    # where we're "cleaning the command"
    def advance(self):
        current_command = self.file_list[self.current_index]
        # remove ALL whitespace
        current_command = current_command.split()
        current_command = "".join(current_command)

        # remove comments
        comment_index = current_command.find("//")
        if comment_index >= 0:
            current_command = current_command[0:comment_index]

        self.current_command = current_command
        # advance index after fetching command
        self.current_index += 1
        return

    # returns type of current command, A_COMMAND, C_COMMAND, L_COMMAND
    def commandType(self):
        if self.current_command.find('@') > -1:
            return Command.A_COMMAND
        else:
            return Command.C_COMMAND

    # return the symbol of the current command
    # only call when commandType() == L_Command or A_Command
    def symbol(self):
        command = int(self.current_command.strip("@"))
        binary_command = "{0:b}".format(command)
        binary_command = binary_command.rjust(16,"0")
        return binary_command

    # return the dest mnemonic in the current C-Command
    # only call when commandType() == C_Command
    def dest(self):
        equal_index = self.current_command.find('=')
        if equal_index < 0:
            return "null"
        else:
            dest_code = self.current_command[0:equal_index].upper()
            a = m = d = ""
            for char in dest_code:
                if char == "A":
                    a = "A"
                elif char == "M":
                    m = "M"
                elif char == "D":
                    d = "D"

            mnemonic = a + m + d
            return mnemonic

    # return comp mnemonic in the current command
    # only call when commandType() == C_Command
    def comp(self):
        semi_col_index = self.current_command.find(';')
        equal_index = self.current_command.find('=')

        if semi_col_index < 0:
            semi_col_index = None

        if equal_index < 0:
            equal_index = 0
        else:
            equal_index = equal_index + 1

        command = self.current_command[equal_index:semi_col_index]
        mnemonic = command.upper()

        return mnemonic

    # return the jump mnemonic in the current command
    # only call when commandType() == C_Command
    def jump(self):
        semi_col_index = self.current_command.find(';')
        if semi_col_index < 0:
            return "null"
        else:
            command = self.current_command[(semi_col_index + 1):]
            mnemonic = command.upper()
            return mnemonic

    # parse file

    def parse(self):
        while self.hasMoreCommands():
            self.advance()

            command_type = self.commandType()

            if command_type == Command.A_COMMAND:
                command = self.symbol()
                self.output.append(command)
            else:
                dest = Code.dest(self.dest())
                comp = Code.comp(self.comp())
                jump = Code.jump(self.jump())

                command = "111" + comp + dest + jump
                self.output.append(command)

        self.output_to_file()

    def output_to_file(self):
        with open("./output.hack", "a") as file:
            for line in self.output:
                file.write(line + "\n")


class Code:
    # returns binary code of the dest mnemonic
    @staticmethod
    def dest(code):
        codes = {
            "null": "000",
            "M": "001",
            "D": "010",
            "MD": "011",
            "A": "100",
            "AM": "101",
            "AD": "110",
            "AMD": "111"
        }

        try:
            bin_out = codes[code]
            return bin_out
        except:
            print("Invalid dest instruction {}".format(code))
            exit()

    # returns binary code of comp mnemonic
    @staticmethod
    def comp(code):
        codes = {
            "0": "0101010",
            "1": "0111111",
            "-1": "0111010",
            "D": "0001100",
            "A": "0110000",
            "!D": "0001101",
            "!A": "0110001",
            "-D": "0001111",
            "-A": "0110011",
            "D+1": "0011111",
            "A+1": "0110111",
            "D-1": "0001110",
            "A-1": "0110010",
            "D+A": "0000010",
            "D-A": "0010011",
            "A-D": "0000111",
            "D&A": "0000000",
            "D|A": "0010101",
            "M": "1110000",
            "!M": "1110001",
            "-M": "1110011",
            "M+1": "1110111",
            "M-1": "1110010",
            "D+M": "1000010",
            "D-M": "1010011",
            "M-D": "1000111",
            "D&M": "1000000",
            "D|M": "1010101"
        }

        try:
            bin_out = codes[code]
            return bin_out
        except:
            print("Invalid comp instruction {}".format(code))
            exit()

    # returns binary code of jump mnemonic
    @staticmethod
    def jump(code):
        codes = {
            "null": "000",
            "JGT": "001",
            "JEQ": "010",
            "JGE": "011",
            "JLT": "100",
            "JNE": "101",
            "JLE": "110",
            "JMP": "111"
        }

        try:
            bin_out = codes[code]
            return bin_out
        except:
            print("Invalid jump instruction {}".format(code))
            exit()


if __name__ == "__main__":
    input_file = sys.argv[1]
    test = Parser(input_file)
    test.parse()
