import pygame
import numpy as np
import time

WIDTH = 200.0
HEIGHT = 200.0
BACKGROUND = (45, 120, 170)
MAX_RECURSIONS = 3
DRAW_DISTANCE = 100000


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
                self.normal = Vector3(xn, yn, zn)
                self.color = c
                self.reflectivity = reflectivity

        def getColor (self, position):
                if int(position.z/10) % 2 == 1:
                        if int(position.x/10) % 2 == 1:
                                return (255, 255, 255)
                        else:
                                return (16,16,16)
                else:
                        if int(position.x/10) % 2 == 1:
                                return (16, 16, 16)
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
                C = dot(dist, dist) - s.radius**2
                discr = B**2 - 4*C*A
                
                if discr >= 0:
                        t0 = (-B + np.sqrt(discr))/(2*A)
                        t1 = (-B - np.sqrt(discr))/(2*A)
                        
                        d = min(t0,t1)
                                
                        if d < distance:
                                closest = s
                                distance = d
                       
        for p in planes:
                denom = dot(p.normal, ray.direction)
                if denom > 0:
                        v = p.center - ray.origin
                        d = dot(v, p.normal) / denom
                        
                        if d >= 0:        
                                if d < distance:
                                        closest = p
                                        distance = d

        return closest, distance

def reflect (incident, intersect, normal):
        origin = intersect
        direction = normalize(incident) - scale(normalize(normal), -2*dot(incident, normal))
        return Ray(origin, direction)


def trace (ray):
        o, d = get_first_intersect(ray)        
        if type(o) != int:
                if o.__class__.__name__ == "Sphere":
                        scaled = scale(normalize(ray.direction), d)
                        intersect = ray.origin + scaled
                        norm = intersect - o.center

                        temp = dot(norm, norm)
                        temp = 1.0 / np.sqrt(temp)
                        norm = scale(norm, temp)

                        diffuse = (dot(normalize(light-intersect), norm))

                        specular = dot(normalize(light-intersect), reflect(ray.direction, intersect, norm).direction)

                        shadowRay = Ray(intersect, light-intersect)
                        a, b = get_first_intersect(shadowRay)
                        #if a != 0:
                                #diffuse = 0
                                #specular = 0

                        if diffuse < 0.1:
                                diffuse = 0.1
                        elif diffuse > 1:
                                diffuse = 1


                        return (o.getColor()[0]*diffuse, o.getColor()[1]*diffuse, o.getColor()[2]*diffuse), reflect(ray.direction, intersect, norm), o.reflectivity

                if o.__class__.__name__ == "Plane":
                        scaled = scale(normalize(ray.direction), d)
                        intersect = ray.origin + scaled

                        norm = o.normal

                        #diffuse = (dot(normalize(light-intersect), norm))

                        #specular = dot(normalize(light-intersect), reflect(ray.direction, intersect, norm).direction)

                        #shadowRay = Ray(intersect, light-intersect)
                        #a, b = get_first_intersect(shadowRay)
                        #if a != 0:
                                #diffuse = 0
                                #specular = 0

                        #if diffuse < 0.1:
                                #diffuse = 0.1
                        #elif diffuse > 1:
                                #diffuse = 1


                        #return (o.color[0]*diffuse, o.color[1]*diffuse, o.color[2]*diffuse), reflect(ray.direction, intersect, norm), o.reflectivity
                        hitPoint = intersect - o.center
                        return (o.getColor(hitPoint)[0], o.getColor(hitPoint)[1], o.getColor(hitPoint)[2]), reflect(ray.direction, intersect, norm), o.reflectivity

        return BACKGROUND, 0, 0

def calc_pixel (ray):
        r = 0
        out = (0,0,0)

        while r < MAX_RECURSIONS:

                c, ray, reflectivity = trace(ray)
                #reflectivity = 1
                c = (c[0]/255.0, c[1]/255.0, c[2]/255.0)

                #out = ( (out[0]*(1-reflectivity))+(c[0]*reflectivity),
                #        (out[1]*(1-reflectivity))+(c[1]*reflectivity),
                #        (out[2]*(1-reflectivity))+(c[2]*reflectivity))

                out = ( (out[0]+c[0]),
                        (out[1]+c[1]),
                        (out[2]+c[2]))

                r += 1
                if ray == 0:
                        break

        out = (out[0]*255/MAX_RECURSIONS, out[1]*255/MAX_RECURSIONS, out[2]*255/MAX_RECURSIONS)

        if r == 1:
                out = BACKGROUND

        return out, r
        
        

pygame.init()
screen = pygame.display.set_mode((int(WIDTH), int(HEIGHT)))

spheres = [ Sphere(30, 30, 200, 50,(255,0,0,), 0.5),
            Sphere(150, 30, 150, 50,(0,0,255), 0.5), 
            Sphere(100, 125, 100, 50,(0,255,0), 0.5),
            Sphere(100, 50, 250, 50,(128,128,128), 0.5)
          ]

planes =  [ Plane(100,150,0, 0,1,0, (255,255,255), 0.5)
          ]

light = Vector3(0, 0, 0)
done = False
totalRays = 0
i = 0

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