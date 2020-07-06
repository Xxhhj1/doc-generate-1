class StatementRecord:

    def __init__(self, s_name, r_name, e_name, s_type, e_type, which_extractor, info_from_set=None, **extra_info):
        if info_from_set is None:
            self.info_from_set = set([])
        else:
            self.info_from_set = info_from_set

        self.s_name = s_name
        self.r_name = r_name
        self.e_name = e_name
        self.s_type = s_type
        self.e_type = e_type
        self.which_extractor = which_extractor
        self.extra_info = extra_info

    def get_s_name(self):
        return self.s_name

    def get_e_name(self):
        return self.e_name

    def get_r_name(self):
        return self.r_name

    def get_info_from_set(self):
        return self.info_from_set

    def add_info_from(self, extract_way, source_text, belong_doc):
        self.info_from_set.add((extract_way, source_text, belong_doc))

    def to_json(self):

        base = {
            "s_name": self.s_name,
            "r_name": self.r_name,
            "e_name": self.e_name,
            "s_type": self.s_type,
            "e_type": self.e_type,

            "info_from_set": list(self.get_info_from_set()),
        }

        return base

    def __repr__(self):
        return "%r %r %r %r %r" % (self.s_name, self.r_name, self.e_name, self.s_type, self.e_type)

    def __hash__(self):
        text = self.s_name + "@@" + self.r_name + "@@" + self.e_name
        return hash(text)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        else:
            return False
