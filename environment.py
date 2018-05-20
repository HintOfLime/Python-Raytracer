import numpy as np
from materials import *
from objects import *
from vector import Vector3

FPS = 30
FRAMES = 240
DRAW_DISTANCE = 10000

light = Vector3(0,-190,0)

spheres = [ Sphere(Vector3(40.0, 120.0, 0.0), 80.0, Solid((255,255, 255), (255,255,255)), 1.0, 0.5, 0.9),
            Sphere(Vector3(-70.0, 150.0, 50), 50.0, Solid((255,0,0), (255,255,255)), 1.0, 0.5, 0.15),
            Sphere(Vector3(-35.0, 170.0, -75), 30.0, Solid((0,255,0), (255,255,255)), 1.0, 0.5, 0.15),
            Sphere(Vector3(-80.0, 160.0, -30), 40.0, Grid(), 1.0, 0.5, 0.1)
          ]

planes =  [ Plane(Vector3(0.0, 200.0, 0.0), Vector3(0, -1.0, 0.0), Grid(), 0.5, 0.5, 0.1),
            Plane(Vector3(0.0, -200.0, 0.0), Vector3(0, 1.0, 0.0), Solid((255,255,255), (255,255,255)), 1.0, 0.5, 0.0),
            Plane(Vector3(-200.0, 0.0, 0.0), Vector3(1.0, 0.0, 0.0), Solid((255,50,50), (255,255,255)), 1.0, 0.5, 0.05),
            Plane(Vector3(200.0, 0.0, 0.0), Vector3(-1.0, 0.0, 0.0), Solid((0,0,255), (255,255,255)), 1.0, 0.5, 0.05),
            Plane(Vector3(0.0, 0.0, 200.0), Vector3(0.0, 0.0, -1.0), Solid((0,255,0), (255,255,255)), 1.0, 0.5, 0.05),
            Plane(Vector3(0.0, 0.0, -200.0), Vector3(0.0, 0.0, 1.0), Solid((0,255,255), (255,255,255)), 1.0, 0.5, 0.05)
          ]

def camera_position(frame):
    theta = frame * ((2.0*np.pi)/FRAMES)*2.0
    cameraPos = Vector3(190.0*np.sin(theta), (np.sin(theta/2.0)*-35.0)+45.0, 190.0*-np.cos(theta))
    cameraRot = Vector3((np.pi/180.0)*20.0 + (np.sin(theta/2.0)*(np.pi/180)*15.0), theta, 0.0)
    return cameraPos, cameraRot