class User():
    def __init__(self, email, password, firstname, lastname):
        self.email = email
        self.password = password
        self.firstname = firstname
        self.lastname = lastname

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False
    
    @staticmethod
    def check_password(form_password, password):
        return form_password == password