from datetime import datetime

line_diff = "#############"


class Logger:
    def __init__(self, filename):
        self.filename = filename
        self.text = "\n#############\n"
        self.add_line("Current Time: " + str(datetime.now()))

    def add_line(self, line):
        self.text += line + "\n"

    def submit(self):
        file = open(self.filename + ".log", "a+")
        file.write(self.text)
        file.close()