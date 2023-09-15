class relation_info:
    def __init__(self, relation):
        self.relation = relation
        self.inner_polygons = []
        self.outer_polygons = []

    def merge_polygons_inside_relation(self):
        p_lists1 = self.relation.get("members", [])
        new_p_lists = []

        # detect enclosed polygons (start == end)
        for p_list in p_lists1:
            try:
                if p_list.get("type", "") != "way":
                    continue
                if self.eq_by_lat_lon(p_list["geometry"][0], p_list["geometry"][-1]):
                    self.add_to_done_polygons(p_list)
                else:
                    new_p_lists.append(p_list)
            except Exception as err:
                print(err)

        print(f'{len(new_p_lists)} ways for merge')
        print(f'{len(self.inner_polygons)} inner ways completed {len(self.outer_polygons)} outer ways completed')

        merged = True
        n_merges = 0
        while merged:
            merged = False
            n_merges += 1
            print(f'{n_merges} merge ({len(new_p_lists)})')
            merge_dict = {}
            for i, p_list1 in enumerate(new_p_lists):
                geometry = p_list1["geometry"]
                p1 = self.geo_str(geometry[0])
                p2 = self.geo_str(geometry[-1])
                if p1 == p2:
                    continue
                if p1 not in merge_dict:
                    merge_dict[p1] = [i]
                else:
                    merge_dict[p1].append(i)
                if p2 not in merge_dict:
                    merge_dict[p2] = [i]
                else:
                    merge_dict[p2].append(i)

            indexes_taken = {}
            new_p_lists2 = []
            for k in merge_dict:
                try:
                    pair = merge_dict[k]
                    if len(pair) == 1:
                        continue
                    elif len(pair) >= 2:
                        if pair[0] in indexes_taken or pair[1] in indexes_taken:
                            continue
                        if pair[0] == pair[1]:
                            continue
                        if len(pair) == 2:
                            p_list1 = new_p_lists[pair[0]]
                            p_list2 = new_p_lists[pair[1]]
                        else:
                            continue

                        indexes_taken[pair[0]] = None
                        indexes_taken[pair[1]] = None
                        merged = self.connect_two_ways(merged, new_p_lists2, p_list1, p_list2)

                except Exception as err:
                    print(err)

            for i in range(len(new_p_lists)):
                if i not in indexes_taken:
                    new_p_lists2.append(new_p_lists[i])

            new_p_lists3 = []
            for i, p_list in enumerate(new_p_lists2):
                if self.eq_by_lat_lon(p_list["geometry"][0], p_list["geometry"][-1]):
                    self.add_to_done_polygons(p_list)
                else:
                    new_p_lists3.append(p_list)

            del new_p_lists
            del new_p_lists2
            new_p_lists = new_p_lists3

        #new_p_lists = self.connect_disconnected_polygons(new_p_lists)

        for p_list in new_p_lists:
            self.add_to_done_polygons(p_list)

        print(f'{n_merges} done')

    def connect_two_ways(self, merged, new_p_lists2, p_list1, p_list2):
        geometry1 = p_list1["geometry"]
        geometry2 = p_list2["geometry"]
        p11 = geometry1[0]
        p12 = geometry1[-1]
        p21 = geometry2[0]
        p22 = geometry2[-1]
        if p22 == p11:
            p_list2["geometry"].extend(p_list1["geometry"][1:])
            new_p_lists2.append(p_list2)
            merged = True
        elif p21 == p11:
            p_list1["geometry"] = p_list1["geometry"][::-1]
            p_list1["geometry"].extend(p_list2["geometry"][1:])
            new_p_lists2.append(p_list1)
            merged = True
        elif p21 == p12:
            p_list1["geometry"].extend(p_list2["geometry"][1:])
            new_p_lists2.append(p_list1)
            merged = True
        elif p22 == p12:
            p_list1["geometry"] = p_list1["geometry"][::-1]
            p_list2["geometry"].extend(p_list1["geometry"][1:])
            new_p_lists2.append(p_list2)
            merged = True
        return merged

    def add_to_done_polygons(self, p_list):
        if p_list.get("role", "") == "outer":
            self.outer_polygons.append(p_list)
        else:
            self.inner_polygons.append(p_list)

    def eq_by_lat_lon(self, geo1, geo2):
        return geo1['lat'] == geo2['lat'] and geo1['lon'] == geo2['lon']

    def geo_str(self, geo):
        return f"{geo['lat']}|{geo['lon']}"