
class Event(object):
    pass


class UserLoggedIn(Event):
    def __init__(self, userid, oauth2_token, userinfo):
        self.userid = userid
        self.oauth2_token = oauth2_token
        self.userinfo = userinfo


class UserLoggedOut(Event):
    def __init__(self, userid):
        self.userid = userid
