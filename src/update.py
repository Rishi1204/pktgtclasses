import json
import csv
import re

def updateScholasticsResponses(oldNames):
    f = open("Updated_Scholastics.json", "r")
    o = open("Updated_Scholastics_2.json", "w")
    oldData = json.load(f)
    for item in oldData:
        item["Course_Name"] = (re.sub("[A-Za-z]+", lambda ele: " " + ele[0] + " ", item["Course_Name"])).strip()
        if item["Current_Takers"] != "":
           item["Past_Takers"] += ", " + item["Current_Takers"]
           item["Current_Takers"] = ""
        for name in oldNames:
            formattedName = name + ", "
            if (formattedName in item["Past_Takers"]):
                item["Past_Takers"] = item["Past_Takers"].replace(formattedName, "")
            elif (name in item["Past_Takers"]):
                item["Past_Takers"] = item["Past_Takers"].replace(name, "")
        print(item)           
    f.close()
    o.write(json.dumps(oldData))
    o.close()

def listToString(list):
    if len(list) == 1:
        return list[0]
    else:
        return list[0] + ", " + listToString(list[1:])
    
def parseResponses():
    with open("Classes_S23.csv", 'r') as file:
        data = csv.reader(file)
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
    file.close()
    with open("Updated_Scholastics_2.json", 'r') as file:
        data = json.load(file)
        for className in classMap:
            classExists = False
            for item in data:
                if item["Course_Name"] == className:
                    classExists = True
                    item["Current_Takers"] += listToString(classMap[className])
                    continue
            # if the class has never been taken before
            if not classExists:
                newItem = {"Course_Name": className, "Current_Takers": listToString(classMap[className]), "Past_Takers": ""}
                data.append(newItem)
        o = open("Scholastics_S23.json", "w")
        o.write(json.dumps(data))
        o.close()
    file.close()
        

parseResponses()
# updateScholasticsResponses([])

                    