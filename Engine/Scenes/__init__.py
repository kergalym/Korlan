from Engine.Actors.NPC.npc_ernar import NpcErnar
from Engine.Actors.NPC.npc_mongol import NpcMongol
from Engine.Actors.NPC.npc_mongol2 import NpcMongol2

from Engine.FSM.npc_ernar_fsm import NpcErnarFSM
from Engine.FSM.npc_mongol_fsm import NpcMongolFSM
from Engine.FSM.npc_mongol2_fsm import NpcMongol2FSM

py_npc_actor_classes = [
    NpcErnar,
    NpcMongol,
    NpcMongol2
]

py_npc_fsm_classes = [
    NpcErnarFSM,
    NpcMongolFSM,
    NpcMongol2FSM
]

# List used by loading screen

level_npc_assets = {'name': ['NPC_Ernar', 'NPC_Mongol', 'NPC_Mongol2'],
                    'type': ['npc', 'npc', 'npc'],
                    'shape': ['capsule', 'capsule', 'capsule'],
                    'class': ['friend', 'enemy', 'enemy']
                    }

level_npc_axis = {'NPC_Ernar': [-15.0, 15.0, 0],
                  'NPC_Mongol': [-25.0, 25.0, 0],
                  'NPC_Mongol2': [-35.0, 35.0, 0]
                  }


"""
level_npc_assets = {'name': [],
                    'type': [],
                    'shape': [],
                    'class': []
                    }
level_npc_axis = {}
"""