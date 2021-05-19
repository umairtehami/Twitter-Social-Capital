
class Project:

    def __init__(self,name, description, path):
        self.name = name
        self.description = description
        self.path = path
        self.extractions = []

    def add_extraction(self,extration):
        self.extractions.append(extration)

    def show_extrations(self):
        for extraction in self.extractions:
            print(extraction.name)

    def save_project(self):
        print(self.path)