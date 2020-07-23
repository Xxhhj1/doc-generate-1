from sekg.util.dependency_tree_util import DependencyTreeUtil

from project.extractor_module.characteristic_extractor.be_jj_extractor import BeJJStatementExtractor
from project.extractor_module.characteristic_extractor.be_jj_np_extractor import BeJJNPStatementExtractor
from project.extractor_module.characteristic_extractor.can_be_vbn_extractor import CanBeVBNStatementExtractor
from project.extractor_module.characteristic_extractor.vb_np_rb import VBNPRBStatementExtractor
from project.extractor_module.data_model.simple_sentence import SimpleSentence
from project.extractor_module.data_model.simple_sentence_split import SimpleSentenceSplit


class StatementExtractorPipeline:
    def __init__(self, nlp=None):
        self.extractor_list = []
        self.sentence_split = SimpleSentenceSplit()
        self.nlp = nlp

    def init_pipeline(self):
        self.extractor_list = []

    def add_all_text_extractor(self):
        # self.add_func_related_extractor(self.nlp)
        # self.add_func_compare_extractor(self.nlp)
        # self.add_behavior_extractor(self.nlp)
        # self.add_constraint_extractor(self.nlp)
        # self.add_concept_extractor(self.nlp)
        # self.add_membership_extractor(self.nlp)
        self.add_characteristic_extractor(self.nlp)
        print("add all extractor finish")

    def add_some_extractor(self, *extractor_list):
        for extractor in extractor_list:
            if extractor not in self.extractor_list:
                self.extractor_list.append(extractor)

    def add_characteristic_extractor(self, nlp):
        self.extractor_list.append(BeJJStatementExtractor(nlp))
        self.extractor_list.append(BeJJNPStatementExtractor(nlp))
        self.extractor_list.append(CanBeVBNStatementExtractor(nlp))
        self.extractor_list.append(VBNPRBStatementExtractor(nlp))

    def extract_simple_sentence(self, simple_sentence: SimpleSentence):
        doc = simple_sentence.get_doc()
        full_doc = simple_sentence.get_full_doc()
        api_name = simple_sentence.api_from
        main_predicate = DependencyTreeUtil.get_main_predicate(full_doc)

    def extract_from_text(self, text, api_from):
        simple_sentence_list = self.sentence_split.create_sentence_list(text, api_from)
        statement_record_list = []
        for simple_sentence in simple_sentence_list:
            for extractor in self.extractor_list:
                statement_record_list.extend(extractor.extract_from_simple_sentence(simple_sentence))
        return statement_record_list
