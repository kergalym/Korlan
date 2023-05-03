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
        self.gpu_instancing = None
        self.model = None
        self.is_loaded = False

    def init(self):
        if len(self.foliage_asset_bs) > 0:
            del self.foliage_asset_bs
            self.foliage_asset_bs = {}

        self.gpu_instancing = self.base.game_instance["gpu_instancing_cls"]

        taskMgr.add(self.asset_watcher_task, "asset_watcher_task")

    def get_foliage_stack(self):
        return self.foliage_asset_bs

    async def async_foliage_loading(self, path):
        if self.is_loaded:
            return

        if not self.model:
            self.is_loaded = False
            self.model = await self.base.loader.load_model(path, blocking=False)
            self.is_loaded = True
            self.model.reparent_to(self.base.game_instance["world_np"])
            self.is_loaded = False
        elif self.model.get_name() not in path:
            self.is_loaded = False
            self.model = await self.base.loader.load_model(path, blocking=False)
            self.is_loaded = True
            self.model.reparent_to(self.base.game_instance["world_np"])
            self.is_loaded = False

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

                if self.model is not None:
                    for asset in self.model.find_all_matches("**/*LOD*"):
                        print(asset)
                        prefab_lod, prefab_lod_np = self.gpu_instancing.construct_prefab_lod(pattern=asset.get_name())

                        # We are going to in instance this object multiple times
                        if asset is not None:

                            name_bs = asset.get_parent().get_name()

                            # Skip asset if we added it already
                            if name_bs in self.foliage_asset_bs:
                                continue

                            if "LODNode" in asset.get_name():
                                continue

                            self.gpu_instancing.setup_prefab_lod(prefab=asset,
                                                                 prefab_lod_np=prefab_lod_np,
                                                                 prefab_lod=prefab_lod)

                            self.gpu_instancing.populate_instance(prefab=asset)

                            self.foliage_asset_bs[name_bs] = asset.get_parent()

        return task.cont
