from __future__ import print_function

from direct.actor.Actor import Actor
from direct.filter.CommonFilters import CommonFilters
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AIWorld, AICharacter
from panda3d.core import Vec3, load_prc_file_data, Material, Texture, TransparencyAttrib, Point3, NodePath
from direct.showbase.ShowBase import ShowBase
from direct.stdpy import threading
from code import InteractiveConsole
from panda3d.core import *
import random
from pathlib import Path


class MainApp(ShowBase):

    def __init__(self):
        # Setup window size and title
        super().__init__()
        load_prc_file_data("", """
        win-size 1920 1080
        window-title Render Pipeline - Asset Testing Scene
        """)

        # Import the movement controller, this is a convenience class
        # to provide an improved camera control compared to Panda3Ds default
        # mouse controller.
        from Engine.Render.rpcore.util.movement_controller import MovementController

        # ------ End of render pipeline code, thats it! ------

        # Set time of day

        """ic_thread = threading.Thread(target=InteractiveConsole(globals()).interact)
        ic_thread.start()"""

        self.game_dir = str(Path.cwd())

        # Load the scene
        self.model = self.loader.load_model("/home/galym/Korlan/Assets/Levels/lvl_one.egg.bam", noCache=True)
        # self.model.set_two_sided(True)
        self.model.reparent_to(self.render)

        self.actor = self.loader.load_model('/home/galym/Korlan/Assets/Actors/Korlan/Korlan.egg', noCache=True)
        self.actor = Actor(self.actor,
                           {"walk": "/home/galym/Korlan/Assets/Animations/Korlan-Walking.egg",
                            "idle": "/home/galym/Korlan/Assets/Animations/Korlan-LookingAround.egg"})

        self.actor.set_pos(-5, -10, 0)
        # self.actor.setTransparency(TransparencyAttrib.MDual, 1)
        self.actor.set_scale(1.25)
        self.actor.reparent_to(self.render)
        # self.actor.set_two_sided(True)

        self.actor2 = self.loader.load_model('/home/galym/Korlan/Assets/Actors/Korlan/Korlan.egg', noCache=True)
        self.actor2 = Actor(self.actor2,
                            {"walk": "/home/galym/Korlan/Assets/Animations/Korlan-Walking.egg",
                             "idle": "/home/galym/Korlan/Assets/Animations/Korlan-LookingAround.egg"})

        self.actor2.set_pos(0, 10.5, 0)
        # self.actor.setTransparency(TransparencyAttrib.MDual, 1)
        self.actor2.set_scale(1.25)
        self.actor2.reparent_to(self.render)

        self.actor3 = self.loader.load_model('/home/galym/Korlan/Assets/Actors/Korlan/Korlan.egg', noCache=True)
        self.actor3 = Actor(self.actor3,
                            {"walk": "/home/galym/Korlan/Assets/Animations/Korlan-Walking.egg",
                             "idle": "/home/galym/Korlan/Assets/Animations/Korlan-LookingAround.egg"})

        self.actor3.set_pos(0, 20.5, 0)
        # self.actor.setTransparency(TransparencyAttrib.MDual, 1)
        self.actor3.set_scale(1.25)
        self.actor3.reparent_to(self.render)

        self.actor4 = self.loader.load_model('/home/galym/Korlan/Assets/Actors/Korlan/Korlan.egg', noCache=True)
        self.actor4 = Actor(self.actor4,
                            {"walk": "/home/galym/Korlan/Assets/Animations/Korlan-Walking.egg",
                             "idle": "/home/galym/Korlan/Assets/Animations/Korlan-LookingAround.egg"})

        self.actor4.set_pos(0, 30.5, 0)
        # self.actor.setTransparency(TransparencyAttrib.MDual, 1)
        self.actor4.set_scale(1.25)
        self.actor4.reparent_to(self.render)

        self.actor5 = self.loader.load_model('/tmp/Korlan.egg', noCache=True)
        self.actor5 = Actor(self.actor5,
                            {"walk": "/tmp/untitled-Walking.egg",
                             "attack": "/tmp/untitled-archer_standing_draw_arrow_2.egg"})
        self.actor5.set_pos(0, 0.5, 0)
        """self.actor5.setTransparency(TransparencyAttrib.MDual, 1)
        self.actor5.setTransparency(TransparencyAttrib.M_alpha, 1)
        self.actor5.setDepthWrite(True)"""
        self.actor5.set_h(233.0)
        self.actor5.reparent_to(self.render)
        self.actor5.set_two_sided(True)
        # self.actor5.set_scale(20)

        """self.render_pipeline.set_effect(render, "effects/alpha_testing.yaml", {
            "render_gbuffer": True,
            "render_shadow": True,
            "alpha_testing": True,
            "normal_mapping": True
            })

        self.render.set_shader_input("alpha_factor_operand", 1.0)"""

        """data1, data2 = self.actor.getTightBounds()
        width = data2.getX() - data1.getX()
        height = data2.getY() - data1.getY()

        print('width: ' + str(width), 'height: ' + str(height))"""

        if not render.find("**/flame").is_empty():
            # self.render_pipeline.reload_shaders()
            self.flame_np = render.find("**/flame")
            width = self.flame_np.getX()
            height = self.flame_np.getZ()
            flame_dimensions = LVecBase2(width, height)

        self.actor.loop("idle")
        self.actor2.loop("idle")
        self.actor3.loop("idle")
        self.actor4.loop("idle")
        # self.actor5.loop("attack")

        self.controller = MovementController(self)
        self.controller.set_initial_position_hpr(
            Vec3(-17.2912578583, -13.290019989, 6.88211250305),
            Vec3(-39.7285499573, -14.6770210266, 0.0))
        self.controller.setup()

        self.AIworld = AIWorld(self.render)

        self.AIchar = []
        self.AIbehaviors = []
        self.Actors = []

        self.Actors.append(self.actor)
        self.Actors.append(self.actor2)
        self.Actors.append(self.actor3)
        self.Actors.append(self.actor4)

        self.AIchar.append(AICharacter("korlan", self.actor, 60, 0.05, 25 - (5 * random.random())))
        self.AIchar.append(AICharacter("korlan", self.actor2, 60, 0.05, 25 - (5 * random.random())))
        self.AIchar.append(AICharacter("korlan", self.actor3, 60, 0.05, 25 - (5 * random.random())))
        self.AIchar.append(AICharacter("korlan", self.actor4, 60, 0.05, 25 - (5 * random.random())))

        self.AIworld.addAiChar(self.AIchar[0])
        self.AIworld.addAiChar(self.AIchar[1])
        self.AIworld.addAiChar(self.AIchar[2])
        self.AIworld.addAiChar(self.AIchar[3])

        self.AIbehaviors.append(self.AIchar[0].getAiBehaviors())
        self.AIbehaviors.append(self.AIchar[1].getAiBehaviors())
        self.AIbehaviors.append(self.AIchar[2].getAiBehaviors())
        self.AIbehaviors.append(self.AIchar[3].getAiBehaviors())

        self.AIbehaviors[0].initPathFind("/home/galym/Korlan/Assets/NavMeshes/lvl_one.csv")
        self.AIbehaviors[1].initPathFind("/home/galym/Korlan/Assets/NavMeshes/lvl_one.csv")
        self.AIbehaviors[2].initPathFind("/home/galym/Korlan/Assets/NavMeshes/lvl_one.csv")
        self.AIbehaviors[3].initPathFind("/home/galym/Korlan/Assets/NavMeshes/lvl_one.csv")

        self.AIbehaviors[0].pathFindTo(self.actor2.get_pos(), "addPath")
        self.AIbehaviors[1].pathFindTo(self.actor4.get_pos(), "addPath")
        self.AIbehaviors[2].pathFindTo(self.actor.get_pos(), "addPath")
        self.AIbehaviors[3].pathFindTo(self.actor3.get_pos(), "addPath")

        self.AIbehaviors[0].addDynamicObstacle(self.actor2)
        self.AIbehaviors[1].addDynamicObstacle(self.actor3)

        self.AIbehaviors[2].addDynamicObstacle(self.actor)
        self.AIbehaviors[3].addDynamicObstacle(self.actor4)

        # render.explore()

        # AI World update
        taskMgr.add(self.AIUpdate, "AIUpdate")

        self.done = []
        for i in range(4):
            self.done.append(False)

        light = Spotlight('s')
        light_np = self.render.attach_new_node(light)
        # This light is facing backwards, towards the camera.
        # light_np.set_hpr(hpr[0], hpr[1], hpr[2])
        light_np.set_pos(-3, 8, 2)
        light_np.set_scale(100)
        self.render.set_light(light_np)

        filters = CommonFilters(base.win, base.cam)
        # filters.setAmbientOcclusion()


    def AIUpdate(self, task):
        # self.AIworld.update()
        # self.setMove(2)

        return task.cont

    def setMove(self, type):
        if type == 1:
            for i in range(4):
                if (i == 0):
                    self.AIbehaviors[i].pathFindTo(self.Actors[1].get_pos(), "addPath")
                    self.AIbehaviors[0].addDynamicObstacle(self.Actors[2])
                if (i == 1):
                    self.AIbehaviors[i].pathFindTo(self.Actors[3].get_pos(), "addPath")
                    self.AIbehaviors[0].addDynamicObstacle(self.Actors[3])

                if (i == 2):
                    self.AIbehaviors[i].pathFindTo(self.Actors[0].get_pos(), "addPath")
                if (i == 3):
                    self.AIbehaviors[i].pathFindTo(self.Actors[2].get_pos(), "addPath")

        if type == 2:
            for i in range(4):
                if (i == 0):
                    self.AIbehaviors[i].pathFindTo(self.Actors[1].get_pos(), "addPath")
                if (i == 1):
                    self.AIbehaviors[i].pathFindTo(self.Actors[3].get_pos(), "addPath")
                if (i == 2):
                    self.AIbehaviors[i].pathFindTo(self.Actors[0].get_pos(), "addPath")
                if (i == 3):
                    self.AIbehaviors[i].pathFindTo(self.Actors[2].get_pos(), "addPath")
                # self.Actors[i].play("walk")


main = MainApp()
main.run()
