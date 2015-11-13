import json


class PeopleInfo:
    def __init__(self):
        self.info = {'name': "", "birth day": "", "birth year": "", "location": "", "link": ""}

    def SetName(self, name):
        self.info['name'] = name

    def SetBirthDay(self, birth_day):
        self.info["birth day"] = str(birth_day)

    def SetBirthYear(self, birth_year):
        self.info["birth year"] = str(birth_year)

    def SetLocation(self, location):
        self.info["location"] = location

    def SetLink(self, link):
        self.info["link"] = link

    def JsonDump(self, f):
        json.dump(self.info, f, sort_keys=True)
        f.write("\n")
