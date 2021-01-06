import math

import functions


def fileReader(path):
    f = open(path, "r+")
    lst = f.readlines()
    f.close()
    return lst


def extractDataFromFile(listOfElements):
    R_Data = getDataAsInt(listOfElements, 2, 8)
    S_Data = getDataAsInt(listOfElements, 11, 17)
    return R_Data, S_Data


def getDataAsInt(listOfElements, start, end):
    dictionary = {"n_": int(listOfElements[start].split("=")[1].strip(r"\n"))}
    for i in range(start + 1, end):
        element = listOfElements[i].split("=")
        key = element[0].strip()
        value = element[1].strip(r"\n")
        dictionary[key] = int(value)
    dictionary["R_"] = 20
    return dictionary


def calculate_operation(query, scheme_r_data, scheme_s_data, index):
    if isinstance(query[0], list):
        return calculate_operation(query[-1], scheme_r_data, scheme_s_data, index)
    if len(query) == 1:
        if query[0] == "R":
            return scheme_r_data
        elif query[0] == "S":
            return scheme_s_data
    else:
        calculate_operation(query[1:], scheme_r_data, scheme_s_data, index)
        print(query)
        if query[0].startswith("CARTESIAN"):
            print("CARTESIAN\ninput: n_R={0} n_s={1}, R_R={2} R_S={3}".
                  format(scheme_r_data["n_R"], scheme_s_data["n_S"], scheme_r_data["R_"], scheme_s_data["R_"]))
        elif query[0].strartwith("SIGMA"):
            print("do something")
        elif query[0].startswith("PI"):
            print("do something")
        elif query[0].startswith("NJOIN"):
            print("do something")
        elif query[0] == "R":
            return scheme_r_data
        elif query[0] == "S":
            return scheme_s_data


def piHandler(query, scheme_r_data, scheme_s_data):
    schema = getSchema(query[1:], scheme_r_data, scheme_s_data)
    print(query[0])
    print("input: n_Schema={0} R_Schema={1}".format(schema["n_"], schema["R_"]))
    attributes = functions.extractAttributes(query[0][1:-1])
    new_schema = {"n_": schema["n_"], "R_": len(attributes) * 4}
    print("output: n_Schema={0} R_Schema={1}".format(new_schema["n_"], new_schema["R_"]))
    return new_schema


def sigmaHandler(query, scheme_r_data, scheme_s_data):
    schema = getSchema(query[1:], scheme_r_data, scheme_s_data)
    print(query[0])
    print("input: n_Schema={0} R_Schema={1}".format(schema["n_"], schema["R_"]))
    predicates = getPredicate(query[0].split("SIGMA")[1][1:-1])
    probability = evaluateProbability(predicates, scheme_r_data, scheme_s_data)
    new_schema = {"n_": math.ceil(schema["n_"] * probability), "R_": schema["R_"]}
    print("output: n_Schema={0}, R_Schema={1}".format(new_schema["n_"], new_schema["R_"]))
    return new_schema


def cartesianHandler(query, scheme_r_data, scheme_s_data):
    schema1 = getSchema(query[1][0], scheme_r_data, scheme_s_data)
    schema2 = getSchema(query[1][1], scheme_r_data, scheme_s_data)
    print(query[0])
    print("input: n_Schema1={0} n_Schema2={1} R_Schema1={2} R_Schema2={3}".
          format(schema1["n_"], schema2["n_"], schema1["R_"], schema2["R_"]))
    new_n = schema1["n_"] * schema2["n_"]
    new_R = schema1["R_"] + schema2["R_"]
    new_schema = {"n_": new_n, "R_": new_R}
    print("output: n_Schema={0}, R_Schema={1}".format(new_n, new_R))
    return new_schema


def njoinHandler(query, scheme_r_data, scheme_s_data):
    schema1 = getSchema(query[1][0], scheme_r_data, scheme_s_data)
    schema2 = getSchema(query[1][1], scheme_r_data, scheme_s_data)
    print(query[0])
    print("input: n_Schema1={0} n_Schema2={1} R_Schema1={2} R_Schema2={3}".
          format(schema1["n_"], schema2["n_"], schema1["R_"], schema2["R_"]))
    new_n = schema1["n_"] * schema2["n_"]
    new_R = schema1["R_"] + schema2["R_"]
    predicates = getPredicate("S.D=R.D AND S.E=R.E")
    probability = evaluateProbability(predicates, scheme_r_data, scheme_s_data)
    new_schema = {"n_": math.ceil(new_n * probability), "R_": new_R}
    print("output: n_Schema={0}, R_Schema={1}".format(new_schema["n_"], new_schema["R_"]))
    return new_schema


def getSchema(query, scheme_r_data, scheme_s_data):
    if query == "R" or query[0] == "R":
        return scheme_r_data
    elif query == "S" or query[0] == "S":
        return scheme_s_data
    elif query[0].startswith("PI"):
        return piHandler(query, scheme_r_data, scheme_s_data)
    elif query[0].startswith("SIGMA"):
        return sigmaHandler(query, scheme_r_data, scheme_s_data)
    elif query[0] == "CARTESIAN":
        return cartesianHandler(query, scheme_r_data, scheme_s_data)
    elif query[0] == "NJOIN":
        return njoinHandler(query, scheme_r_data, scheme_s_data)


def getPredicate(query):
    lst = []
    if "AND" in query:
        lst = query.split("AND")
        [element.strip() for element in lst]
    else:
        lst.append(query)
    return lst


def evaluateProbability(listOfConditions, schema_r_data, schema_s_data):
    probability = 1
    for condition in listOfConditions:
        leftAttribute = condition.split("=")[0]
        if isEqualityOfAttributes(condition):
            rightAttribute = condition.split("=")[1]
            probability *= 1/evaluate2Attributes(leftAttribute, rightAttribute, schema_r_data, schema_s_data)
        else:
            probability *= 1/evaluateAttribute(leftAttribute, schema_r_data, schema_s_data)
    return probability


def evaluateAttribute(attribute, scheme_r_data, scheme_s_data):
    if "S" in attribute.split(".")[0]:
        return scheme_s_data["V({0})".format(attribute.split(".")[1].strip(")( "))]
    elif "R" in attribute.split(".")[0]:
        return scheme_r_data["V({0})".format(attribute.split(".")[1].strip(")( "))]


def evaluate2Attributes(attribute1, attribute2, schema_r_data, schema_s_data):
    return max(evaluateAttribute(attribute1, schema_r_data, schema_s_data),
               evaluateAttribute(attribute2, schema_r_data, schema_s_data))


def isEqualityOfAttributes(condition):
    leftOpernad = condition.split("=")[0]
    rightOpernad = condition.split("=")[1]
    return ("R" in leftOpernad or "S" in leftOpernad) and ("R" in rightOpernad or "S" in rightOpernad)



