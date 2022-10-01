"""NPC list used to be populated at the game level"""

names = ['NPC_Ernar',
         'NPC_Mongol',
         'NPC_Mongol2',
         'NPC_Korlan_Horse',
         'NPC_Horse',
         'NPC_Horse2',
         'NPC_Horse3'
         ]

npc_ids = [1, 2, 3, 0, 1, 2, 3]

types = ['npc',
         'npc',
         'npc',
         'npc_animal',
         'npc_animal',
         'npc_animal',
         'npc_animal'
         ]

shapes = ['capsule',
          'capsule',
          'capsule',
          'capsule',
          'capsule',
          'capsule',
          'capsule'
          ]

classes = ['friend',
           'neutral',
           'enemy',
           'friend',
           'enemy',
           'enemy',
           'enemy'
           ]

LEVEL_NPC_ASSETS = {'name': names,
                    'type': types,
                    'shape': shapes,
                    'class': classes
                    }

LEVEL_NPC_AXIS = {names[0]: [-3.0, 17.0, 0],
                  names[1]: [-7.0, 20.0, 0],
                  names[2]: [-10.0, 27.0, 0],
                  names[3]: [-9.0, 5.0, 0],
                  names[4]: [9.0, 5.0, 0],
                  names[5]: [-10.0, 5.0, 0],
                  names[6]: [-12, 5.0, 0]
                  }
