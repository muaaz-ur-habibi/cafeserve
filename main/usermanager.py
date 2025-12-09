
class UsersManager:
    def __init__(self):
        self.users_list:list[str] = []

    def add_user(self, name:str):
        self.users_list.append(name)

    def is_logged_in(self, name:str):
        return name in self.users_list