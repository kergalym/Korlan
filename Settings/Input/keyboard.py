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
import json
from os.path import isfile

from direct.showbase.DirectObject import DirectObject
from korlan_run import Main


class Keyboard(DirectObject):
    def __init__(self):
        self.main = Main()
        DirectObject.__init__(self)

    """ Runs tasks """

    def run_task(self, key, task_type, task):

        if (isinstance(key, str)
                and isinstance(task_type, str)
                and task_type is None
                and isinstance(task, str)):
            self.accept(key, task)
        elif (isinstance(key, str)
              and isinstance(task_type, str)
              and task_type is 'Once'
              and isinstance(task, str)):
            self.acceptOnce(key, task)

    """ Sets the keyboard key in json """

    def set_mice_key(self, key, action):
        if (isinstance(key, str)
                and isinstance(action, str)):
            data = "{{}: {}}".format(key, action)
            with open("{}/Configs/Keyboard/{}_bind.json".format(self.main.main(), key), 'w') as f:
                f.write(data)

    """ Loads the keymap from json """

    def load_keymap(self, key):
        if (isinstance(key, str)
                and isfile("{}/Configs/Keyboard/{}_bind.json".format(self.main.main(), key))):
            with open("{}/Configs/Keyboard/{}_bind.json".format(self.main.main(), key), 'r') as f:
                conf = f.read()
            print(json.loads(conf))

    """ Loads the default keymap from json """

    def load_keymap_default(self, key):
        if (isinstance(key, str)
                and isfile("{}/Configs/Keyboard/{}_default_bind.json".format(self.main.main(), key))):
            with open("{}/Configs/Keyboard/{}_default_bind.json".format(self.main.main(), key), 'r') as f:
                conf = f.read()
            print(json.loads(conf))
