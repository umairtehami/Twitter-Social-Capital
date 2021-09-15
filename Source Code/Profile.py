
#Saves all the information about the list profiles given by user.
class Profile:

    def __init__(self, screen_name = "", id = 0, followers = 0, following = 0, location = "", description = "", created_at = ""):
        self.screen_name = screen_name
        self.id = id
        self.followers = followers
        self.following = following
        self.location = location
        self.description = description
        self.created_at = created_at