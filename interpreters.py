import sage.all as sage
from solverObjects import *

def determine_vars(string):
    """
    TODO: revamp this method to completely find out if a system is linear and then save its dictionary
    :param string:
    :return:
    """
    variables = []  # returns a list of strings
    current_var = ""
    for x in string:
        if x.isalpha():
            current_var = current_var + x
        elif current_var != "":
            variables.append(current_var)
            current_var = ""
    if current_var != "":
        variables.append(current_var)
    return variables

def createEqsOb(input):
    if isinstance(input, str):
        eqs = str_to_eqs(input)
        symExp = eqs[0]
        numExp = eqs[1]
        #TODO: continue this so a sage numeric expression can be input as well as a sage symbolic
    return ExpressionsWrap(symExp, numExp)


def str_to_eqs(stringin, inside_funcs = False):
    """
    Convert string into Sage symbolic and Sage numeric equations
    :param stringin: string for the expression.  Should not contain (in)equalities
    :param inside_funcs: boolean to determine if we also need to consider the existence of functions
    :return: list of two elements, first symbolic, second a dictionary of indices to tuples containing variable
    names and coefficients
    TODO: allow function to interpret functions, which would alter the parentheses conditions
    TODO: support factorials even though factorials are rarely used in functions
    """
    operators = {"+": 1, "-": 1, "*": 1, "/": 1, "^":1}
    parentheses = {"(": 1, ")": 1}
    string = stringin
    varsStrings = {}
    for x in reversed(range(len(string))):
        if x > 0:
            if string[x].isalpha():
                var_arb = string[x]
                i = 1
                while x+i < len(string) and string[x+i].isalpha():
                    var_arb += string[x+i]
                    i += 1
                varsStrings[var_arb] = sage.var(var_arb)
                if string[x-1] not in operators and not string[x-1].isalpha() and string[x-1] not in parentheses:
                    string = string[:x] + "*" + string[x:]
            if string[x] == "(" and string[x-1] not in operators:
                string = string[:x] + "*" + string[x:]
            if x < len(string) - 1 and string[x] == ")" and string[x+1] not in operators:
                string = string[:x+1] + "*" + string[x+1:]
    func1 = sage.sage_eval(string, varsStrings).expand()
    variables = func1.arguments()
    func_comp = 0
    num_func = {}
    i = 0
    for x in variables:
        func_comp += x * func1.coefficient(x,1)
        num_func[i] = (x, func1.coefficient(x,1))
        i += 1
    if func1 != func_comp:
        output = [func1, None]
    else:
        output = [func1, num_func]
    return output


def determine_coefficients(string):
    # Note that this cannot handle nonlinear equations, rewrite another interpreter for nonlinear programs
    # Rather than split an equation here by inequality, do that later and perform this function on its different parts
    variables = determine_vars(string)
    variable_indices = []  # Idea: use these indices along with coefficients to convey the information to the MILP
    coefficients = []
    for x in variables:
        variable_indices.append(string.find(x))  # Guaranteed to find it given determineVars
    for y in variable_indices:
        coefficient = ""
        if y == 0:
            coefficients.append(1)
        else:
            index = y - 1
            if string[y - 1] == "*":
                y = y - 2
                index = y
            while string[index].isnumeric():
                coefficient = string[index] + coefficient
                index -= 1
            if string[index] == "-":
                coefficient = "-" + coefficient
            if coefficient == "":
                coefficient = "1"
            coefficients.append(int(coefficient))
    return [coefficients, variables]  # These are guaranteed to match up


def get_constant(string):
    cnst = ""
    bad = False
    for x in range(len(string)):
        if (string[x].isalpha() and string[x - 1].isnumeric()) or (string[x] == "*" and string[x - 1].isnumeric()):
            cnst = ""
            bad = False
        elif string[x].isnumeric():
            if string[x - 1] == "*" or string[x - 1].isalpha():
                bad = True
            elif not bad:
                cnst += string[x]
        elif not string[x].isnumeric() and cnst != "":
            return cnst
        else:
            bad = False
    if cnst == "":
        return 0
    else:
        return int(cnst)

def constructGraph(nodes):
    None



