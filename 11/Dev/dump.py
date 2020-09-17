import enum

class Opp(enum.Enum):
    O_ADD = "add"
    O_SUB = "sub"
    O_NEG = "neg"
    O_EQ = "eq"
    O_GT = "gt"
    O_LT = "lt"
    O_AND = "and"
    O_OR = "or"
    O_NOT = "not"
    O_MUL = "call Math.multiply 2"
    O_DIV = "call Math.divide 2"

mapping = {
    "+": Opp.O_ADD, "-":Opp.O_SUB, 
    "/": Opp.O_DIV, "*":Opp.O_MUL, 
    "&": Opp.O_AND, "|":Opp.O_OR, 
    ">": Opp.O_GT, "<":Opp.O_DIV,
    "=": Opp.O_EQ
}