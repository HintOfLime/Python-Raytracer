from PIL import Image

class Solid:
        def __init__ (self, cd, cs):
                self.cd = cd
                self.cs = cs
                return
        
        def getColor(self, position):
                return self.cd, self.cs

class Grid:
        def __init__ (self):
                return

        def getColor(self, texCoord):
                if int(round(texCoord[1], 1)) % 2 == 1:
                        if int(round(texCoord[0], 1)) % 2 == 1:
                                return (200, 200, 200), (255,255,255)
                        else:
                                return (0,0,0), (255,255,255)
                else:
                        if int(round(texCoord[0], 1)) % 2 == 1:
                                return (0, 0, 0), (255,255,255)
                        else:
                                return (200,200,200), (255,255,255)

class Texture:
        def __init__ (self, file):
                self.texture = Image.open(file).convert("RGB")
                return

        def getColor(self, texCoord):
                width, height = self.texture.size
                r, g, b = self.texture.getpixel((texCoord[0]*(width-1), texCoord[1]*(height-1)))
                return (r,g,b), (255,255,255)