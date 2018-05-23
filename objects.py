from vector import *

class Sphere:
        def __init__ (self, center, r, colorClass, kd, ks, reflectivity):
                self.center = center
                self.radius = r
                self.colorClass = colorClass
                self.kd = kd
                self.ks = ks
                self.reflectivity = reflectivity

        def getNormal(self, intersect):
                return normalize(intersect - self.center)

        def getColor (self, position):
                return self.colorClass.getColor(position)

        def getSurfaceCoord (self, intersect):
                hitVec = intersect - self.center
                x = (np.arctan2(hitVec.z, hitVec.x) / (2*np.pi)) + 0.5
                y = 1.0 - (np.arccos(hitVec.y / self.radius) / np.pi)
                return (x, y)

        def getTangentAxis (self, intersect):
                norm = normalize(intersect - self.center)
                tangent = normalize(cross(Vector3(0.0,1.0,0.0), norm))
                bitangent  = normalize(cross(norm, tangent))
                return tangent, bitangent

class Plane:
        def __init__ (self, center, normal, width, height, colorClass, kd, ks, reflectivity):
                self.center = center
                self.normal = normalize(normal)
                self.width = width
                self.height = height
                self.colorClass = colorClass
                self.kd = kd
                self.ks = ks
                self.reflectivity = reflectivity

        def getNormal(self, intersect):
                return normalize(self.normal)

        def getColor (self, position):
                return self.colorClass.getColor(position)

        def getSurfaceCoord (self, intersect):
                x_axis = cross(self.normal, Vector3(1.0,0.0,0.0))
                if magnitude(x_axis) == 0:
                        x_axis = cross(self.normal, Vector3(0.0,0.0,1.0))
                y_axis = cross(self.normal, x_axis)

                hitCoord = ( (dot(intersect-self.center, x_axis)/self.width)  + 0.5,
                             (dot(intersect-self.center, y_axis)/self.height) + 0.5)

                return hitCoord

        def getTangentAxis (self, intersect):
                x_axis = cross(self.normal, Vector3(1.0,0.0,0.0))
                if magnitude(x_axis) == 0:
                        x_axis = cross(self.normal, Vector3(0.0,0.0,1.0))
                y_axis = cross(self.normal, x_axis)
                return y_axis, x_axis

def Cube (planes, center, size, colorClass, kd, ks, reflectivity):
                planes.append(Plane(    Vector3(center.x+(size.x/2), center.y, center.z),
                                        Vector3(1.0, 0.0, 0.0),
                                        size.z, size.y,
                                        colorClass, kd, ks, reflectivity))

                planes.append(Plane(    Vector3(center.x-(size.x/2), center.y, center.z),
                                        Vector3(-1.0, 0.0, 0.0),
                                        size.z, size.y,
                                        colorClass, kd, ks, reflectivity))

                planes.append(Plane(    Vector3(center.x, center.y+(size.y/2), center.z),
                                        Vector3(0.0, 1.0, 0.0),
                                        size.z, size.y,
                                        colorClass, kd, ks, reflectivity))

                planes.append(Plane(    Vector3(center.x, center.y-(size.y/2), center.z),
                                        Vector3(0.0, -1.0, 0.0),
                                        size.x, size.z,
                                        colorClass, kd, ks, reflectivity))

                planes.append(Plane(            Vector3(center.x, center.y, center.z+(size.z/2)),
                                        Vector3(0.0, 0.0, 1.0),
                                        size.x, size.y,
                                        colorClass, kd, ks, reflectivity))

                planes.append(Plane(    Vector3(center.x, center.y, center.z-(size.z/2)),
                                        Vector3(0.0, 0.0, -1.0),
                                        size.x, size.y,
                                        colorClass, kd, ks, reflectivity))

                return