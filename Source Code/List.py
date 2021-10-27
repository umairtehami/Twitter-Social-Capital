
# List class saves all the Twitter profiles.
class List:

    def __init__(self, id):
        self.id = id
        self.profiles = []

    # Setter
    def set_list(self,id):
        self.id = id

    # Getter
    def get_list(self):
        return self.id

    # Add new profile to the existing list
    def add_profile(self,profile):
        self.profiles.append(profile)

    # Return the profile in the position "position" of the list
    def get_profile(self,position):
        return self.profiles[position]

    # Return True if the profile exists in the list, False in other case
    def existing_profile(self,id):
        for prof in self.profiles:
            if(str(prof.id) == str(id)):
                return True
        return False

    # Return the screen name if profile exists in the list, "" in other case
    def existing_profile_name(self, id):
        for prof in self.profiles:
            if(str(prof.id) == str(id)):
                return prof.screen_name
        return ""