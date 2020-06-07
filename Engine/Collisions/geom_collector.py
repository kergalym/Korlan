class GeomCollector:

    def get_num_geomnodes(self, assets_children: dict) -> dict:
        if assets_children:
            geomnode_num_dict = {}

            # Get a dict with number of geomnodes
            for k in assets_children:
                asset = assets_children[k]

                # Clean from duplicate
                if "BS" in asset.get_name():
                    continue

                asset_parent = assets_children[k].get_parent()
                # Clean from duplicate
                if "BS" in asset_parent.get_name():
                    continue

                name = assets_children[k].get_name()
                if name == '':
                    name = asset_parent.get_name()

                geomnode_num_dict[name] = asset
                geomnode_num_dict[name] = asset.findAllMatches('**/+GeomNode')

            return geomnode_num_dict

    def get_geom_single_nodes(self, geomnode_num_dict: dict) -> dict:
        if geomnode_num_dict:
            # The key is node name and the value is node paths list
            geomnode_dict = {}
            # Get geomnodes for single nodes
            for geomnode in geomnode_num_dict:
                if (not render.find("**/{0}".format(geomnode)).is_empty()
                        and render.find("**/{0}".format(geomnode)).get_num_children() == 0):
                    np = render.find("**/{0}".format(geomnode))
                    if np and np.find('+GeomNode').is_empty():
                        geomnode_dict[geomnode] = np
                    elif np and np.find('**/+GeomNode').is_empty():
                        geomnode_dict[geomnode] = np
                else:
                    geomnode_dict[geomnode] = geomnode_num_dict[geomnode]

            for geomnode in geomnode_dict:
                if not geomnode_dict[geomnode]:
                    if not render.find("**/{0}".format(geomnode)).is_empty():
                        np = render.find("**/{0}".format(geomnode))
                        if geomnode == np.get_name():
                            if np and not np.find('+GeomNode').is_empty():
                                geomnode_dict[geomnode] = np.find('+GeomNode')

            return geomnode_dict

    def geomnodes_compose(self, geomnode_dict: dict) -> list:
        if geomnode_dict:
            # The key is node name and the value is node path (contains a node)
            geomnodes_all_dict = {}
            # The key is geometry node and the value is node path (contains a node)
            nodes_all_dict = {}

            # Get all geomnodes together
            for geomnode in geomnode_dict:
                # Get single node
                if (hasattr(geomnode_dict[geomnode], 'get_num_children')
                        and geomnode_dict[geomnode].get_num_children() == 0):
                    geomnodes_all_dict[geomnode] = geomnode_dict[geomnode]

                    np = render.find("**/{0}".format(geomnode))
                    if not np.is_empty():
                        nodes_all_dict[np.get_name()] = np

                # Get multiple nodes
                elif not hasattr(geomnode_dict[geomnode], 'get_num_children'):
                    for x in geomnode_dict[geomnode]:
                        parent_name = x.get_parent().get_name()
                        name = x.get_name()
                        # Construct a name for empty
                        # from parent name
                        if name == '':
                            x.set_name(parent_name)
                            name = x.get_name()
                            geomnodes_all_dict[name] = x
                        else:
                            geomnodes_all_dict[name] = x

                        np = render.find("**/{0}".format(name))
                        if not np.is_empty():
                            nodes_all_dict[np] = x

            return [nodes_all_dict, geomnodes_all_dict]

    def geom_collector(self) -> list:
        assets = base.asset_nodes_collector()
        assets_children = base.asset_node_children_collector(
            assets, assoc_key=True)

        if (hasattr(base, "shaped_objects")
                and not base.shaped_objects):
            if assets_children:
                for k in assets_children:
                    asset = assets_children[k]
                    # Clear dict from actors
                    if not asset.find('**/+Character').is_empty():
                        assets_children.pop(k)

                geomnode_num_dict = self.get_num_geomnodes(assets_children)
                geomnode_dict = self.get_geom_single_nodes(geomnode_num_dict)

                return self.geomnodes_compose(geomnode_dict)
