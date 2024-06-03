class FakeFlaskRequest:
    def __init__(self, json):
        self.json = json
    
    def get_json(self):
        return self.json