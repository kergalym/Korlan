
# Disable the "xxx has no yyy member" error, pylint seems to be unable to detect
# the properties of a nodepath
# pylint: disable=no-member

from __future__ import print_function

import os
import sys
import math
from random import random, randint, seed

from direct.actor.Actor import Actor
from panda3d.core import Vec3, load_prc_file_data, Texture
from direct.showbase.ShowBase import ShowBase


# Polyfill a set_shader_inputs function for older versions of Panda.
from panda3d.core import NodePath
from direct.extensions_native.extension_native_helpers import Dtool_funcToMethod

class MainApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Setup window size, title and so on
        load_prc_file_data("", """
            win-size 1600 900
            window-title Render Pipeline - Car Demo
        """)

        # ------ Begin of render pipeline code ------

        from Engine.Render.rpcore.render_pipeline import RenderPipeline
        import gltf

        self.render_pipeline = RenderPipeline()
        self.render_pipeline.pre_showbase_init()
        self.render_pipeline.create(self)

        from Engine.Render.rpcore import PointLight

        light = PointLight()
        light.pos = (0, 50, 10)
        light.color = (0.2, 0.6, 1.0)
        light.energy = 1000.0
        light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
        light.casts_shadows = True
        light.shadow_map_resolution = 512
        light.near_plane = 0.2
        self.render_pipeline.add_light(light)

        # This is a helper class for better camera movement - its not really
        # a rendering element, but it included for convenience

        # ------ End of render pipeline code, thats it! ------

        self.render_pipeline.daytime_mgr.time = "20:08"

        # Load the scene
        model = self.loader.loadModel("/home/galym/Korlan_blends/test/untitled.egg")
        # model = base.loader.loadModel("/home/galym/Korlan/Assets/Levels/Environment/Nomad house/Nomad_house.bam.egg")
        # model2 = base.loader.loadModel("/home/galym/Korlan_blends/Scenes/scene_one_nomad_house_1.egg")
        gltf.patch_loader(self.loader)
        model2 = self.loader.loadModel("/home/galym/Korlan_blends/test/untitled.bam")
        #model2 = Actor(model2)

        model.reparent_to(render)
        model.setTransparency(True)
        model.set_h(0)
        model.set_pos(0, 8, -1)
        model.set_two_sided(True)
        model2.reparent_to(render)
        model2.setTransparency(True)
        model2.set_pos(1, -8, -1)
        # model2.loop("LookingAround")

MainApp().run()

