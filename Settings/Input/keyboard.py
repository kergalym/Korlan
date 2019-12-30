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
        self.keymap = {
            "left": 0,
            "right": 0,
            "forward": 0,
            "backward": 0,
            "cam-left": 0,
            "cam-right": 0
        }

    # Records the state of the arrow/actions keys
    def set_key(self, key, value):
        self.keymap[key] = value

    def read_kbd_settings(self):
        pass

    def kbd_init(self):
        # Accept the control keys for movement and rotation
        self.base.accept("a", self.set_key, ["left", True])
        self.base.accept("d", self.set_key, ["right", True])
        self.base.accept("w", self.set_key, ["forward", True])
        self.base.accept("s", self.set_key, ["backward", True])
        self.base.accept("arrow_left", self.set_key, ["cam-left", True])
        self.base.accept("arrow_right", self.set_key, ["cam-right", True])
        self.base.accept("a-up", self.set_key, ["left", False])
        self.base.accept("d-up", self.set_key, ["right", False])
        self.base.accept("w-up", self.set_key, ["forward", False])
        self.base.accept("s-up", self.set_key, ["backward", False])
        self.base.accept("arrow_left-up", self.set_key, ["cam-left", False])
        self.base.accept("arrow_right-up", self.set_key, ["cam-right", False])
