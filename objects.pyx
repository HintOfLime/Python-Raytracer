from vector import *
from environment import *

class Object(object):
        def __init__ (self, shape, colorClass, float kd, float ks, float reflectivity):
                self.shape = shape
                self.colorClass = colorClass
                self.kd = kd
                self.ks = ks
                self.reflectivity = reflectivity

        def getColor (self, position):
                return self.colorClass.getColor(position)

class Light(object):
        def __init__ (self, shape):
                self.shape = shape
                

class Sphere(object):
        def __init__ (self, center, float r):
                self.center = center
                self.radius = r
                self.aabb = AABB(self.center, Vector3(self.radius*2.0, self.radius*2.0, self.radius*2.0))

        def getNormal(self, intersect):
                return normalize(intersect - self.center)

        def getSurfaceCoord (self, intersect):
                hitVec = intersect - self.center
                cdef float x = (np.arctan2(hitVec.z, hitVec.x) / (2*np.pi)) + 0.5
                cdef float y = 1.0 - (np.arccos(hitVec.y / self.radius) / np.pi)
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
                if self.aabb.intersect(ray) == False:
                        return False
                
                cdef float A = dot(ray.direction, ray.direction)
                dist = ray.origin - self.center
                cdef float B = 2.0 * dot(ray.direction, dist)
                cdef float C = dot(dist, dist) - (self.radius*self.radius)
                cdef float discr = (B*B) - (4*A*C)
                
                if discr <= 0.0:
                        return False

                cdef float t0 = (-B - np.sqrt(discr))/(2*A)
                cdef float t1 = (-B + np.sqrt(discr))/(2*A)
                if t0 < 0.0 and t1 < 0.0:
                        return False
                elif t0 < 0.0:
                        d = t1
                elif t1 < 0.0:
                        d = t0
                else:
                        d = min(t0, t1)
                
                return d

class Plane(object):
        def __init__ (self, center, normal, size):
                self.center = center
                self.normal = normalize(normal)
                self.size = size
                x_axis, y_axis = self.getTangentAxis(0)
                self.width = dot(x_axis, size)+0.0001
                self.height = dot(y_axis, size)+0.0001
                self.aabb = AABB(self.center, Vector3(self.size.x, self.size.y, self.size.z))

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
                return intersect + scale(x_axis, (hitCoord[0])*self.width) + scale(y_axis, (hitCoord[1])*self.height)

        def getTangentAxis (self, intersect):
                x_axis = cross(self.normal, Vector3(1.0,0.0,0.0))
                if magnitude(x_axis) == 0:
                        x_axis = cross(self.normal, Vector3(0.0,0.0,1.0))
                y_axis = cross(self.normal, x_axis)
                return normalize(x_axis), normalize(y_axis)

        def intersect (self, ray):
                if self.aabb.intersect(ray) == False:
                        return False

                cdef float denom = dot(self.normal, ray.direction)
                if denom > -0.000001 and denom < 0.000001:
                        return False
                  
                v = self.center - ray.origin
                cdef float d = dot(v, self.normal) / denom

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

class AABB(object):
        def __init__(self, center, size):
                self.center = center
                self.size = size
                self.max = Vector3(center.x+(size.x/2), center.y+(size.y/2), center.z+(size.z/2))
                self.min = Vector3(center.x-(size.x/2), center.y-(size.y/2), center.z-(size.z/2))

        def intersect (self, ray):
                cdef float t1 = (self.min.x - ray.origin.x)/(ray.direction.x+0.0001)
                cdef float t2 = (self.max.x - ray.origin.x)/(ray.direction.x+0.0001)
                cdef float tmin = min(t1, t2)
                cdef float tmax = max(t1, t2)

                t1 = (self.min.y - ray.origin.y)/(ray.direction.y+0.0001)
                t2 = (self.max.y - ray.origin.y)/(ray.direction.y+0.0001)
                tmin = max(tmin, min(t1, t2))
                tmax = min(tmax, max(t1, t2))

                t1 = (self.min.z - ray.origin.z)/(ray.direction.z+0.0001)
                t2 = (self.max.z - ray.origin.z)/(ray.direction.z+0.0001)
                tmin = max(tmin, min(t1, t2))
                tmax = min(tmax, max(t1, t2))

                return tmax >= max(0.0, tmin)

        def contains (self, aabb):
                cdef bint x = abs(self.center.x - aabb.center.x) <= (self.size.x + aabb.size.x)/2.0
                cdef bint y = abs(self.center.y - aabb.center.y) <= (self.size.y + aabb.size.y)/2.0
                cdef bint z = abs(self.center.z - aabb.center.z) <= (self.size.z + aabb.size.z)/2.0
                return x and y and z


def Cube (objects, center, size, colorClass, float kd, float ks, float reflectivity):
                p1 = (Object(Plane( Vector3(center.x+(size.x/2), center.y, center.z),
                                             Vector3(1.0, 0.0, 0.0),
                                             Vector3(0, size.y, size.z)),
                                             colorClass, kd, ks, reflectivity))

                p2 = (Object(Plane( Vector3(center.x-(size.x/2), center.y, center.z),
                                             Vector3(-1.0, 0.0, 0.0),
                                             Vector3(0, size.y, size.z)),
                                             colorClass, kd, ks, reflectivity))

                p3 = (Object(Plane( Vector3(center.x, center.y+(size.y/2), center.z),
                                             Vector3(0.0, 1.0, 0.0),
                                             Vector3(size.x, 0, size.z)),
                                             colorClass, kd, ks, reflectivity))

                p4 = (Object(Plane( Vector3(center.x, center.y-(size.y/2), center.z),
                                             Vector3(0.0, -1.0, 0.0),
                                             Vector3(size.x, 0, size.z)),
                                             colorClass, kd, ks, reflectivity))

                p5 = (Object(Plane( Vector3(center.x, center.y, center.z+(size.z/2)),
                                             Vector3(0.0, 0.0, 1.0),
                                             Vector3(size.x, size.y, 0)),
                                             colorClass, kd, ks, reflectivity))

                p6 = (Object(Plane( Vector3(center.x, center.y, center.z-(size.z/2)),
                                             Vector3(0.0, 0.0, -1.0),
                                             Vector3(size.x, size.y, 0)),
                                             colorClass, kd, ks, reflectivity))

                aabb = AABB(center, size)
                p1.aabb = aabb
                p2.aabb = aabb
                p3.aabb = aabb
                p4.aabb = aabb
                p5.aabb = aabb
                p6.aabb = aabb
                objects.extend([p1,p2,p3,p4,p5,p6])