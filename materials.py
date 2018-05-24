from PIL import Image
import numpy as np
import math

GAMMA = 1.2

def gamma_encode (linear):
        return (pow(linear[0], 1.0/GAMMA), pow(linear[1], 1.0/GAMMA), pow(linear[2], 1.0/GAMMA))

def gamma_decode (encoded):
        if math.isnan(encoded[0]) or math.isnan(encoded[1]) or math.isnan(encoded[2]):
                return (0,0,0)
        linear = (pow(encoded[0], GAMMA), pow(encoded[1], GAMMA), pow(encoded[2], GAMMA))
        linear = (np.clip(linear[0], 0, 255),
                  np.clip(linear[1], 0, 255),
        np.clip(linear[2], 0, 255))
        return linear

class Solid:
        def __init__ (self, cd, cs):
                self.cd = cd
                self.cs = cs
        
        def getColor(self, position):
                return gamma_encode(self.cd), self.cs, (128,128,128)

class Grid:
        def __init__ (self, tiling):
                self.tiling = tiling

        def getColor(self, texCoord):
                if int(texCoord[1]*self.tiling) % 2 == 1:
                        if int(texCoord[0]*self.tiling) % 2 == 1:
                                return gamma_encode((255,255,255)), (255,255,255), (128,128,128)
                        else:
                                return gamma_encode((0,0,0)), (255,255,255), (128,128,128)
                else:
                        if int(texCoord[0]*self.tiling) % 2 == 1:
                                return gamma_encode((0,0,0)), (255,255,255), (128,128,128)
                        else:
                                return gamma_encode((255,255,255)), (255,255,255), (128,128,128)

class Texture:
        def __init__ (self, texture, bumpmap):
                self.texture = TextureWrapper(texture)
                self.bumpmap = TextureWrapper(bumpmap)

        def getColor(self, texCoord):
                return gamma_encode( self.texture.getColor(texCoord) ), (255,255,255), self.bumpmap.getColor(texCoord)

class TextureWrapper:
        def __init__ (self, file):
                self.texture = Image.open(file).convert("RGB")
                return

        def getColor(self, texCoord):
                width, height = self.texture.size
                r, g, b = self.texture.getpixel((texCoord[0]*(width-1.0), texCoord[1]*(height-1.0)))
                return (r,g,b)