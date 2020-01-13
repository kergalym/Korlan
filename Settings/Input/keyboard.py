"""
BSD 3-Clause License

Copyright (c) 2019, Galym Kerimbekov
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


class Keyboard:
    def __init__(self):
        self.base = base
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

        self.k_forward_lo = self.game_settings['Keymap']['forward'].lower()
        self.k_backward_lo = self.game_settings['Keymap']['backward'].lower()
        self.k_left_lo = self.game_settings['Keymap']['left'].lower()
        self.k_right_lo = self.game_settings['Keymap']['right'].lower()
        self.k_crouch_lo = self.game_settings['Keymap']['crouch'].lower()
        self.k_jump_lo = self.game_settings['Keymap']['jump'].lower()
        self.k_use_lo = self.game_settings['Keymap']['use'].lower()
        self.k_attack_lo = self.game_settings['Keymap']['attack'].lower()
        self.k_h_attack_lo = self.game_settings['Keymap']['h_attack'].lower()
        self.k_f_attack_lo = self.game_settings['Keymap']['f_attack'].lower()
        self.k_block_lo = self.game_settings['Keymap']['block'].lower()
        self.k_sword_lo = self.game_settings['Keymap']['sword'].lower()
        self.k_bow_lo = self.game_settings['Keymap']['bow'].lower()
        self.k_tengri_lo = self.game_settings['Keymap']['tengri'].lower()
        self.k_umai_lo = self.game_settings['Keymap']['umai'].lower()

        self.keymap = {
            'cam-left': 0,
            'cam-right': 0,
            'forward': 0,
            'backward': 0,
            'left': 0,
            'right': 0,
            'crouch': 0,
            'jump': 0,
            'use': 0,
            'attack': 0,
            'h_attack': 0,
            'f_attack': 0,
            'block': 0,
            'sword': 0,
            'bow': 0,
            'tengri': 0,
            'umai': 0
        }

    # Records the state of the arrow/actions keys
    def set_key(self, key, value):
        self.keymap[key] = value

    def kbd_init(self):
        # Accept the control keys for movement and rotation
        self.base.accept("arrow_left", self.set_key, ["cam-left", True])
        self.base.accept("arrow_right", self.set_key, ["cam-right", True])
        self.base.accept(self.k_forward_lo, self.set_key, ['forward', True])
        self.base.accept(self.k_backward_lo, self.set_key, ['backward', True])
        self.base.accept(self.k_left_lo, self.set_key, ['left', True])
        self.base.accept(self.k_right_lo, self.set_key, ['right', True])
        self.base.accept(self.k_crouch_lo, self.set_key, ['crouch', True])
        self.base.accept(self.k_jump_lo, self.set_key, ['jump', True])
        self.base.accept(self.k_use_lo, self.set_key, ['use', True])
        self.base.accept(self.k_attack_lo, self.set_key, ['attack', True])
        self.base.accept(self.k_h_attack_lo, self.set_key, ['h_attack', True])
        self.base.accept(self.k_f_attack_lo, self.set_key, ['f_attack', True])
        self.base.accept(self.k_block_lo, self.set_key, ['block', True])
        self.base.accept(self.k_sword_lo, self.set_key, ['sword', True])
        self.base.accept(self.k_bow_lo, self.set_key, ['bow', True])
        self.base.accept(self.k_tengri_lo, self.set_key, ['tengri', True])
        self.base.accept(self.k_umai_lo, self.set_key, ['umai', True])

    def kbd_init_released(self):
        # Define released keys
        self.base.accept("arrow_left-up", self.set_key, ["cam-left", False])
        self.base.accept("arrow_right-up", self.set_key, ["cam-right", False])
        self.base.accept("{0}-up".format(self.k_forward_lo), self.set_key, ['forward', False])
        self.base.accept("{0}-up".format(self.k_backward_lo), self.set_key, ['backward', False])
        self.base.accept("{0}-up".format(self.k_left_lo), self.set_key, ['left', False])
        self.base.accept("{0}-up".format(self.k_right_lo), self.set_key, ['right', False])
        self.base.accept("{0}-up".format(self.k_crouch_lo), self.set_key, ['crouch', False])
        self.base.accept("{0}-up".format(self.k_jump_lo), self.set_key, ['jump', False])
        self.base.accept("{0}-up".format(self.k_use_lo), self.set_key, ['use', False])
        self.base.accept("{0}-up".format(self.k_attack_lo), self.set_key, ['attack', False])
        self.base.accept("{0}-up".format(self.k_h_attack_lo), self.set_key, ['h_attack', False])
        self.base.accept("{0}-up".format(self.k_f_attack_lo), self.set_key, ['f_attack', False])
        self.base.accept("{0}-up".format(self.k_block_lo), self.set_key, ['block', False])
        self.base.accept("{0}-up".format(self.k_sword_lo), self.set_key, ['sword', False])
        self.base.accept("{0}-up".format(self.k_bow_lo), self.set_key, ['bow', False])
        self.base.accept("{0}-up".format(self.k_tengri_lo), self.set_key, ['tengri', False])
        self.base.accept("{0}-up".format(self.k_umai_lo), self.set_key, ['umai', False])
