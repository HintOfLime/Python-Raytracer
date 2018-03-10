import pygame
import numpy as np
import time

WIDTH = 300.0
HEIGHT = 300.0
BACKGROUND = (16, 16, 16)
MAX_RECURSIONS = 2
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
        def __init__ (self, x, y, z, r, c):
                self.center = Vector3(x, y, z)
                self.radius = r
                self.color = c

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
                       

        return closest, distance

def reflect (incident, intersect, normal):
        origin = intersect
        direction = incident - scale(normal, -2*dot(incident, normal))
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

                        shade = (dot(normalize(light-intersect), norm))**3

                        shadowRay = Ray(intersect, light-intersect)
                        a, b = get_first_intersect(shadowRay)
                        #if a != 0:
                        #        shade = 0

                        if shade < 0.01:
                                shade = 0.01
                        elif shade > 1:
                                shade = 1


                        return (o.color[0]*shade, o.color[1]*shade, o.color[2]*shade), reflect(ray.direction, intersect, norm)
                        #return (o.color[0]*shade, o.color[1]*shade, o.color[2]*shade), 0

        return BACKGROUND, 0

def calc_pixel (ray):
        r = 0
        color = (0,0,0)
        while r < MAX_RECURSIONS:
                c, ray = trace(ray)
                r += 1
                color = (color[0]+c[0], color[1]+c[1], color[2]+c[2])
                if ray == 0:
                        break

        color = (color[0]/MAX_RECURSIONS, color[1]/MAX_RECURSIONS, color[2]/MAX_RECURSIONS)

        return color
        
        

pygame.init()
screen = pygame.display.set_mode((int(WIDTH), int(HEIGHT)))

spheres = [ Sphere(30, 30, 200, 50,(255,0,0)),
            Sphere(150, 30, 150, 50,(0,0,255)), 
            Sphere(100, 130, 100, 50,(0,255,0)),
            Sphere(100, 60, 250, 50,(200,200,200))
          ]

light = Vector3(0, 0, 0)

done = False
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
                        r.origin = Vector3(100, 100, 0)
                        r.direction = normalize(Vector3(((screenX/WIDTH)-0.5)*200*0.01, ((screenY/HEIGHT)-0.5)*200*0.01, 1))
                        screen.set_at((int(screenX), int(screenY)), calc_pixel(r))
                        screenX += 1

                if done:
                         break

                screenX = 0
                screenY += 1
                pygame.display.flip()
        i += 1