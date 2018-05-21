import numpy as np
from materials import *
from objects import *
from vector import Vector3

FPS = 15
FRAMES = 120
DRAW_DISTANCE = 10000

light = Vector3(-140,-240,-140)

spheres = [ Sphere(Vector3(-140.0, -60.0, 160), 60.0, Solid((255,255, 255), (255,255,255)), 1.0, 1.0, 0.9),
            Sphere(Vector3(0.0, -100.0, 0.0), 40.0, Texture("earth.bmp"), 1.0, 1.0, 0.025)
          ]

planes =  [ Plane(Vector3(0.0, 0.0, 0.0), Vector3(0, -1.0, 0.0), Grid(), 0.5, 1.0, 0.2),
            Plane(Vector3(0.0, -250.0, 0.0), Vector3(0, 1.0, 0.0), Solid((200,200,200), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(-200.0, 0.0, 0.0), Vector3(1.0, 0.0, 0.0), Solid((170,20,20), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(200.0, 0.0, 0.0), Vector3(-1.0, 0.0, 0.0), Solid((30, 100, 220), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(0.0, 0.0, 200.0), Vector3(0.0, 0.0, -1.0), Solid((200,200,200), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(0.0, 0.0, -200.0), Vector3(0.0, 0.0, 1.0), Solid((200,200,200), (255,255,255)), 0.8, 0.3, 0.0)
          ]

def camera_position(frame):
    theta = frame * ((2.0*np.pi)/FRAMES)*2.0
    cameraPos = Vector3(150.0*np.sin(theta), -100.0, 150.0*-np.cos(theta))
    cameraRot = Vector3(0.0, theta, 0.0)
    return cameraPos, cameraRot