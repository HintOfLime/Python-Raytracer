from vector import *

class Object:
        def __init__ (self, shape, colorClass, kd, ks, reflectivity):
                self.shape = shape
                self.colorClass = colorClass
                self.kd = kd
                self.ks = ks
                self.reflectivity = reflectivity

        def getColor (self, position):
                return self.colorClass.getColor(position)

class Light:
        def __init__ (self, shape):
                self.shape = shape
                

class Sphere:
        def __init__ (self, center, r):
                self.center = center
                self.radius = r

        def getNormal(self, intersect):
                return normalize(intersect - self.center)

        def getSurfaceCoord (self, intersect):
                hitVec = intersect - self.center
                x = (np.arctan2(hitVec.z, hitVec.x) / (2*np.pi)) + 0.5
                y = 1.0 - (np.arccos(hitVec.y / self.radius) / np.pi)
                return (x, y)

        def getWorldCoord (self, intersect, hitCoord):
                tangent, bitangent = self.getTangentAxis(0)
                return intersect + scale(tangent, hitCoord[0]) + scale(bitangent, hitCoord[1])

        def getTangentAxis (self, intersect):
                norm = normalize(intersect - self.center)
                tangent = normalize(cross(Vector3(0.0,1.0,0.0), norm))
                bitangent  = normalize(cross(norm, tangent))
                return tangent, bitangent

        def intersect (self, ray):
                A = dot(ray.direction, ray.direction)
                dist = ray.origin - self.center
                B = 2.0 * dot(ray.direction, dist)
                C = dot(dist, dist) - (self.radius*self.radius)
                discr = (B*B) - (4*A*C)
                
                if discr <= 0.0:
                        return False

                t0 = (-B - np.sqrt(discr))/(2*A)
                t1 = (-B + np.sqrt(discr))/(2*A)

                if t0 < 0.0 and t1 < 0.0:
                        return False
                elif t0 < 0.0:
                        d = t1
                elif t1 < 0.0:
                        d = t0
                else:
                        d = min(t0, t1)
                
                return d

class Plane:
        def __init__ (self, center, normal, width, height):
                self.center = center
                self.normal = normalize(normal)
                self.width = width
                self.height = height

        def getNormal(self, intersect):
                return normalize(self.normal)

        def getSurfaceCoord (self, intersect):
                x_axis = cross(self.normal, Vector3(1.0,0.0,0.0))
                if magnitude(x_axis) == 0:
                        x_axis = cross(self.normal, Vector3(0.0,0.0,1.0))
                y_axis = cross(self.normal, x_axis)

                hitCoord = ( (dot(intersect-self.center, x_axis)/self.width)  + 0.5,
                             (dot(intersect-self.center, y_axis)/self.height) + 0.5)

                return hitCoord

        def getWorldCoord (self, intersect, hitCoord):
                x_axis, y_axis = self.getTangentAxis(0)
                return intersect + scale(x_axis, (hitCoord[0]-0.5)*self.width) + scale(y_axis, (hitCoord[1]-0.5)*self.height)

        def getTangentAxis (self, intersect):
                x_axis = cross(self.normal, Vector3(1.0,0.0,0.0))
                if magnitude(x_axis) == 0:
                        x_axis = cross(self.normal, Vector3(0.0,0.0,1.0))
                y_axis = cross(self.normal, x_axis)
                return normalize(x_axis), normalize(y_axis)

        def intersect (self, ray):
                denom = dot(self.normal, ray.direction)
                if denom > -0.000001 and denom < 0.000001:
                        return False
                  
                v = self.center - ray.origin
                d = dot(v, self.normal) / denom

                if d < 0.0:
                        return False

                scaled = scale(normalize(ray.direction), d)
                intersect = ray.origin + scaled
                coord = self.getSurfaceCoord(intersect)
                if coord[0] > 1.0 or coord[0] < 0.0:
                        return False
                if coord[1] > 1.0 or coord[1] < 0.0:
                        return False
                return d

def Cube (objects, center, size, colorClass, kd, ks, reflectivity):
                objects.append(Object(Plane( Vector3(center.x+(size.x/2), center.y, center.z),
                                             Vector3(1.0, 0.0, 0.0),
                                             size.z, size.y),
                                             colorClass, kd, ks, reflectivity))

                objects.append(Object(Plane( Vector3(center.x-(size.x/2), center.y, center.z),
                                             Vector3(-1.0, 0.0, 0.0),
                                             size.z, size.y),
                                             colorClass, kd, ks, reflectivity))

                objects.append(Object(Plane( Vector3(center.x, center.y+(size.y/2), center.z),
                                             Vector3(0.0, 1.0, 0.0),
                                             size.z, size.y),
                                             colorClass, kd, ks, reflectivity))

                objects.append(Object(Plane( Vector3(center.x, center.y-(size.y/2), center.z),
                                             Vector3(0.0, -1.0, 0.0),
                                             size.x, size.z),
                                             colorClass, kd, ks, reflectivity))

                objects.append(Object(Plane( Vector3(center.x, center.y, center.z+(size.z/2)),
                                             Vector3(0.0, 0.0, 1.0),
                                             size.x, size.y),
                                             colorClass, kd, ks, reflectivity))

                objects.append(Object(Plane( Vector3(center.x, center.y, center.z-(size.z/2)),
                                             Vector3(0.0, 0.0, -1.0),
                                             size.x, size.y),
                                             colorClass, kd, ks, reflectivity))