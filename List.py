
class List:

    def __init__(self, id):
        self.id = id
        self.profiles = []

    def set_list(self,id):
        self.id = id

    def get_list(self):
        return self.id

    def add_profile(self,profile):
        self.profiles.append(profile)

    def get_profile(self,position):
        return self.profiles[position]

    def existing_profile(self,profile):
        for prof in self.profiles:
            if(prof.screen_name == profile):
                return True
        return False

    def existing_profile_name(self, id):
        for prof in self.profiles:
            if(prof.id == id):
                return prof.screen_name
        return ""