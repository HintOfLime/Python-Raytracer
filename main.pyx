#!/usr/bin/python
import pygame
import numpy as np
import time
import os
import shutil
import random
import multiprocessing as mp
from vector import *
from environment import *

cdef float AMBIENT = 0.05
cdef int WIDTH = 300
cdef int HEIGHT = 300
cdef int SCALE = 2
cdef int MAX_RECURSIONS = 2
cdef bint EXPORT_VIDEO = True
cdef int RENDERERS = 4
cdef int SHADOW_SAMPLES = 36
cdef int LIGHTING_SAMPLES = 16
cdef int GRID_SIZE = 500
cdef int GRID_SECTIONS = 1

def render(p, queue, output, grid):
        #print "Renderer " + str(p) + " started"
        while True:
                try:
                        data = queue.get(timeout=0.1)
                        x1 = data[0]
                        x2 = data[1]
                        y = data[2]
                        cameraPos = data[3]
                        cameraRot = data[4]
                        out = [(0,0,0)]*int(x2-x1)
                        for x in range(x2-x1):
                                direction = normalize(rotate(normalize( Vector3(((float(x+x1) / float(WIDTH))-0.5)*200.0*0.012, ((float(y) / float(HEIGHT))-0.5)*200.0*.012, 1.0)), cameraRot))
                                r = Ray(cameraPos, direction)
                                c, rays = calc_pixel(r, grid)
                                out[x] = gamma_decode(c)
                        output.put((p, x1, x2, y, out, rays))
                except:
                        output.put((p, 0, 0, -1))
                        continue
        #print "Renderer " + str(p) + " done"

def get_first_intersect(ray, grid):
        cdef float distance = GRID_SIZE
        closest = 0

        obs = []
        for box in grid:
                if box[0].intersect(ray):
                        obs.extend(box[1])

        obs = list(set(obs))
        for o in obs:
                d = o.shape.intersect(ray)
                if d != False and d < distance:
                        closest = o
                        distance = d

        return closest, distance

def rotate(a, theta):
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


def reflect (incident, intersect, normal):
        incident = normalize(incident)
        normal = normalize(normal)

        direction = incident - scale(normal, 2*dot(normal,incident))

        origin = intersect + scale(direction, 0.001)
        return Ray(origin, direction)


def trace (ray, recursion_depth, grid):
        recursion_depth += 1
        o, d = get_first_intersect(ray, grid)      

        cdef int rays = 0

        for light in lights:
                if light.shape.intersect(ray) != False and light.shape.intersect(ray) <= d:
                        return (255,255,255), 1

        if type(o) == int:
                return (0, 0, 0), 1

        scaled = scale(normalize(ray.direction), d)
        intersect = ray.origin + scaled
        
        norm = o.shape.getNormal(intersect)

        if dot(ray.direction, norm) > 0.0:
                scale(norm, -1.0)

        cd, cs, b = o.getColor(o.shape.getSurfaceCoord(intersect))

        tangent, bitangent = o.shape.getTangentAxis(intersect)

        norm = normalize(norm + scale(tangent, ((b[0]/-255.0)+0.5)*1.0) + scale(bitangent , ((b[1]/-255.0)+0.5)*1.0))

        cdef float diffuse = 0.0
        cdef float specular = 0.0
        cdef int xySamples = int(np.sqrt(LIGHTING_SAMPLES))
        rays += xySamples
        for light in lights:
                for y in range(xySamples):
                        for x in range(xySamples):
                                x2 = (x/xySamples)
                                y2 = (y/xySamples)
                                x2 += (random.random()-0.5)/(xySamples)
                                y2 += (random.random()-0.5)/(xySamples)
                                diffuse += dot(normalize(light.shape.getWorldCoord(light.shape.center, (x2, y2)) - intersect), norm)
                                specular += dot(normalize(light.shape.getWorldCoord(light.shape.center, (x2, y2)) - intersect), normalize(reflect(ray.direction, intersect, norm).direction))
        diffuse = diffuse / (xySamples**2)
        specular = specular / (xySamples**2)

        if diffuse < 0.0:
                diffuse = 0.0
        if specular < 0.0:
                specular = 0.0
        specular = specular ** 4

        cdef float shadowIntensity = 0.0
        xySamples = int(np.sqrt(SHADOW_SAMPLES))
        rays += xySamples
        for light in lights:
                for y in range(xySamples):
                        for x in range(xySamples):
                                x2 = (x/xySamples)
                                y2 = (y/xySamples)
                                x2 += (random.random()-0.5)/(xySamples)
                                y2 += (random.random()-0.5)/(xySamples)
                                shadowRay = Ray(intersect+scale(norm, 0.001), normalize(light.shape.getWorldCoord(light.shape.center, (x2, y2)) - intersect))
                                a, d = get_first_intersect(shadowRay, grid)
                                if d < magnitude(light.shape.getWorldCoord(light.shape.center, (x2, y2)) - intersect):
                                        shadowIntensity += 1.0/(xySamples**2)

        color = ((((cd[0]*diffuse*o.kd)+(cs[0]*specular*o.ks))*(1.0-shadowIntensity))+(cd[0]*AMBIENT),
                        (((cd[1]*diffuse*o.kd)+(cs[1]*specular*o.ks))*(1.0-shadowIntensity))+(cd[1]*AMBIENT),
                        (((cd[2]*diffuse*o.kd)+(cs[2]*specular*o.ks))*(1.0-shadowIntensity))+(cd[2]*AMBIENT))

        if o.reflectivity > 0.0 and recursion_depth < MAX_RECURSIONS:
                reflection_color, r = trace( reflect(ray.direction, intersect, norm), recursion_depth, grid )
                rays += r
                color = ((color[0]*(1-o.reflectivity)) + (reflection_color[0]*o.reflectivity*(1.0-shadowIntensity+0.1)),
                                (color[1]*(1-o.reflectivity)) + (reflection_color[1]*o.reflectivity*(1.0-shadowIntensity+0.1)),
                                (color[2]*(1-o.reflectivity)) + (reflection_color[2]*o.reflectivity*(1.0-shadowIntensity+0.1)))
        else:
                color = (color[0]*(1.0-o.reflectivity),
                                color[1]*(1.0-o.reflectivity),
                                color[2]*(1.0-o.reflectivity))

        color = (np.clip(color[0], 0, 255),
                        np.clip(color[1], 0, 255),
                        np.clip(color[2], 0, 255))

        return color, rays

def calc_pixel (ray, grid):
        cdef int recursion_depth = 0
        out, rays = trace(ray, recursion_depth, grid)
        return out, rays

def build_grid():
        grid = []
        for x in range(GRID_SECTIONS):
                for y in range(GRID_SECTIONS):
                        for z in range(GRID_SECTIONS):
                                size = float(GRID_SIZE)/float(GRID_SECTIONS)
                                aabb = AABB(Vector3(((x-(GRID_SECTIONS/2.0)+0.5)*size)+0.01, ((y-(GRID_SECTIONS/2.0)+0.5)*size)+0.01, ((z-(GRID_SECTIONS/2.0)+0.5)*size)+0.01), Vector3(size, size, size))
                                contains = []
                                #contains.append(Object(Sphere(Vector3((x-(GRID_SECTIONS/2.0)+0.5)*size, (y-(GRID_SECTIONS/2.0)+0.5)*size, (z-(GRID_SECTIONS/2.0)+0.5)*size), size/2.0), Solid((255,0,0),(0,0,0)),1,1,0))
                                for o in objects:
                                        if aabb.contains(o.shape.aabb):
                                                contains.append(o)
                                grid.append((aabb, contains))
        return grid

def main ():
        pygame.init()
        screen = pygame.display.set_mode((int(WIDTH*SCALE), int(HEIGHT*SCALE)))

        grid = build_grid()

        if EXPORT_VIDEO == True:
                if not os.path.exists("screenshots"):
                        os.makedirs("screenshots")

        processes = [0]*RENDERERS
        output = mp.Queue()
        queue = mp.Queue()

        p = 0
        while p < RENDERERS:
                processes[p] = mp.Process(target=render, args=(p, queue, output, grid))
                processes[p].daemon = True
                processes[p].start()
                p += 1

        done = False
        cdef int i = 0
        while not done:
                print "Frame " + str( int(i) )

                cameraPos, cameraRot = camera_position(i)

                start_time = time.time()

                for y in range(HEIGHT):
                        queue.put((0, WIDTH, y, cameraPos, cameraRot))

                rays = 0
                rendering = [True]*RENDERERS
                any_rendering = True
                while any_rendering:
                        for event in pygame.event.get():
                                if event.type == pygame.QUIT:
                                        done = True
                                        rendering = False
                        if done:
                                break

                        try:
                                result = output.get(timeout = 0.0)
                                y = result[3]
                                if y < 0:
                                        rendering[result[0]] = False
                                        any_rendering = True in rendering
                                for x in range(WIDTH):
                                        screenX = x#+(result[0]*(WIDTH/RENDERERS))
                                        for y2 in range(SCALE):
                                                for x2 in range(SCALE):
                                                        screen.set_at((int((screenX*SCALE)+x2), int((y*SCALE)+y2)), result[4][x])
                                rays += result[3]
                                
                        except:
                                pygame.display.flip()
                                pass

                time_elapsed = time.time() - start_time
                fps = 1.0 / time_elapsed
                print str( round(time_elapsed/60, 2)) + " minutes"
                print str( round(fps, 2) ) + " FPS"
                print str( rays ) + " Rays"
                print str( round(time_elapsed*(FRAMES-i-1)/60.0, 2) ) + " minutes remaining"
                print ""

                if EXPORT_VIDEO == True:
                        pygame.image.save(screen, "screenshots/screenshot_" + str("%06d" % int(i)) + ".bmp")

                i += 1
                if i > FRAMES-1:
                        break

        for p in processes:
                p.terminate()

        pygame.quit()

        if EXPORT_VIDEO == True:
                os.system("ffmpeg -r " + str(FPS) + " -i screenshots/screenshot_%06d.bmp -vcodec libx264 -y movie.mp4")
                shutil.rmtree("screenshots")

if __name__ == "__main__":
        main()
