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


