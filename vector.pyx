import numpy as np

class Ray(object):
        def __init__ (self, origin, direction):
                self.origin = origin
                self.direction = direction

class Vector3(object):
        def __init__ (self, float x, float y, float z):
                self.x = x
                self.y = y
                self.z = z

        def __add__ (self, other):
                new = Vector3(  self.x + other.x,
                                self.y + other.y,
                                self.z + other.z
                )
                return new

        def __sub__ (self, other):
                new = Vector3(  self.x - other.x,
                                self.y - other.y,
                                self.z - other.z
                )
                return new

        def __mul__ (self, other):
                new = Vector3(  self.x * other.x,
                                self.y * other.y,
                                self.z * other.z
                )
                return new

        def __div__ (self, other):
                new = Vector3(  self.x / other.x,
                                self.y / other.y,
                                self.z / other.z
                )
                return new

def normalize (a):
                cdef float d = magnitude(a)
                if d == 0.0:
                        return Vector3(0,0,0)
                else:
                        return Vector3(a.x/d, a.y/d, a.z/d)

def dot (a, b):
        return (a.x*b.x) + (a.y*b.y) + (a.z*b.z)

def cross (a, b):
        return Vector3( (a.y*b.z) - (a.z*b.y),
                        (a.z*b.x) - (a.x*b.z),
                        (a.x*b.y) - (a.y*b.x))

def scale (a, float k):
        b = Vector3(a.x * k, a.y * k, a.z * k)
        return b

def magnitude (a):
        return np.sqrt((a.x*a.x) + (a.y*a.y) + (a.z*a.z))