# Parses and stores information in .prj file
# TODO: DO SOMETHING USEFUL WITH THIS INFORMATION

class FilePrj:
    def __init__(self, src):
        self.src = src
        s = open(src, "r")
        self.text = s.readline()
        s.close()
        
    def __str__(self):
        s = "="*40 + "\n"
        s = s + "Prj file: \n"
        s = s + "  - " + self.text + "\n"
        s = s + "="*40
        return s
        
    @staticmethod
    def read(src):
        f = FilePrj(src)
        #v = f.text.split(",")
        #for vv in v:
        #    print(vv)
        return f