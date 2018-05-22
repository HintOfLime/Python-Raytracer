import pygame
import numpy as np
import time
import os
import shutil
import multiprocessing as mp
from vector import *
from environment import *

WIDTH = 800
HEIGHT = 800
SCALE = 1
MAX_RECURSIONS = 3
EXPORT_VIDEO = True
RENDERERS = 2

def render(p, x1, y1, x2, y2, cameraPos, cameraRot, output):
        #print "Renderer " + str(p) + " started"
        out = [[(0,0,0)]*int(x2-x1) for n in range(int(y2-y1))]
        for y in range(y2-y1):
                for x in range(x2-x1):
                        direction = normalize(rotate(normalize( Vector3(((float(x+x1) / float(WIDTH))-0.5)*200.0*0.012, ((float(y+y1) / float(HEIGHT))-0.5)*200.0*.012, 1.0)), cameraRot))
                        r = Ray(cameraPos, direction)
                        c, rays = calc_pixel(r)
                        out[y][x] = gamma_decode(c)

        #print "Renderer " + str(p) + " done"
        output.put((p, out))

class Ray:
        def __init__ (self, origin, direction):
                self.origin = origin
                self.direction = direction

def rotate(a, theta) :
        matrix_x = np.matrix([[1,                  0,                   0               ],
                             [0,                  np.cos(theta.x),    -np.sin(theta.x) ],
                             [0,                  np.sin(theta.x),     np.cos(theta.x) ]])

        matrix_y = np.matrix([[np.cos(theta.y),    0,                   np.sin(theta.y) ],
                             [0,                  1,                   0               ],
                             [-np.sin(theta.y),   0,                   np.cos(theta.y) ]])

        matrix_z = np.matrix([[np.cos(theta.z),    -np.sin(theta.z),    0               ],
                             [np.sin(theta.z),    np.cos(theta.z),     0               ],
                             [0,                  0,                   1               ]])
        a = normalize(a)
        matrix = np.dot(matrix_z, np.dot(matrix_x, matrix_y))
        a = np.matrix([a.x, a.y, a.z])
        b = a * matrix
        b = Vector3(b[0,0], b[0,1], b[0,2])

        return b

def get_first_intersect(ray):
        distance = DRAW_DISTANCE
        closest = 0
        for s in spheres:
                A = dot(ray.direction, ray.direction)
                dist = ray.origin - s.center
                B = 2.0 * dot(ray.direction, dist)
                C = dot(dist, dist) - (s.radius*s.radius)
                discr = (B*B) - (4*A*C)
                
                if discr <= 0.0:
                        continue

                t0 = (-B - np.sqrt(discr))/(2*A)
                t1 = (-B + np.sqrt(discr))/(2*A)

                if t0 < 0.0 and t1 < 0.0:
                        continue
                elif t0 < 0.0:
                        d = t1
                elif t1 < 0.0:
                        d = t0
                else:
                        d = min(t0, t1)
                
                               
                if d < distance:
                        closest = s
                        distance = d
                
                       
        for p in planes:
                denom = dot(p.normal, ray.direction)
                if denom > -0.000001 and denom < 0.000001:
                        continue
                
                        
                v = p.center - ray.origin
                d = dot(v, p.normal) / denom

                if d < 0.0:
                        continue

                if d < distance:
                        closest = p
                        distance = d

        return closest, distance

def reflect (incident, intersect, normal):
        incident = normalize(incident)
        normal = normalize(normal)

        direction = incident - scale(normal, 2*dot(normal,incident))

        origin = intersect + scale(direction, 0.001)
        return Ray(origin, direction)



def trace (ray, reursion_depth):
        o, d = get_first_intersect(ray)        
        if type(o) != int:
                reursion_depth += 1

                scaled = scale(normalize(ray.direction), d)
                intersect = ray.origin + scaled
                
                norm = o.getNormal(intersect)

                if dot(ray.direction, norm) > 0.0:
                        scale(norm, -1.0)

                cd, cs, b = o.getColor(o.getCoord(intersect))

                tangent = normalize(cross(Vector3(0.0,1.0,0.0), norm))
                bitangent  = normalize(cross(norm, tangent))

                norm = normalize(norm + scale(tangent, (b[0]/-255.0)+0.5) + scale(bitangent , (b[1]/-255.0)+0.5))

                diffuse = dot(normalize(light-intersect), norm)
                specular = dot(normalize(light-intersect), normalize(reflect(ray.direction, intersect, norm).direction))
                ambient = 0.1

                if diffuse < 0.0:
                        diffuse = 0.0
                if specular < 0.0:
                        specular = 0.0

                shadowRay = Ray(intersect+scale(norm, 0.001), normalize(light-intersect))
                a, d = get_first_intersect(shadowRay)
                if d < magnitude(light-intersect):
                        diffuse = 0.0
                        specular = 0.0
                specular = specular ** 4

                color = ((cd[0]*diffuse*o.kd)+(cs[0]*specular*o.ks)+(cd[0]*ambient),
                         (cd[1]*diffuse*o.kd)+(cs[1]*specular*o.ks)+(cd[1]*ambient),
                         (cd[2]*diffuse*o.kd)+(cs[2]*specular*o.ks)+(cd[2]*ambient))

                if o.reflectivity > 0.0 and reursion_depth < MAX_RECURSIONS:
                        reflection_color = trace( reflect(ray.direction, intersect, norm), reursion_depth )
                        color = ((color[0]*(1-o.reflectivity)) + (reflection_color[0]*o.reflectivity),
                                        (color[1]*(1-o.reflectivity)) + (reflection_color[1]*o.reflectivity),
                                        (color[2]*(1-o.reflectivity)) + (reflection_color[2]*o.reflectivity))
                else:
                        color = (color[0]*(1.0-o.reflectivity),
                                        color[1]*(1.0-o.reflectivity),
                                        color[2]*(1.0-o.reflectivity))

                color = (np.clip(color[0], 0, 255),
                                np.clip(color[1], 0, 255),
                                np.clip(color[2], 0, 255))

                return color

        return (0, 0, 0)

def calc_pixel (ray):
        recursion_depth = 0
        out = trace(ray, recursion_depth)
        return out, recursion_depth

if __name__ == '__main__':
        pygame.init()
        screen = pygame.display.set_mode((int(WIDTH*SCALE), int(HEIGHT*SCALE)))

        done = False
        i = 0

        if not os.path.exists("screenshots"):
                os.makedirs("screenshots")

        while not done:
                print "Frame " + str( int(i) )

                cameraPos, cameraRot = camera_position(i)

                processes = [0]*RENDERERS
                output = mp.Queue()

                start_time = time.time()

                if done:
                        break

                if RENDERERS > 1:
                        p = 0
                        while p < RENDERERS:
                                x1 = p*(WIDTH/RENDERERS)
                                y1 = 0
                                processes[p] = mp.Process(target=render, args=(p, x1, y1, x1+(WIDTH/RENDERERS), HEIGHT, cameraPos, cameraRot, output,))
                                processes[p].start()
                                p += 1

                        p = 0
                        while p < RENDERERS:
                                for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                                done = True
                                if done:
                                                break
                                processes[p].join(timeout=0.0)
                                result = output.get()

                                for y in range(HEIGHT):
                                        for x in range(WIDTH/RENDERERS):
                                                screenX = x+(result[0]*(WIDTH/RENDERERS))
                                                for y2 in range(SCALE):
                                                        for x2 in range(SCALE):
                                                                screen.set_at((int((screenX*SCALE)+x2), int((y*SCALE)+y2)), result[1][y][x])
                                       
                                pygame.display.flip()
                                p += 1
                else:
                        for y in range(HEIGHT):
                                for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                                done = True
                                if done:
                                                break

                                for x in range(WIDTH):
                                        direction = normalize(rotate(normalize( Vector3(((float(x) / float(WIDTH))-0.5)*200.0*0.012, ((float(y) / float(HEIGHT))-0.5)*200.0*.012, 1.0)), cameraRot))
                                        r = Ray(cameraPos, direction)
                                        c, rays = calc_pixel(r)
                                        for y2 in range(SCALE):
                                                        for x2 in range(SCALE):
                                                                screen.set_at((int((x*SCALE)+x2), int((y*SCALE)+y2)), gamma_decode(c))
                                pygame.display.flip()

                time_elapsed = time.time() - start_time
                fps = 1.0 / time_elapsed
                print str( round(fps, 2) ) + " FPS"
                print str( round(time_elapsed*(FRAMES-i-1)/60.0, 2) ) + " minutes remaining"

                if EXPORT_VIDEO == True:
                        pygame.image.save(screen, "screenshots/screenshot_" + str("%06d" % int(i)) + ".bmp")
                else:
                        while True:
                                for event in pygame.event.get():
                                        if event.type == pygame.QUIT:
                                                done = True
                                if done:
                                        break

                i += 1
                if i > FRAMES-1:
                        break


        if EXPORT_VIDEO == True:
                os.system("ffmpeg -r " + str(FPS) + " -i screenshots/screenshot_%06d.bmp -vcodec libx264 -y movie.mp4")
                shutil.rmtree("screenshots")