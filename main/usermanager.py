
class UsersManager:
    def __init__(self):
        self.users_list:list[str] = []
        self.users_count:int = 0

    def add_user(self, name:str):
        self.users_list.append(name)
        self.users_count+=1

    def is_logged_in(self, name:str):
        return name in self.users_list