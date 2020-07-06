from sekg.util.dependency_tree_util import DependencyTreeUtil


class SimpleSentence:
    def __init__(self, api_from, full_doc, doc, predicate=None):
        self.api_from = api_from
        self.full_doc = full_doc
        self.doc = doc
        if predicate is None:
            self.predicate = DependencyTreeUtil.get_main_predicate(doc)
        else:
            self.predicate = predicate

        self.subject = DependencyTreeUtil.get_subject(doc)

    def valid_check(self):
        if self.subject is None or self.predicate is None:
            return False
        return True

    def get_doc(self):
        return self.doc

    def get_subject(self):
        return self.subject

    def get_predicate(self):
        return self.predicate

    def get_full_doc(self):
        return self.full_doc
