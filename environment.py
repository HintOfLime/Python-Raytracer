import numpy as np
from materials import *
from objects import *
from vector import Vector3

FPS = 30
FRAMES = 240
DRAW_DISTANCE = 10000

light = Vector3(-140,-240,-140)

spheres = [ Sphere(Vector3(-140.0, -60.0, 160), 60.0, Texture("white.png", "rough.png"), 1.0, 1.0, 0.9),
            Sphere(Vector3(0.0, -100.0, 0.0), 50.0, Texture("earth.bmp", "rough.png"), 1.0, 0.5, 0.0)
          ]

planes =  [ Plane(Vector3(0.0, 0.0, 0.0), Vector3(0, -1.0, 0.0), 400, 400, Grid(20), 0.5, 0.3, 0.2),
            Plane(Vector3(0.0, -250.0, 0.0), Vector3(0, 1.0, 0.0), 400, 400, Solid((200,200,200), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(-200.0, -125.0, 0.0), Vector3(1.0, 0.0, 0.0), 250, 400, Solid((170,20,20), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(200.0, -125.0, 0.0), Vector3(-1.0, 0.0, 0.0), 250, 400, Solid((30, 100, 220), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(0.0, -125.0, 200.0), Vector3(0.0, 0.0, -1.0), 250, 400, Solid((200,200,200), (255,255,255)), 0.8, 0.3, 0.0),
            Plane(Vector3(0.0, -125.0, -200.0), Vector3(0.0, 0.0, 1.0), 250, 400, Solid((200,200,200), (255,255,255)), 0.8, 0.3, 0.0)
          ]

Cube(planes, Vector3(0.0, -15, 0.0), Vector3(70.0, 70.0, 70.0), Texture("white.png", "plate.jpg"), 0.7, 1.0, 0.3)

def camera_position(frame):
    theta = frame * ((2.0*np.pi)/FRAMES)
    cameraPos = Vector3(150.0*np.sin(theta), -100.0, 150.0*-np.cos(theta))
    cameraRot = Vector3(0.0, theta, 0.0)
    return cameraPos, cameraRot