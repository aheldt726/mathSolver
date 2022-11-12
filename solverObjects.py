class ExpressionsWrap:
    def __init__(self, sym, num):
        self.symbolic = sym
        self.numeric = num


class Edge:
    def __init__(self, node1, node2, weight, weightloc):
        self.start_node = node1
        self.end_node = node2
        self.weight = weight
        self.weight_location = weightloc

    def __str__(self):
        if self.weight is not None:
            return "[" + str(self.start_node) + ", " + str(self.end_node)  + ", " + str(self.weight) + "]"
        else:
            return "[" + str(self.start_node) + ", " + str(self.end_node) + "]"

    def update_weight(self, new_weight):
        self.weight = new_weight

    def get_weight_loc(self):
        return self.weight_location


class Pert:  # TODO: reduce redundancies or unnecessary statements
    def __init__(self, node_name, node_loc, crash, beta, parents, name_dict):
        self.name = node_name  # Needed to print itself correctly
        self.loc = node_loc
        self.parents = parents
        self.names = name_dict
        self.beta = False
        self.crash = False
        self.num_children = 0
        self.has_children = False
        self.max_end_time = None
        self.end_times = []
        self.dict = None

        if isinstance(crash, list):
            self.crash_time = crash[0]
            self.crash_cost = crash[1]
            self.crash = True
        self.time = None
        if isinstance(beta, list):
            self.min_time = beta[0]
            self.av_time = beta[1]
            self.max_time = beta[2]
            self.time = (self.min_time + self.max_time + 4*self.av_time)/6
            self.variance = (self.max_time-self.min_time)/6
            self.beta = True
        else:
            self.time = beta
            self.variance = 0
        parents_named = []
        for x in self.parents:
            parents_named.append(self.names[x])
        self.time_total = self.time
        self.inherited_time = 0

    def get_time(self):
        return self.time

    def calc_times(self, dictionary):
        #Important note: dictionary here maps numbers to objects of this type
        max_time = 0
        for x in self.parents:
            if x in dictionary:
                dictionary[x].new_child()
                if dictionary[x].get_time() > max_time:
                    max_time = dictionary[x].get_time()
            else:
                self.parents = None
                max_time = 0

        self.time_total = max_time + self.time
        self.inherited_time = max_time
        self.dict = dictionary

    def new_child(self):
        self.num_children = self.num_children + 1
        self.has_children = True

    def update_end_time(self, time):
        self.end_times.append(time)
        if len(self.end_times) == self.num_children or self.num_children == 0:
            self.max_end_time = min(self.end_times)
            if self.parents is not None:
                for x in self.parents:
                    y = self.max_end_time - self.time
                    self.dict[x].update_end_time(y)

    def is_critical(self):
        val = False
        if self.inherited_time == self.max_end_time - self.time and self.time_total == self.max_end_time:
            val = True
        return val

    def print_info(self):  # TODO: reformat output so vertical lines match
        print(f"{self.name}|{self.inherited_time} {self.time_total}")
        print(f"{self.time}|{self.max_end_time - self.time} {self.max_end_time}")




