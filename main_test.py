
# Disable the "xxx has no yyy member" error, pylint seems to be unable to detect
# the properties of a nodepath
# pylint: disable=no-member

from __future__ import print_function

import os
import sys
import math
from random import random, randint, seed

from direct.actor.Actor import Actor
from direct.task import Task
from panda3d.core import Vec3, load_prc_file_data, Texture, LVector3
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from direct.particles.ParticleEffect import ParticleEffect
from panda3d.core import Filename


class MainApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Setup window size, title and so on
        load_prc_file_data("", """
            win-size 1920 1080
            window-title Render Pipeline
        """)

        self.disableMouse()
        props = WindowProperties()
        props.setCursorHidden(True)
        self.win.requestProperties(props)
        self.camLens.setFov(60)

        # Set the current viewing target
        # self.focus = LVector3(55, -55, 20)
        self.focus = LVector3(0, 0, 0)
        self.heading = 180
        self.pitch = 0
        self.mousex = 0
        self.mousey = 0
        self.last = 0
        self.mousebtn = [0, 0, 0]

        # Start the camera control task:
        taskMgr.add(self.controlCamera, "camera-task")
        self.accept("escape", sys.exit, [0])
        self.accept("mouse1", self.setMouseBtn, [0, 1])
        self.accept("mouse1-up", self.setMouseBtn, [0, 0])
        self.accept("mouse2", self.setMouseBtn, [1, 1])
        self.accept("mouse2-up", self.setMouseBtn, [1, 0])
        self.accept("mouse3", self.setMouseBtn, [2, 1])
        self.accept("mouse3-up", self.setMouseBtn, [2, 0])
        self.accept("arrow_left", self.rotateCam, [-1])
        self.accept("arrow_right", self.rotateCam, [1])

        import gltf

        from Engine.Render.rpcore.render_pipeline import RenderPipeline

        self.render_pipeline = RenderPipeline()
        self.render_pipeline.pre_showbase_init()
        self.render_pipeline.create(self)

        from Engine.Render.rpcore import PointLight

        # This is a helper class for better camera movement - its not really
        # a rendering element, but it included for convenience

        # ------ End of render pipeline code, thats it! ------

        self.render_pipeline.daytime_mgr.time = "20:25"

        # Load the scene
        model = self.loader.loadModel("/home/galym/Korlan/Assets/Levels/Environment/Nomad house/Nomad_house.egg.bam")
        # model = base.loader.loadModel("/home/galym/Korlan/Assets/Levels/Environment/Nomad house/Nomad_house.bam.egg")
        # model2 = base.loader.loadModel("/home/galym/Korlan_blends/Scenes/scene_one_nomad_house_1.egg")
        gltf.patch_loader(self.loader)
        model2 = self.loader.loadModel("/home/galym/Korlan_blends/test/untitled.egg")
        model2.set_two_sided(True)
        # model2 = Actor(model2)

        model.reparent_to(render)
        model.setTransparency(True)
        model.set_h(0)
        model.set_pos(5, 8, 4)
        model.set_two_sided(True)
        model2.reparent_to(render)
        model2.setTransparency(True)
        model2.set_pos(5, -8, 5)
        model2.set_scale(6)
        # model2.loop("LookingAround")
        self.model = model

        light = PointLight()
        light.pos = (-3, 15, 5)
        light.color = (0.4, 0.4, 0.4)
        light.set_color_from_temperature(3000.0)
        light.energy = 100.0
        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
        light.casts_shadows = True
        light.shadow_map_resolution = 512
        light.near_plane = 0.2
        self.render_pipeline.add_light(light)

        # self.render_pipeline.prepare_scene(model2)

        base.enableParticles()
        self.t = self.loader.loadModel("teapot")
        self.t.setPos(0, 10, 0)
        self.t.reparentTo(render)
        self.p = ParticleEffect()
        self.p = ParticleEffect()
        self.loadParticleConfig('/home/galym/Korlan/particles/fireish.ptf')

    def loadParticleConfig(self, filename):
        # Start of the code from steam.ptf
        self.p.cleanup()
        self.p = ParticleEffect()
        self.p.loadConfig(Filename(filename))
        # Sets particles to birth relative to the teapot, but to render at
        # toplevel
        self.p.start(self.model)
        self.p.setPos(3.000, 0.000, 2.250)

    def setMouseBtn(self, btn, value):
        self.mousebtn[btn] = value

    def rotateCam(self, offset):
        self.heading = self.heading - offset * 10

    def controlCamera(self, task):
        # figure out how much the mouse has moved (in pixels)
        md = self.win.getPointer(0)
        x = md.getX()
        y = md.getY()
        if self.win.movePointer(0, 100, 100):
            self.heading = self.heading - (x - 100) * 0.2
            self.pitch = self.pitch - (y - 100) * 0.2
        if self.pitch < -45:
            self.pitch = -45
        if self.pitch > 45:
            self.pitch = 45
        self.camera.setHpr(self.heading, self.pitch, 0)
        dir = self.camera.getMat().getRow3(1)
        elapsed = task.time - self.last
        if self.last == 0:
            elapsed = 0
        if self.mousebtn[0]:
            self.focus = self.focus + dir * elapsed * 30
        if self.mousebtn[1] or self.mousebtn[2]:
            self.focus = self.focus - dir * elapsed * 30
        self.camera.setPos(self.focus - (dir * 5))
        if self.camera.getX() < -59.0:
            self.camera.setX(-59)
        if self.camera.getX() > 59.0:
            self.camera.setX(59)
        if self.camera.getY() < -59.0:
            self.camera.setY(-59)
        if self.camera.getY() > 59.0:
            self.camera.setY(59)
        if self.camera.getZ() < 5.0:
            self.camera.setZ(5)
        if self.camera.getZ() > 45.0:
            self.camera.setZ(45)
        self.focus = self.camera.getPos() + (dir * 5)
        self.last = task.time
        return Task.cont

MainApp().run()

