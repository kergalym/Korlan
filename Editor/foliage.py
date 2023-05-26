from os.path import exists
from direct.task.TaskManagerGlobal import taskMgr
from direct.stdpy.file import exists as vfs_exists
from direct.stdpy.file import listdir as vfs_listdir


class Foliage:
    """
    This class implements foliage stack and foliage painting
    """
    def __init__(self):
        self.base = base
        self.render = render
        self.foliage_asset_bs = {}
        self.models = {}
        self.stack = []
        self.gpu_instancing = None
        self.model = None
        self.is_loaded = False

    def init(self):
        if len(self.foliage_asset_bs) > 0:
            del self.foliage_asset_bs
            self.foliage_asset_bs = {}

        if len(self.models) > 0:
            del self.models
            self.models = {}

        self.gpu_instancing = self.base.game_instance["gpu_instancing_cls"]

        taskMgr.do_method_later(1.5, self.asset_watcher_task, "asset_watcher_task")

    def get_foliage_stack(self):
        return self.foliage_asset_bs

    def get_models_stack(self):
        return self.models

    async def async_foliage_loading(self, path):
        if not self.model:
            self.is_loaded = False
            self.model = await self.base.loader.load_model(path, blocking=False)
            self.is_loaded = True
            name = self.model.get_name().replace(".egg", "")
            self.model.set_name(name)
            self.is_loaded = False
            if name not in self.models:
                self.models[name] = self.model

        elif self.model.get_name() not in self.models:
            self.is_loaded = False
            self.model = await self.base.loader.load_model(path, blocking=False)
            self.is_loaded = True
            name = self.model.get_name().replace(".egg", "")
            self.model.set_name(name)
            self.is_loaded = False
            if name not in self.models:
                self.models[name] = self.model

        else:
            if self.model.get_num_children() == 0:
                self.is_loaded = False
                self.model = await self.base.loader.load_model(path, blocking=False)
                self.is_loaded = True
                name = self.model.get_name().replace(".egg", "")
                self.model.set_name(name)
                self.is_loaded = False
                if name not in self.models:
                    self.models[name] = self.model

    def asset_watcher_task(self, task):
        if self.base.game_instance["menu_mode"]:
            return task.done

        path = "{0}/Assets/Foliage".format(self.base.game_dir)
        if vfs_exists(path) or exists(path):
            for _path in vfs_listdir(path):

                if ".egg" not in _path:
                    continue

                file_path = "{0}/{1}".format(path, _path)

                if not vfs_exists(file_path) or not exists(file_path):
                    continue

                taskMgr.add(self.async_foliage_loading(file_path))

                if self.model is None:
                    break

        return task.again

    def instance_to(self, pos, count, density):
        for prefab in self.model.find_all_matches("**/*LOD*"):
            # We are going to in instance this object multiple times

            name_bs = prefab.get_name()

            prefab_lod, prefab_lod_np = self.gpu_instancing.construct_prefab_lod(pattern=prefab.get_name())

            if "LODNode" in prefab.get_name():
                continue

            self.gpu_instancing.setup_prefab_lod(prefab=prefab,
                                                 prefab_lod_np=prefab_lod_np,
                                                 prefab_lod=prefab_lod)

            self.gpu_instancing.populate_instances_with_brush(prefab=prefab,
                                                              pos=pos,
                                                              count=count,
                                                              density=density)

            if "LOD0" in prefab.get_parent().get_name():
                self.foliage_asset_bs[name_bs] = prefab.get_parent()

