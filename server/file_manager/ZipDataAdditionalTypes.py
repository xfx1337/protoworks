import json

class ProjectData:
    def __init__(self, project):
        self.project = project
        if self.project == None:
            self.data = ""
        self.data = json.dumps(self.project)

    def get_str(self):
        return "PROJECT_DATA: " + self.data