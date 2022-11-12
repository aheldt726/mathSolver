from interpreters import *


def lp_solver_string_based(objective, constraints):
    # Instantiate the solver
    p = sage.MixedIntegerLinearProgram()
    v = p.new_variable(nonnegative=True, real=True)
    # Objective function is guaranteed to have no inequalities
    ob_fun = 0
    ob_info = determine_coefficients(objective)
    ob_coefficients = ob_info[0]
    maxVarIndex = 0
    varNames = {}  # dictionary so vars in the constraints can match to vars in the objective if the number of vars differs
    for x in range(len(ob_coefficients)):
        ob_fun = ob_fun + ob_coefficients[x] * v[x]
        varNames[ob_info[1][x]] = v[x]
        maxVarIndex = x
    p.set_objective(ob_fun)
    constraints = constraints.strip().split("\n")
    for x in constraints:
        constraintLeft = 0
        constraintRight = 0
        lessThan = False
        greaterThan = False
        equals = False
        parts = []
        if "<=" in x:
            lessThan = True
            parts = x.split("<=")
        elif ">=" in x:
            greaterThan = True
            parts = x.split(">=")
        elif "=" in x:
            equals = True
            parts = x.split("=")
        # left side handling
        cnstLeftInfo = determine_coefficients(parts[0])
        cnstLeftCoefficients = cnstLeftInfo[0]
        for x in range(len(cnstLeftCoefficients)):
            if cnstLeftInfo[1][x] not in varNames:
                varNames[cnstLeftInfo[1][x]] = v[maxVarIndex + 1]
                maxVarIndex += 1
            # print("leftinfo:" + str(cnstLeftInfo[1][x]))
            # print("dictionary:" + str())
            constraintLeft += varNames[cnstLeftInfo[1][x]] * cnstLeftCoefficients[x]
        constraintLeft += get_constant(parts[0])
        # right side handling
        cnstRightInfo = determine_coefficients(parts[1])
        cnstRightCoefficients = cnstRightInfo[0]
        for x in range(len(cnstRightCoefficients)):
            if cnstRightInfo[1][x] not in varNames:
                varNames[cnstRightInfo[1][x]] = v[maxVarIndex + 1]
                maxVarIndex += 1
            constraintRight += varNames[cnstLeftInfo[1][x]] * cnstRightCoefficients[x]
        constraintRight += get_constant(parts[1])
        print(constraintLeft)
        print(constraintRight)
        if lessThan:
            p.add_constraint(constraintLeft <= constraintRight)
        elif greaterThan:
            p.add_constraint(constraintLeft >= constraintRight)
        elif equals:
            p.add_constraint(constraintLeft=constraintRight)
    a = []
    sol = p.solve()
    return [sol, maxVarIndex, varNames, p]

