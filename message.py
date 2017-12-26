class Message(object):
    def __init__(self):
        super().__init__()
        self.message={}

    def send_message(self,key,value):
        self.message[key]=value

    def find_message(self,key):
        if key in self.message.keys():
            return(self.message[key])
        else:
            return(None)