import numpy as np
from materials import *
from objects import *
from vector import Vector3

FPS = 30
FRAMES = 240

lights = [ Light(Plane(Vector3(0.0, -149.0, 0.0), Vector3(0.0, 1.0, 0.0), Vector3(250, 0, 250)))
         ]

objects = [ Object(Sphere(Vector3(50.0, 40.0, -20.0), 60.0), Texture("white.png", "scratched.jpg"), 1.0, 1.0, 0.9),
            Object(Sphere(Vector3(-30.0, 50.0, 55.0), 50.0), Texture("earth.bmp", "rough.png"), 1.0, 0.5, 0.0),
            Object(Plane(Vector3(0.0, 100.0, 0.0), Vector3(0, -1.0, 0.0), Vector3(400, 0, 400)), Grid(20), 0.5, 0.3, 0.2)#,
            #Object(Plane(Vector3(0.0, -150.0, 0.0), Vector3(0, 1.0, 0.0), Vector3(400, 0, 400)), Solid((200,200,200), (255,255,255)), 0.8, 0.1, 0.0),
            #Object(Plane(Vector3(-200.0, -25.0, 0.0), Vector3(1.0, 0.0, 0.0), Vector3(0, 250, 400)), Solid((170,20,20), (255,255,255)), 0.8, 0.1, 0.0),
            #Object(Plane(Vector3(200.0, -25.0, 0.0), Vector3(-1.0, 0.0, 0.0), Vector3(0, 250, 400)), Solid((30, 100, 220), (255,255,255)), 0.8, 0.1, 0.0),
            #Object(Plane(Vector3(0.0, -25.0, 200.0), Vector3(0.0, 0.0, -1.0), Vector3(400, 250, 0)), Solid((200,200,200), (255,255,255)), 0.8, 0.1, 0.0),
            #Object(Plane(Vector3(0.0, -25.0, -200.0), Vector3(0.0, 0.0, 1.0), Vector3(400, 250, 0)), Solid((200,200,200), (255,255,255)), 0.8, 0.1, 0.0)
          ]

Cube(objects, Vector3(-45.0, 60.0, -30.0), Vector3(60.0, 60.0, 60.0), Texture("white.png", "plate.jpg"), 0.8, 1.0, 0.5)

def camera_position(frame):
    cdef float theta = frame * ((2.0*np.pi)/FRAMES)
    cameraPos = Vector3(150.0*np.sin(theta), 0.0, 150.0*-np.cos(theta))
    cameraRot = Vector3(0.0, theta, 0.0)
    #cameraRot = Vector3(np.pi/2, 0.0, 0.0)
    #cameraPos = Vector3(0.0, -140.0, 0.0)
    return cameraPos, cameraRot