"""
Copyright (c) 2019 Galym Kerimbekov kegalym2@mail.ru

    This file is a part of Korlan The Game.
    PandaSteer is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.
    PandaSteer is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with PandaSteer; if not, write to the Free Software
    Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
"""

""" Temporary hacks or workarounds should be here """

from panda3d.core import TransparencyAttrib

""" Sets Apha blending mode if not by default """


def set_tex_transparency(node):
    if node and not str or int:
        node.setTransparency(True)
        node.setTransparency(TransparencyAttrib.MAlpha)


""" Gets a child of the node """


def get_child_node(node, child_num):
    if node and not str or int:
        child_node = node.get_child(child_num)
        return child_node


