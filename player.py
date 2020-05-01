class Player:

    def __init__(self, name, sid):
        self.name = name
        self.status = 'active'
        self.sid = sid
        self.role = ''

    def get_status(self):
        return self.status

    def get_name(self):
        return self.name

    def get_sid(self):
        return self.sid

    def get_role(self):
        return self.role