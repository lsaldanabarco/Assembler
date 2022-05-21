# -*- coding: utf-8 -*-
"""
@author: Lucia Saldana Barco
"""

import sys

# sys.argv[0] -> name of this file
# sys.argv[1] -> first argument
if len(sys.argv) != 2:
    print("usage: python assembler.py prog.asm")
    exit(-1)

# Opens Input file
input_file = open(sys.argv[1], 'r')

# Creates and opens output file
program_name_with_extension = sys.argv[1]
program_name = program_name_with_extension[:program_name_with_extension.index(".")]
output_file = open(program_name + ".hack", "w+")

#input_file = open(".\\nand2tetris\\nand2tetris\\projects\\06\\rect\\Rect.asm", 'r')
#output_file = open(".\\nand2tetris\\nand2tetris\\projects\\06\\rect\\Rect1.hack", "w+")

# Are there more lines in the input?
hasMoreLines = True
# "next variable" variable keeps track of the address the next variable should be assigned to
next_variable = 16

# Symbol Table
symbol_table = {
    "R0" : 0, "R1" : 1, "R2" : 2, "R3" : 3, "R4" : 4, "R5" : 5, "R6" : 6, "R7" : 7, "R8" : 8,
    "R9" : 9, "R10" : 10, "R11" : 11, "R12" : 12, "R13" : 13, "R14" : 14, "R15" : 15,
    "SCREEN" : 16384, 
    "KBD" : 24576, 
    "SP" : 0, 
    "LCL" : 1,
    "ARG" : 2,
    "THIS" : 3,
    "THAT" : 4,
}

# Comp Lookup Table
comp_lookup_table = {
    # a == 0
    "0" : "0101010",
    "1" : "0111111",
    "-1" : "0111010",
    "D" : "0001100",
    "A" : "0110000",
    "!D" : "0001101",
    "!A" : "0110001",
    "-D" : "0001111",
    "-A" : "0110011",
    "D+1" : "0011111",
    "A+1" : "0110111",
    "D-1" : "0001110",
    "A-1" : "0110010",
    "D+A" : "0000010",
    "D-A" : "0010011",
    "A-D" : "0000111",
    "D&A" : "0000000",
    "D|A" : "0010101",
    # a == 1
    "M" : "1110000",
    "!M" : "1110001",
    "-M" : "1110011",
    "M+1" : "1110111",
    "M-1" : "1110010",
    "D+M" : "1000010",
    "D-M" : "1010011",
    "M-D" : "1000111",
    "D&M" : "1000000",
    "D|M" : "1010101",
}

# Dest Lookup Table
dest_lookup_table = {
    "000" : "000",
    "M" : "001",
    "D" : "010",
    "DM" : "011",
    "MD" : "011",
    "A" : "100",
    "AM" : "101",
    "MA" : "101",
    "AD" : "110",
    "DA" : "110",
    "ADM" : "111",
}

# Jump Lookup Table
jump_lookup_table = {
    "000" : "000",
    "JGT" : "001",
    "JEQ" : "010",
    "JGE" : "011",
    "JLT" : "100",
    "JNE" : "101",
    "JLE" : "110",
    "JMP" : "111",
}
 
    
    


# FirstPass function
def first_pass():
    # Initialize PC variable
    program_counter = 0
    # LOOP: (until GetNextCommand returns EOF)
    while hasMoreLines == True:
        # Call get next command function
        command, command_type = get_next_command()
        # If L type add to symbol table with current PC value
        if (command_type == "L") and (command not in symbol_table):
            symbol_table[command] = program_counter #+ 1
        else:
            program_counter += 1


# SecondPass function
def second_pass():
    # LOOP: (until GetNextCommand returns EOF)
    while hasMoreLines == True:
        # Call get next command function
        command, command_type = get_next_command()
        # Ignore L type commands call translate function
        if command_type != "L" and command != None:
            binary_representation = translate(command, command_type)
            output_file.write(binary_representation + "\n")


# Get Next Command function (returns command and type)
def get_next_command():
    command = ""
    
    while command == "":
        # Get next line from file
        line = input_file.readline()
        
        # if line is empty, end of file is reached
        if not line:
            global hasMoreLines 
            hasMoreLines = False
            return None, None
        # Check if it is a blank line or comment
        elif line != "\n" and not(line.startswith("//")):
            # Check for comments after code
            if "//" in line:
                line = line[: line.index("//")]
            line = line.strip() # Remove leading/trailing whitespace
            command = line
            if "@" in line:
                return command, "A"
            elif ("=" in command) or (";" in command):
                return command, "C"
            else:
                return command, "L"



# Translate calls translate_A or translate_C, depending on type
def translate(command, type):
    if type == "A":
        return translate_A(command)
    else:
        return translate_C(command)



def translate_A(command):
    value = None
    # Check if digit after @ 
    if any(map(str.isdigit, command[1:2])):
        value = int(command[1:])
    else: # if non-digit, look up symbol in symbol table
        if command[1:] in symbol_table:
            value = symbol_table[command[1:]]
        elif ("(" + command[1:] + ")") in symbol_table:
            value = symbol_table["(" + command[1:] + ")"]
        else: # If not in symbol table, then it is first appearance of a variable
            global next_variable
            symbol_table[command[1:]] = next_variable # add to symbol table
            value = next_variable
            next_variable += 1 # increment next variable
    
    # Convert value to binary and pad with zeros until you get 16 bits
    binary_value = converter(value)
    while len(binary_value) < 16:
        binary_value = "0" + binary_value
    return binary_value


def translate_C(command):
    # Get Dest
    if command.find("=") != -1:
        dest = command[: command.index("=")].strip()
    else:
        dest = "000"
        
    # Get Comp
    if command.find("=") != -1 and command.find(";") != -1:
        comp = command[command.index("=") + 1 : command.index(";")].strip()
    elif command.find("=") != -1:
        comp = command[command.index("=") + 1 :].strip()
    elif command.find(";") != -1:
        comp = command[: command.index(";")].strip()
    else:
        comp = command.strip()
    
    # Get jump
    if command.find(";") != -1:
        jump = command[command.index(";") + 1 :].strip()
    else:
        jump = "000"
        
    # Assemble binary instruction: 111accccccdddjjj
    binary_instruction_C = "111"
    binary_instruction_C += comp_lookup_table[comp] 
    binary_instruction_C += dest_lookup_table[dest] 
    binary_instruction_C += jump_lookup_table[jump]
    
    return binary_instruction_C
    


def converter(value):
    digit = "0"
    if value >= 1:
        digit = converter(value // 2)
        digit += str(value % 2)
    return digit




# Call first-pass function (pass in input stream)
first_pass()
# Reset input stream (go to beginning of file)
input_file.seek(0,0)
hasMoreLines = True

# Call second-pass function (pass in input, output stream)
second_pass()
# Close Files
input_file.close()
output_file.close()


