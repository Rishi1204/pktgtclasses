import json
import csv
import re

def listToString(list):
    """
    Helper function to convert a list to a string
    """
    if len(list) == 0:
        return ""
    if len(list) == 1:
        return list[0]
    else:
        return list[0] + ", " + listToString(list[1:])

def updateExistingScholastics(graduatedBrothers: set) -> None:
    """
    Update the existing scholastics file to move the current takers to past takers and remove graduated brothers
    """
    f = open("src/Scholastics_S23.json", "r")
    courses = json.load(f)
    newCourses = []
    for course in courses:
        if course["Current_Takers"] != "":
            course["Past_Takers"] += ", " + course["Current_Takers"]
            course["Past_Takers"] = course["Past_Takers"].strip(",")
            course["Past_Takers"] = course["Past_Takers"].strip(" ")
        course["Current_Takers"] = ""
        pastTakers = course["Past_Takers"].split(", ")
        # remove graduated brothers
        newPastTakers = []
        for name in pastTakers:
            if name not in graduatedBrothers:
                newPastTakers.append(name)
        newCourse = {"Course_Name": course["Course_Name"], "Current_Takers": course["Current_Takers"], "Past_Takers": listToString(newPastTakers)}
        # only add if it has previous takers
        if newCourse["Past_Takers"] != "":
            newCourses.append(newCourse)
    f.close()
    # write to new file
    o = open("src/Scholastics_F23.json", "w")
    o.write(json.dumps(newCourses))
    o.close()

    
def parseNewScholastics():
    # open the new csv file with new class responses
    f = open("src/Classes_F23.csv", "r")
    data = csv.reader(f)
    # a map of people to classes
    personMap = dict()
    for row in data:
        personMap[row[0]] = row[1].split("\n")
    # a map of classes to people
    classMap = dict()
    for person in personMap:
        for className in personMap[person]:
            if className not in classMap:
                classMap[className] = []
            classMap[className].append(person)
    f.close()
    # populate the updated json file with the new current takers
    f = open("src/Scholastics_F23.json", "r")
    courses = json.load(f)
    newCourses = []
    for course in courses:
        if course["Course_Name"] in classMap:
            newCourse = {"Course_Name": course["Course_Name"].strip(' '), "Current_Takers": listToString(classMap[course["Course_Name"]]), "Past_Takers": course["Past_Takers"]}
            classMap.pop(course["Course_Name"])
        else:
            newCourse = {"Course_Name": course["Course_Name"].strip(' '), "Current_Takers": "", "Past_Takers": course["Past_Takers"]}
        newCourses.append(newCourse)
    # add the new classes
    for className in classMap:
        newCourse = {"Course_Name": className.strip(' '), "Current_Takers": listToString(classMap[className]), "Past_Takers": ""}
        newCourses.append(newCourse)
    f.close()
    # write to new file
    o = open("src/New_Scholastics_F23.json", "w")
    o.write(json.dumps(newCourses))
    o.close()
        

# parseResponses()
graduatedBrothers = {'Matthew Dacey-Koo', 'Sergio', 'David Desrochers', 'Ronald George', 'Gabe'}
updateExistingScholastics(graduatedBrothers)
parseNewScholastics()

                    