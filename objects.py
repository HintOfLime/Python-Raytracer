from vector import *

class Sphere:
        def __init__ (self, center, r, colorClass, kd, ks, reflectivity):
                self.center = center
                self.radius = r
                self.colorClass = colorClass
                self.kd = kd
                self.ks = ks
                self.reflectivity = reflectivity

        def getColor (self, position):
                return self.colorClass.getColor(position)

        def getCoord (self, intersect):
                hitVec = intersect - self.center
                x = (np.arctan2(hitVec.z, hitVec.x) / (2*np.pi)) + 0.5
                y = np.arccos(hitVec.y / self.radius) / np.pi
                return (x, y)
class Plane:
        def __init__ (self, center, normal, colorClass, kd, ks, reflectivity):
                self.center = center
                self.normal = normal
                self.colorClass = colorClass
                self.kd = kd
                self.ks = ks
                self.reflectivity = reflectivity

        def getColor (self, position):
                return self.colorClass.getColor(position)

        def getCoord (self, intersect):
                x_axis = cross(self.normal, Vector3(1.0,0.0,0.0))
                if magnitude(x_axis) == 0:
                        x_axis = cross(self.normal, Vector3(0.0,0.0,1.0))
                y_axis = cross(self.normal, x_axis)

                hitCoord = ( dot(intersect-self.center, x_axis)/30.0+1000000,
                             dot(intersect-self.center, y_axis)/30.0+1000000 )

                return hitCoord