
# Relation class saves information about the interactions within two profiles
class Relation:

    def __init__(self, source, target, weight = 0, label = "", type = "Directed"):
        self.source = source
        self.target = target
        self.weight = 1
        self.label = label
        self.type = type

    # Upgrade relation weight
    def upgrade_weight(self,weight):
        self.weight = weight

    # Get relation weight
    def get_weight(self):
        return int(self.weight)

    # Print relation
    def print_relation(self):
        print(self.source, self.label, self.target, self.weight, self.type)

    # Return True if relation already exists, False in other case
    def existing_relation(self,relations):
        for rel in relations:
            if str(rel.source) == str(self.source) and str(rel.target) == str(self.target):
                return True
        return False

    # Upgrade 1 point the weight if the relation already exists and return True, False in other case
    def existing_and_upgrade_relation(self,relations):
        for rel in relations:
            if str(rel.source) == str(self.source) and str(rel.target) == str(self.target):
                weight = rel.get_weight() + 1
                rel.upgrade_weight(weight)
                return True
        return False