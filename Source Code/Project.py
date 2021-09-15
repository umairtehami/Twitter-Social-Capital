
# Saves information related to the project and it extractions
class Project:

    def __init__(self,name, description, path):
        self.name = name
        self.description = description
        self.path = path
        self.extractions = []

    # Add extraction to the current project
    def add_extraction(self,extration):
        self.extractions.append(extration)
