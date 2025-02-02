from enum import unique
import mongoengine as db
import json
import re
from flask import jsonify

import os
import sys
os.environ['PYTHONHASHSEED'] = '1234'


class codesnippets(db.Document):
    _id = db.IntField()
    language = db.StringField()
    skillcategory = db.StringField()
    difficulty = db.StringField()
    code = db.StringField()
    name = db.StringField()

    def to_json(self):
        return {
            "_id": self._id,
            "languange": self.language,
            "skillcategory": self.skillcategory,
            "difficulty": self.difficulty,
            "code": self.code,
            "name": self.name
        }

class profile(db.Document):
    _id = db.IntField()
    Easy = db.IntField() #number of easy problems solved
    Medium = db.IntField()
    Hard = db.IntField()
    problemsSolved = db.ListField(db.IntField(), default=list)


    def to_json(self):
        return {
            "_id": self._id,
            "Easy": self.Easy,
            "Medium": self.Medium,
            "Hard": self.Hard
        }


def parseCodeFile():
    countIndex = 1
    codesnippets.drop_collection()
    codeFile = open("code.txt", "r")
    parsingCode = False
    pDifficulty = ""
    codeString = ""
    pLanguage = "Default"
    pSkill = "Default"
    pName = "Default"
    for x in codeFile:
        if "LANGUAGE:" in x: #sets language
            pLanguage = x.split("LANGUAGE:",1)[1].strip()
        #if "DIFFICULTY:" in x: #sets difficulty
        #    pDifficulty = int(re.search(r'\d+', x).group()) #currently obselete code; method for extracting integers
        if "DIFFICULTY:" in x: #sets difficulty
            pDifficulty = x.split("DIFFICULTY:",1)[1].strip()
        if "SKILL:" in x:
            pSkill = x.split("SKILL:",1)[1].strip()
        if "NAME:" in x:
            pName = x.split("NAME:",1)[1].strip()
        if "PROBLEMEND" in x: #detects end of problem, saves json file to server
            problem = codesnippets(_id=hash(pName), language=pLanguage, skillcategory = pSkill, difficulty = pDifficulty, code = codeString, name = pName)
            problem.save()
            parsingCode = False
            pDifficulty = ""
            codeString = ""
        if parsingCode: #adds current line of code to codeString
            codeString = codeString + x
        if "PROBLEMSTART" in x: #detects start of problem, begins parsing code into codeString
            parsingCode = True
        #    pNumber = int(re.search(r'\d+', x).group()) #gets integer from line

    codeFile.close()

def updateProfile(problemId, request):
    request_json = request.get_json()
    userID = request_json.get('userID')
    problem = codesnippets.objects.get(_id=problemId)
    if not (profile.objects(_id=userID)):
        newUser = profile(_id=userID, Easy=0, Medium=0, Hard=0, problemsSolved = [])
        newUser.save()
    user = profile.objects(_id=request.json["userID"])
    #if (user.problemsSolved[]) make sure that the user hasnt already completed this problem
    if (problem.difficulty == "Easy"):
        user.update(inc__Easy=1)
    elif (problem.difficulty == "Medium"):
        user.update(inc__Medium=1)
    elif (problem.difficulty == "Hard"):
        user.update(inc__Hard=1)
    user.update(add_to_set__problemsSolved=problemId)
    
    

def returnProblemFromIndex(problemIndex):
    jsonfile = json.loads(codesnippets.objects(_id=str(problemIndex)).to_json()) #returns a single problem
    first_elem = jsonfile[0] #access the list
    return first_elem

def returnProblemsFromLanguage(problemLanguage):
    jsonfile = json.loads(codesnippets.objects(language=problemLanguage).to_json()) #returns a json containing a json
    return jsonify(jsonfile)


def returnProblemsFromLanguageAndSkill(problemLanguage, problemskill):
    jsonfile = json.loads(codesnippets.objects(language=problemLanguage, skillcategory=problemskill).to_json()) #specifies language and skill
    return jsonify(jsonfile)


def returnProfile(profileId):
    jsonfile = json.loads(profile.objects(_id=profileId).to_json()) #returns a profile from id
    return jsonify(jsonfile)




#print("\nFetch a book")
#problem = codesnippets.objects(language="Java").first()