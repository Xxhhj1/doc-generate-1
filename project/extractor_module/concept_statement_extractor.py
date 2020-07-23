from sekg.util.dependency_tree_util import DependencyTreeUtil
from project.extractor_module.constant.constant import RelationNameConstant, ALLKnowledgeFromType, NPEntityType
from project.extractor_module.data_model.simple_sentence import SimpleSentence
from project.extractor_module.data_model.statement_record import StatementRecord

from project.extractor_module.statement_extractor import StatementExtractor


class ConceptStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "concept"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_represent(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                   doc_api_name))
        statement_record_list.extend(
            self.extract_for_A_is_xxx(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                      doc_api_name))

        return statement_record_list

    def extract_represent(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []
        if sent_doc.text.find(' represent') >= 0 and predicate.lemma_ == 'represent':
            subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
            neg = False
            for f in subtree_span:
                if f.dep_ == "neg":
                    neg = not neg
            if neg:
                return statement_record_list
            object = DependencyTreeUtil.get_object_for_verb(sent_doc, predicate)
            if object is None:
                return statement_record_list
            info_from_set = set()
            info_from_set.add((ALLKnowledgeFromType.FROM_Text_Category, sent_doc.text, doc_api_name))

            relation_data_tuple = StatementRecord(subject.text,
                                                  RelationNameConstant.Ontology_IS_A_Relation,
                                                  object.text,
                                                  NPEntityType.CategoryType,
                                                  NPEntityType.CategoryType,
                                                  self.extractor_name, info_from_set)
            statement_record_list.append(relation_data_tuple)

        return statement_record_list

    def extract_for_A_is_xxx(self, sent_doc, subject, predicate, doc_api_name):
        statement_record_list = []

        attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
        neg = False
        subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
        for f in subtree_span:
            if f.dep_ == "neg":
                neg = not neg
        if attr_span is None:
            return statement_record_list

        attr_spans = DependencyTreeUtil.split_span_into_parallel(sent_doc, attr_span)
        for i, attr_span in enumerate(attr_spans):
            if attr_span is None or attr_span.text == "":
                continue
            try:
                if attr_span.root.pos_ == "NOUN" or attr_span.root.pos_ == 'PROPN':
                    if neg:
                        return statement_record_list
                    noun_phase_doc = self.nlp(attr_span.text)
                    noun_phase, feature_list = DependencyTreeUtil.split_large_noun_phase_span_to_adj_and_np(
                        span=noun_phase_doc)
                    relation = RelationNameConstant.Ontology_IS_A_Relation if not (
                            noun_phase.startswith('member of') or noun_phase.startswith(
                        'part of')) else RelationNameConstant.Ontology_Derive_Relation
                    if noun_phase.startswith('member of'):
                        noun_phase = noun_phase.replace('member of', '', 1)
                    if noun_phase.startswith('part of'):
                        noun_phase = noun_phase.replace('part of', '', 1)

                    info_from_set = set()
                    info_from_set.add((ALLKnowledgeFromType.FROM_Text_Category, sent_doc.text, doc_api_name))
                    category_name = noun_phase
                    if category_name.lower().find("base class") >= 0:
                        category_name += (" " + DependencyTreeUtil.get_conditions_text_for_token(sent_doc,
                                                                                                 attr_span.root))

                    if relation != RelationNameConstant.Ontology_IS_A_Relation:
                        return statement_record_list

                    relation_data_tuple = StatementRecord(subject.text,
                                                          RelationNameConstant.Ontology_IS_A_Relation,
                                                          category_name,
                                                          NPEntityType.CategoryType,
                                                          NPEntityType.CategoryType,
                                                          self.extractor_name, info_from_set)
                    statement_record_list.append(relation_data_tuple)
            except Exception as e:
                print(e)
        return statement_record_list
