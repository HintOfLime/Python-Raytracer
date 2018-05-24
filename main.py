import pygame
import numpy as np
import time
import os
import shutil
import random
import multiprocessing as mp
from vector import *
from environment import *

WIDTH = 300
HEIGHT = 300
SCALE = 1
MAX_RECURSIONS = 3
EXPORT_VIDEO = True
RENDERERS = 4

def render(p, x1, y1, x2, y2, cameraPos, cameraRot, output):
        #print "Renderer " + str(p) + " started"
        out = [[(0,0,0)]*int(x2-x1) for n in range(int(y2-y1))]
        for y in range(y2-y1):
                for x in range(x2-x1):
                        start_time = time.time()
                        direction = normalize(rotate(normalize( Vector3(((float(x+x1) / float(WIDTH))-0.5)*200.0*0.012, ((float(y+y1) / float(HEIGHT))-0.5)*200.0*.012, 1.0)), cameraRot))
                        r = Ray(cameraPos, direction)
                        c, rays = calc_pixel(r)
                        output.put((p, x, y, gamma_decode(c), rays, time.time()-start_time))

        #print "Renderer " + str(p) + " done"

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
        # This is main cause of slowdown,
        # called >50 times per pixel
        # Some sort of spatial subdivisioning?

        distance = DRAW_DISTANCE
        closest = 0
                       
        for o in objects:
                d = o.shape.intersect(ray)
                if d != False and d < distance:
                        closest = o
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

        for light in lights:
                if light.shape.intersect(ray) != False and light.shape.intersect(ray) <= d:
                        return (255,255,255)

        if type(o) != int:
                reursion_depth += 1

                scaled = scale(normalize(ray.direction), d)
                intersect = ray.origin + scaled
                
                norm = o.shape.getNormal(intersect)

                if dot(ray.direction, norm) > 0.0:
                        scale(norm, -1.0)

                cd, cs, b = o.getColor(o.shape.getSurfaceCoord(intersect))

                tangent, bitangent = o.shape.getTangentAxis(intersect)

                norm = normalize(norm + scale(tangent, ((b[0]/255.0)-0.5)*1.0) + scale(bitangent , ((b[1]/255.0)-0.5)*1.0))

                diffuse = 0.0
                specular = 0.0
                for light in lights:
                        for y in range(3):
                                for x in range(3):
                                        diffuse += dot(normalize(light.shape.getWorldCoord(light.shape.center, (x/2.0, y/2.0)) - intersect), norm)
                                        specular += dot(normalize(light.shape.getWorldCoord(light.shape.center, (x/2.0, y/2.0)) - intersect), normalize(reflect(ray.direction, intersect, norm).direction))
                diffuse = diffuse / 9.0
                specular = specular / 9.0
                ambient = 0.1

                if diffuse < 0.0:
                        diffuse = 0.0
                if specular < 0.0:
                        specular = 0.0
                specular = specular ** 4

                shadowIntensity = 0.0
                for light in lights:
                        for y in range(3):
                                for x in range(3):
                                        shadowRay = Ray(intersect+scale(norm, 0.001), normalize(light.shape.getWorldCoord(light.shape.center, ((x/3.0)+(random.random()/3.0), (y/3.0)+(random.random()/3.0))) - intersect))
                                        a, d = get_first_intersect(shadowRay)
                                        if d < magnitude(light.shape.center-intersect)+5:
                                                shadowIntensity += (1.0/9.0)
                diffuse = (1.0-shadowIntensity) * diffuse
                specular = (1.0-shadowIntensity) * specular

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
        # Need to output actual number of rays cast including shadows etc
        return out, recursion_depth+1

def main ():
        pygame.init()
        screen = pygame.display.set_mode((int(WIDTH*SCALE), int(HEIGHT*SCALE)))
        
        if EXPORT_VIDEO == True:
                if not os.path.exists("screenshots"):
                        os.makedirs("screenshots")

        done = False
        i = 0

        while not done:
                print "Frame " + str( int(i) )

                cameraPos, cameraRot = camera_position(i)

                processes = [0]*RENDERERS
                output = mp.Queue()

                start_time = time.time()

                if done:
                        break

                p = 0
                while p < RENDERERS:
                        x1 = p*(WIDTH/RENDERERS)
                        y1 = 0
                        processes[p] = mp.Process(target=render, args=(p, x1, y1, x1+(WIDTH/RENDERERS), HEIGHT, cameraPos, cameraRot, output,))
                        processes[p].daemon = True
                        processes[p].start()
                        p += 1

                rays = 0
                rendering = True
                while rendering:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        done = True
                                        rendering = False
                                if done:
                                        for p in processes:
                                                p.terminate()
                                                break

                        alive = 0
                        for p in processes:
                                p.join(timeout=0.0)
                                if p.is_alive():
                                        alive += 1
                        if alive == 0:
                                rendering = False

                        try:
                                result = output.get(timeout = 0.0)
                                x = result[1]
                                y = result[2]
                                screenX = x+(result[0]*(WIDTH/RENDERERS))
                                for y2 in range(SCALE):
                                        for x2 in range(SCALE):
                                                screen.set_at((int((screenX*SCALE)+x2), int((y*SCALE)+y2)), result[3])
                                rays += result[4]
                                rps = result[4]/result[5]
                                #print str(round(rps, 1)) + " RPS"
                        except:
                                pygame.display.flip()
                                pass

                time_elapsed = time.time() - start_time
                fps = 1.0 / time_elapsed
                print str( round(fps, 2) ) + " FPS"
                print str( rays ) + " Rays"
                print str( round(time_elapsed*(FRAMES-i-1)/60.0, 2) ) + " minutes remaining"

                if EXPORT_VIDEO == True:
                        pygame.image.save(screen, "screenshots/screenshot_" + str("%06d" % int(i)) + ".bmp")

                i += 1
                if i > FRAMES-1:
                        break

        if EXPORT_VIDEO == True:
                os.system("ffmpeg -r " + str(FPS) + " -i screenshots/screenshot_%06d.bmp -vcodec libx264 -y movie.mp4")
                shutil.rmtree("screenshots")

if __name__ == "__main__":
        main()
