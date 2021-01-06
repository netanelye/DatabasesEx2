import random
import sizeEstimation

options = ["4",
           "4a",
           "5a",
           "6 for NJOIN",
           "6a for NJOIN",
           "6 for cartesian",
           "6a for cartesian",
           "11b"]
R = ["R.A", "R.B", "R.C", "R.D", "R.E"]
S = ["S.D", "S.E", "S.F", "S.H", "S.I"]


def getQuery():
    query = input("Please insert a query:\n")
    if query[-1] == ";":
        query = query[0:-1]
    return treeBuilder(query)


def part_1_menu():
    algebraic_query = getQuery()
    print("Query in algebric way: {0}".format(parseQueryToPrintingFormat(algebraic_query)))
    choice = showMenu()
    new_rule = operateRule(choice - 1, algebraic_query)
    query_printer(new_rule)


def part_2_menu():
    algebraic_query = getQuery()
    return getRandomRules(algebraic_query)


def part_3_menu():
    LQPs = part_2_menu()
    index = 0
    print("--------------------------------------------\nFinal logical query plans:")
    [query_printer(lqp) for lqp in LQPs]
    print("\n")
    path = input("Please insert a path of statistics file to read from:\n")
    # path = r"C:\Users\netan\Desktop\statistics.txt"
    lst = sizeEstimation.fileReader(path)
    R_Data, S_Data = sizeEstimation.extractDataFromFile(lst)
    index = 1
    for query_plan in LQPs:
        print("--------------------------------------------------")
        print("Size estimation for LQP number {0}".format(index))
        sizeEstimation.getSchema(query_plan, R_Data, S_Data)
        index += 1


def extractAttributes(expression):
    listOfAttributes = []
    for item in R:
        if item in expression:
            listOfAttributes.append(item)
    for item in S:
        if item in expression:
            listOfAttributes.append(item)
    return listOfAttributes


def indexInput(index, start, end):
    return (index >= start) and (index <= end)


def showMenu():
    print("Please insert a rule to operate from the list below:")
    i = 0
    for option in options:
        print("{0}. {1}".format(i + 1, option))
        i += 1
    choice = int(input())
    while not indexInput(choice, 1, len(options)):
        choice = int(input("bad input, try again\n"))
    return choice


def treeBuilder(query):
    select = getSelect(query)
    ffrom = getFrom(query)
    where = getWhere(query)
    cartesian = "CARTESIAN"
    sigma = "SIGMA[{0}]".format(where)
    pi = "PI[{0}]".format(select)
    return [pi, sigma, cartesian, ffrom]


def rule_4(algebric_query):
    lst = []
    index = 0
    while index < len(algebric_query):
        if isinstance(algebric_query[index], list):
            lst.append(rule_4(algebric_query[index]))
        elif algebric_query[index].startswith("SIGMA") and "AND" in algebric_query[index]:
            lst += rule_4_inner(algebric_query, index)
            index += 1
            while index < len(algebric_query):
                lst.append(algebric_query[index])
                index += 1
            return lst
        else:
            lst.append(algebric_query[index])
        index += 1
    return lst


def rule_4_inner(algebric_query, sigmaIndex):
    left_condition, right_condition = getSplitConditions(algebric_query[sigmaIndex])
    new_sigma = ["SIGMA[{0}]".format(left_condition), "SIGMA[{0}]".format(right_condition)]
    return new_sigma


def get_sigma(algebric_query):
    index = 0
    for item in algebric_query:
        if item.strartwith("SIGMA") and "AND" in item:
            return index
        index += 1
    return -1


def getSplitConditions(str_expression):
    condition = str_expression.split("SIGMA")[1].strip("[]")
    listOfConditions = deleteRedundantBrackets(condition).split("AND")
    centralAndIndex = getCentralAndIndex(listOfConditions)
    leftCondition = ""
    rightCondition = ""
    for i in range(centralAndIndex + 1):
        leftCondition += listOfConditions[i]
        if i < centralAndIndex:
            leftCondition += "AND"
    index = centralAndIndex + 1
    while index < len(listOfConditions):
        rightCondition += listOfConditions[index]
        if index < len(listOfConditions) - 1:
            rightCondition += "AND"
        index += 1
    return deleteRedundantBrackets(leftCondition.strip()), deleteRedundantBrackets(rightCondition.strip())


def deleteRedundantBrackets(condition):
    new_str = condition
    index = 0
    if new_str[0] == '(' and new_str[-1] == ')' and areBracketsBalanced(new_str[1:-1]):
        return deleteRedundantBrackets(new_str[1:-1])
    else:
        return new_str


def areBracketsBalanced(condition):
    stack = []
    for char in condition:
        if char == '(':
            stack.append(char)
        elif char == ')':
            if not stack:
                return False
            stack.pop()
    if stack:
        return False
    return True


def getCentralAndIndex(listOfConditions):
    num_of_bracket = 0
    num_of_brackets = []
    for substr in listOfConditions:
        for char in substr:
            if char == '(':
                num_of_bracket += 1
            if char == ')':
                num_of_bracket -= 1
        num_of_brackets.append(num_of_bracket)
        num_of_bracket = 0
    flag = False
    offset = 0
    sum = 0
    while not flag:
        i = 0
        for i in range(offset + 1):
            sum += num_of_brackets[i]
        if sum == 0:
            flag = True
        else:
            sum = 0
            offset += 1
    return offset


def getConditions(algebric_query):
    conditions_as_string = (algebric_query.split("SIGMA")[1])[1:-1].split("AND")
    return ['{0}'.format(condition).strip() for condition in conditions_as_string]


def rule_4a(algebric_query):
    new_algebric_query = algebric_query.copy()
    firstSigmaIndex = findTwoSigmas(algebric_query)
    if firstSigmaIndex == -1:
        return new_algebric_query
    else:
        new_algebric_query[firstSigmaIndex], new_algebric_query[firstSigmaIndex + 1] = \
            new_algebric_query[firstSigmaIndex + 1], new_algebric_query[firstSigmaIndex]
        return new_algebric_query


def findTwoSigmas(algebric_query):
    for i in range(len(algebric_query) - 1):
        if algebric_query[i].startswith("SIGMA") and algebric_query[i + 1].startswith("SIGMA"):
            return i
    return -1


def rule_5a(algebric_query):
    new_query = algebric_query.copy()
    piIndex = getPIindex(new_query)
    if piIndex == -1:
        return new_query
    if not new_query[piIndex + 1].startswith("SIGMA"):
        return new_query
    else:
        piContent = extractPredicate(new_query[piIndex])
        sigmaContent = extractPredicate(new_query[piIndex + 1])
        if new_query[piIndex + 2] == "CARTESIAN" or new_query[piIndex + 2] == "NJOIN":
            relation = new_query[piIndex + 3]
        else:
            relation = new_query[piIndex + 2]
        if arePredicatesAgree(piContent, sigmaContent, relation):
            new_query[piIndex], new_query[piIndex + 1] = new_query[piIndex + 1], new_query[piIndex]
        else:
            return new_query
        return new_query


def arePredicatesAgree(first_predicate, second_predicate, relation):
    attributesInFirstPredicate = extractAttributes(first_predicate)
    attributesInSecondPredicate = extractAttributes(second_predicate)
    isComplicatedPredicate = isinstance(relation, list)
    if not isComplicatedPredicate:
        for item in attributesInFirstPredicate:
            if not relation in item:
                return False
    for item in attributesInSecondPredicate:
        if not attributesInFirstPredicate.__contains__(item):
            return False
    return True


def getPIindex(aleric_query):
    index = 0
    for substring in aleric_query:
        if substring.startswith("PI"):
            return index
        else:
            index += 1
    return -1


def rule_6(algebric_query, binary_operation, is_6_a):
    for i in range(len(algebric_query) - 1):
        if isinstance(algebric_query[i], list):
            return rule_6(algebric_query[i], binary_operation, is_6_a)
        if algebric_query[i].startswith("SIGMA") and algebric_query[i + 1].startswith(binary_operation):
            if not is_6_a:
                predicateRefersToRelation = isPredicateRefersToRelation(extractPredicate(algebric_query[i]),
                                                                        algebric_query[i + 2][0])
            else:
                predicateRefersToRelation = isPredicateRefersToRelation(extractPredicate(algebric_query[i]),
                                                                        algebric_query[i + 2][1])
            if predicateRefersToRelation:
                return rule_6_inner(algebric_query, binary_operation, i, is_6_a)
    return algebric_query


def isPredicateRefersToRelation(predicate, relation):
    attributeInPredicate = extractAttributes(predicate)
    if isinstance(relation, list):
        return True
    else:
        for item in attributeInPredicate:
            if relation not in item:
                return False
        return True


def rule_6_inner(algebric_query, binary_operation, index, is_6_a):
    sigma = algebric_query[index]
    if not is_6_a:
        left_operand = buildOperand(sigma, algebric_query[index + 2][0])
        right_operand = algebric_query[index + 2][1]
    else:
        left_operand = algebric_query[index + 2][0]
        right_operand = buildOperand(sigma, algebric_query[index + 2][1])
    new_expression = [binary_operation, [left_operand, right_operand]]
    new_query = []
    for i in range(index):
        new_query.append(algebric_query[i])
    new_query += new_expression
    for i in range(index + 3, len(algebric_query)):
        new_query.append(algebric_query[i])
    return new_query


def buildOperand(sigma, operand):
    lst = [sigma]
    if isinstance(operand, list):
        lst += operand
    else:
        lst.append(operand)
    return lst


def findSigmaNjoin(algebric_query, binary_operation):
    for i in range(len(algebric_query) - 1):
        if algebric_query[i].startswith("SIGMA") and algebric_query[i + 1].startswith(binary_operation):
            return i
    return -1


def rule_11b(algebric_query):
    sigmaIndex = findSigmaAndCartesian(algebric_query)
    if sigmaIndex == -1:
        return algebric_query
    else:
        new_query = []
        njoin = "NJOIN"
        args = algebric_query[sigmaIndex + 2]
        for i in range(sigmaIndex):
            new_query.append(algebric_query[i])
        new_query += [njoin, args]
        for i in range(sigmaIndex + 3, len(algebric_query)):
            new_query.append((algebric_query[i]))
        return new_query


def findSigmaAndCartesian(algebraic_query):
    for i in range(len(algebraic_query) - 1):
        if algebraic_query[i].startswith("SIGMA") and algebraic_query[i + 1].startswith("CARTESIAN"):
            predicate = extractPredicate(algebraic_query[i])
            if isPredicateValidForRule11b(predicate):
                return i
    return -1


def isPredicateValidForRule11b(condition):
    if "AND" in condition:
        subcondition = condition.split("AND", 1)
        return is_simple_condition(subcondition[0].strip()) and \
               is_simple_condition(subcondition[1].strip())
    else:
        return False


def is_simple_condition(condition):
    condA = "S.D=R.D"
    condB = "R.D=S.D"
    condC = "S.E=R.E"
    condD = "R.E=S.E"
    return condition == condA or condition == condB or condition == condC or condition == condD


def extractPredicate(theSigma):
    return theSigma.split("[", 1)[1][0:-1]


def getSelect(query):
    select_split = query.split("SELECT")
    from_split = select_split[1].split("FROM")
    return from_split[0].strip()


def getFrom(query):
    from_split = query.split("FROM")
    where_split = from_split[1].split("WHERE")
    s = where_split[0].strip().split(",")
    return ['{0}'.format(element).strip() for element in s]


def getWhere(query):
    where_split = query.split("WHERE")
    return where_split[1].strip()


def query_printer(algebric_query):
    print(parseQueryToPrintingFormat(algebric_query))


def parseQueryToPrintingFormat(algebraic_query):
    if isinstance(algebraic_query, list):
        if algebraic_query[0].startswith("CARTESIAN") or algebraic_query[0].startswith("NJOIN"):
            return "{0}({1}, {2})".format(algebraic_query[0], parseQueryToPrintingFormat(algebraic_query[1][0]),
                                          parseQueryToPrintingFormat(algebraic_query[1][1]))
        if len(algebraic_query) == 1:
            return algebraic_query[0]
        return "{0}({1})".format(algebraic_query[0], parseQueryToPrintingFormat(algebraic_query[1:]))
    else:
        return algebraic_query


def getRandomRules(original_query):
    finalQueries = []
    for setIndex in range(4):
        new_query = original_query.copy()
        print("set no. {0}".format(setIndex + 1))
        for i in range(10):
            indexOfRuleToOperate = random.randint(0, 7)
            new_query = operateRule(indexOfRuleToOperate, new_query)
            query_printer(new_query)
        finalQueries.append(new_query)
        print("\n")
    return finalQueries


def operateRule(ruleToOperate, original_query):
    if ruleToOperate == 0:
        print("operating rule 4")
        return rule_4(original_query)
    elif ruleToOperate == 1:
        print("operating rule 4a")
        return rule_4a(original_query)
    elif ruleToOperate == 2:
        print("operating rule 5a")
        return rule_5a(original_query)
    elif ruleToOperate == 3:
        print("operating rule 6 with NJOIN")
        return rule_6(original_query, "NJOIN", False)
    elif ruleToOperate == 4:
        print("operating rule 6a with NJOIN")
        return rule_6(original_query, "NJOIN", True)
    elif ruleToOperate == 5:
        print("operating rule 6 with CARTESIAN")
        return rule_6(original_query, "CARTESIAN", False)
    elif ruleToOperate == 6:
        print("operating rule 6a with CARTESIAN")
        return rule_6(original_query, "CARTESIAN", True)
    elif ruleToOperate == 7:
        print("operating rule 11b")
        return rule_11b(original_query)
