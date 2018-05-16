import pygame
import numpy as np
import time

WIDTH = 800.0
HEIGHT = 800.0
BACKGROUND = (0, 0, 0)
MAX_RECURSIONS = 5
DRAW_DISTANCE = 10000


class Vector3:
        def __init__ (self, x, y, z):
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

        def dot (self, other):
                return (self.x*other.x) + (self.y*other.y) + (self.z*other.z)

class Ray:
        def __init__ (self, origin, direction):
                self.origin = origin
                self.direction = direction
                

class Sphere:
        def __init__ (self, x, y, z, r, c, reflectivity):
                self.center = Vector3(x, y, z)
                self.radius = r
                self.color = c
                self.reflectivity = reflectivity

        def getColor (self):
                return self.color

class Plane:
        def __init__ (self, x, y, z, xn, yn, zn, c, reflectivity):
                self.center = Vector3(x, y, z)
                self.normal = Vector3(-xn, -yn, -zn)
                self.color = c
                self.reflectivity = reflectivity

        def getColor (self, position):
                if int(position.z/30) % 2 == 1:
                        if int(position.x/30) % 2 == 1:
                                return (255, 255, 255)
                        else:
                                return (64,64,64)
                else:
                        if int(position.x/30) % 2 == 1:
                                return (64, 64, 64)
                        else:
                                return (255,255,255)

def normalize (a):
                d = magnitude(a)
                if d == 0:
                        return Vector3(0,0,0)
                return Vector3(a.x/d, a.y/d, a.z/d)

def dot (a, b):
        return (a.x*b.x) + (a.y*b.y) + (a.z*b.z)

def scale (a, k):
        b = Vector3(a.x * k, a.y * k, a.z * k)
        return b

def magnitude (a):
        return np.sqrt(pow(a.z, 2) + pow(a.y, 2) + pow(a.z, 2))

def get_first_intersect(ray):
        distance = DRAW_DISTANCE
        closest = 0
        for s in spheres:
                A = dot(ray.direction, ray.direction)
                dist = ray.origin - s.center
                B = 2 * dot(ray.direction, dist)
                C = dot(dist, dist) - (s.radius*s.radius)
                discr = (B*B) - (4*A*C)
                
                if discr < 0:
                        continue

                t0 = (-B - np.sqrt(discr))/(2*A)
                t1 = (-B + np.sqrt(discr))/(2*A)

                if t0 < 0 and t1 < 0:
                        continue

                if t0 < 0:
                        d = t1
                elif t1 < 0:
                        d = t0
                else:
                        d = min(t0, t1)


                #if d < 0:
                #        continue
                
                               
                if d < distance:
                        closest = s
                        distance = d
                
                       
        for p in planes:
                denom = dot(p.normal, ray.direction)
                if denom > -0.000001 and denom < 0.000001:
                        continue
                
                        
                v = p.center - ray.origin
                d = dot(v, p.normal) / denom

                if d < 0:
                        continue

                if d < distance:
                        closest = p
                        distance = d

        return closest, distance

def reflect (incident, intersect, normal):
        incident = normalize(incident)
        normal = normalize(normal)

        origin = intersect + scale(normal, 0.0001)

        direction = incident - scale(normal, 2*dot(incident, normal))
        return Ray(origin, direction)



def trace (ray):
        o, d = get_first_intersect(ray)        
        if type(o) != int:
                if o.__class__.__name__ == "Sphere":
                        scaled = scale(normalize(ray.direction), d)
                        intersect = ray.origin + scaled
                        
                        norm = intersect - o.center
                        norm = normalize(norm)

                        inside = False
                        if dot(ray.direction, norm) > 0:
                                scale(norm, -1)
                                inside = True

                        diffuse = dot(normalize(intersect-light), norm)
                        specular = dot(normalize(intersect-light), normalize(reflect(ray.direction, intersect, norm).direction))

                        if diffuse < 0.2:
                                diffuse = 0.2
                        elif diffuse > 1:
                                diffuse = 1
                        if specular < 0:
                                specular = 0
                        elif specular > 1:
                                specular = 1

                        shadowRay = Ray(intersect+scale(norm, 0.001), intersect - light)
                        a, d = get_first_intersect(shadowRay)
                        if a != 0:
                                diffuse = 0.1
                                specular = 0

                        lighting = (diffuse + specular)/2

                        return (o.getColor()[0]*lighting, o.getColor()[1]*lighting, o.getColor()[2]*lighting), reflect(ray.direction, intersect, norm), o.reflectivity

                if o.__class__.__name__ == "Plane":
                        scaled = scale(normalize(ray.direction), d)
                        intersect = ray.origin + scaled

                        norm = o.normal

                        if dot(ray.direction, norm) > 0:
                                scale(norm, -1)

                        diffuse = (dot(normalize(light-intersect), norm))
                        specular = dot(normalize(light-intersect), reflect(ray.direction, intersect, norm).direction)

                        if diffuse < 0.2:
                                diffuse = 0.2
                        elif diffuse > 1:
                                diffuse = 1
                        if specular < 0:
                                specular = 0
                        elif specular > 1:
                                specular = 1

                        diffuse = 1
                        specular = 1

                        shadowRay = Ray(intersect+scale(norm, 0.1), intersect - light)
                        a, d = get_first_intersect(shadowRay)
                        if a != 0:
                                diffuse = 0.4
                                specular = 0

                        lighting = (diffuse + specular)/2

                        #return (o.color[0]*diffuse, o.color[1]*diffuse, o.color[2]*diffuse), reflect(ray.direction, intersect, norm), o.reflectivity
                        hitPoint = intersect - o.center - Vector3(10000, 10000, 0)
                        return (o.getColor(hitPoint)[0]*lighting, o.getColor(hitPoint)[1]*lighting, o.getColor(hitPoint)[2]*lighting), reflect(ray.direction, intersect, norm), o.reflectivity

        return BACKGROUND, 0, 0

def calc_pixel (ray):
        r = 0
        out = (0,0,0)
        color = [(0,0,0)] * (MAX_RECURSIONS+1)
        reflectivity = [0] * (MAX_RECURSIONS+1)

        while r < MAX_RECURSIONS:
                color[r], ray, reflectivity[r] = trace(ray)
                if ray == 0:
                        break
                r += 1

        i = r
        while i >= 0:
                out = ( (out[0]*reflectivity[i]) + (color[i][0]*(1-reflectivity[i])),
                        (out[1]*reflectivity[i]) + (color[i][1]*(1-reflectivity[i])),
                        (out[2]*reflectivity[i]) + (color[i][2]*(1-reflectivity[i]))
                      )
                i = i-1

        return out, r+1
        
        

pygame.init()
screen = pygame.display.set_mode((int(WIDTH), int(HEIGHT)))

spheres = [ 
            Sphere(100, 125, 100, 25,(0,0,255), 0.3),
            Sphere(90, 70, 120, 30,(0,255,0), 0.3),
            Sphere(180, 80, 200, 70, (255,255,255), 0.9),
            Sphere(50, 110, 150, 40, (255,0,0), 0.3)
          ]

planes =  [ Plane(0,150,0, 0,1,0, (255,255,255), 0.5)
          ]

light = Vector3(0, 500, 500)
done = False
totalRays = 0
i = 0

#spheres.append(Sphere(light.x, light.y, light.z, 5, (255,255,255), 0))

while not done:
        screenX = 0.0
        screenY = 0.0

        r = Ray(Vector3(0, 0, 0), Vector3(0, 0, 1))

        while screenY < HEIGHT:
                while screenX < WIDTH:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        done = True

                        if done:
                                break

                        #r.origin = Vector3(200*(screenX/WIDTH), 200*(screenY/HEIGHT), 0)
                        #r.direction = Vector3(0,0,1)
                        r.origin = Vector3(100, 100, 0)
                        r.direction = normalize(Vector3(((screenX/WIDTH)-0.5)*200*0.008, ((screenY/HEIGHT)-0.5)*200*0.008, 1))
                        c, rays = calc_pixel(r)
                        totalRays += rays
                        screen.set_at((int(screenX), int(screenY)), c)
                        screenX += 1

                if done:
                         break

                screenX = 0
                screenY += 1
                pygame.display.flip()
        print totalRays
        totalRays = 0
        i += 1