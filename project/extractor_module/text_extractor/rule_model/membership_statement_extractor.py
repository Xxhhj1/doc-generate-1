from sekg.util.dependency_tree_util import DependencyTreeUtil

from constant.constant import ALLKnowledgeFromType, RelationNameConstant, NPEntityType
from data_model.simple_sentence import SimpleSentence
from data_model.statement_record import StatementRecord
from model.statement_extractor import StatementExtractor
import re


class MembershipStatementExtractor(StatementExtractor):
    def __init__(self, nlp=None):
        super().__init__(nlp)
        self.extractor_name = "membership"

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        statement_record_list = []
        sent_doc = simple_sentence.get_doc()
        doc_api_name = simple_sentence.api_from
        statement_record_list.extend(
            self.extract_for_A_is_xxx(sent_doc, simple_sentence.get_subject(), simple_sentence.get_predicate(),
                                      doc_api_name))
        statement_record_list.extend(
            self.extract_belong_to_like_category(sent_doc, simple_sentence.get_subject(),
                                                 simple_sentence.get_predicate(),
                                                 doc_api_name))
        return statement_record_list

    def extract_belong_to_like_category(self, sent_doc, subject, predicate, doc_api_name):
        # have + belong to
        statement_record_list = []
        if re.search(r'belong[a-z]* to', sent_doc.text) and predicate.lemma_ == 'belong':
            subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
            neg = False
            for f in subtree_span:
                if f.dep_ == "neg":
                    neg = not neg
            if neg:
                return statement_record_list
            object = DependencyTreeUtil.get_object_for_verb(sent_doc, predicate)
            prep_object = DependencyTreeUtil.get_object_for_preposition(sent_doc, predicate)
            if object or prep_object:
                object = object if object else prep_object
            else:
                return statement_record_list
            info_from_set = set()
            info_from_set.add((ALLKnowledgeFromType.FROM_Text_Category, sent_doc.text, doc_api_name))

            relation_data_tuple = StatementRecord(subject.text,
                                                  RelationNameConstant.Ontology_Derive_Relation,
                                                  object.text,
                                                  NPEntityType.CategoryType,
                                                  NPEntityType.CategoryType,
                                                  self.extractor_name, info_from_set)
            statement_record_list.append(relation_data_tuple)
        if predicate.lemma_ == 'have' and not predicate.dep_.startswith('aux'):
            subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
            neg = False
            for f in subtree_span:
                if f.dep_ == "neg":
                    neg = not neg
            if neg:
                return statement_record_list
            object = DependencyTreeUtil.get_object_for_verb(sent_doc, predicate)
            prep_object = DependencyTreeUtil.get_object_for_preposition(sent_doc, predicate)
            if object or prep_object:
                object = object if object else prep_object
            else:
                return statement_record_list
            info_from_set = set()
            info_from_set.add((ALLKnowledgeFromType.FROM_Text_Category, sent_doc.text, doc_api_name))

            relation_data_tuple = StatementRecord(subject.text,
                                                  RelationNameConstant.Ontology_Derive_Relation,
                                                  object.text,
                                                  NPEntityType.CategoryType,
                                                  NPEntityType.CategoryType,
                                                  self.extractor_name, info_from_set)
            statement_record_list.append(relation_data_tuple)

        return statement_record_list

    def extract_for_A_is_xxx(self, sent_doc, subject, predicate, doc_api_name):
        # be member of/be part of
        statement_record_list = []

        raw_attr_span = DependencyTreeUtil.get_attr_for_be_predicate(doc=sent_doc, predicate_token=predicate)
        neg = False
        subtree_span = DependencyTreeUtil.get_subtree_span_from_one_token_obj(sent_doc, predicate)
        for f in subtree_span:
            if f.dep_ == "neg":
                neg = not neg
        if raw_attr_span is None:
            return statement_record_list
        attr_spans = DependencyTreeUtil.split_span_into_parallel(sent_doc, raw_attr_span)
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

                    if relation == RelationNameConstant.Ontology_IS_A_Relation:
                        return statement_record_list

                    relation_data_tuple = StatementRecord(subject.text,
                                                          RelationNameConstant.Ontology_Derive_Relation,
                                                          category_name,
                                                          NPEntityType.CategoryType,
                                                          NPEntityType.CategoryType,
                                                          self.extractor_name, info_from_set)
                    statement_record_list.append(relation_data_tuple)
            except Exception as e:
                print(e)
        return statement_record_list
