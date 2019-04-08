class Shape:
    def __init__(self):
        self.attribs = None
        self.attribs = {}
        
    def add_attributes(self, attribs):
        for k, a in attribs.items():
            print("key: " + a[0])
            print("val: " + str(a[1]) )
            key = a[0]
            val = a[1]
            self.attribs[key] = val
            
    def __str__(self):
        s = " Attributes: \n"
        for k, v in self.attribs.items():
            s = s + "  - %s: %s \n"%(k, str(v) )
        return s