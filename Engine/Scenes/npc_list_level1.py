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

LEVEL_NPC_AXIS = {names[0]: [-32.542572021484375, -35.960758209228516, 0.002476423978805542],
                  names[1]: [-25.542572021484375, -25.960758209228516, 0.002476423978805542],
                  names[2]: [-12.542572021484375, -15.960758209228516, 0.002476423978805542],
                  names[3]: [-32.542572021484375, 0.0, 0.002476423978805542],
                  names[4]: [-10.542572021484375, 3.0, 0.002476423978805542],
                  names[5]: [-0.542572021484375, 6.0, 0.002476423978805542],
                  names[6]: [5.542572021484375, 0.0, 0.002476423978805542]
                  }
