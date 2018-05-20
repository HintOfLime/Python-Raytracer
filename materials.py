class Solid:
        def __init__ (self, cd, cs):
                self.cd = cd
                self.cs = cs
        
        def getColor(self, position):
                return self.cd, self.cs

class Grid:
        def __init__ (self):
                return

        def getColor(self, texCoord):

                if int(texCoord[1]/30) % 2 == 1:
                        if int(texCoord[0]/30) % 2 == 1:
                                return (200, 200, 200), (255,255,255)
                        else:
                                return (16,16,16), (255,255,255)
                else:
                        if int(texCoord[0]/30) % 2 == 1:
                                return (16, 16, 16), (255,255,255)
                        else:
                                return (200,200,200), (255,255,255)