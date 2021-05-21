
class Relation:

    def __init__(self, source, target, weight = 0, label = "", type = "Directed"):
        self.source = source
        self.target = target
        self.weight = weight
        self.label = label
        self.type = type

    def upgrade_weight(self,weight):
        self.weight = weight

    def get_weight(self):
        return int(self.weight)

    def print_relation(self):
        print(self.source, self.label, self.target, self.weight, self.type)

    def existing_relation(self,relations):
        for rel in relations:
            if str(rel.source) == str(self.source) and str(rel.target) == str(self.target):
                return True
        return False

    def existing_and_upgrade_relation(self,relations):
        for rel in relations:
            if str(rel.source) == str(self.source) and str(rel.target) == str(self.target):
                weight = rel.get_weight() + 50
                rel.upgrade_weight(weight)
                return True
        return False