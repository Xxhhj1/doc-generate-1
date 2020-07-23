from sekg.text.spacy_pipeline.pipeline import PipeLineFactory
from sekg.util.dependency_tree_util import DependencyTreeUtil
import inflect

import re
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer

from project.extractor_module.data_model.simple_sentence import SimpleSentence
from project.extractor_module.data_model.simple_sentence_split import SimpleSentenceSplit
from project.utils.tool import Tool


class StatementExtractor:
    def __init__(self, statement_extractor_pipeline=None, nlp=None):
        if nlp is not None:
            self.nlp = nlp
        else:
            self.nlp = PipeLineFactory.full_pipeline()
        self.sentence_split = SimpleSentenceSplit(self.nlp)
        self.stopwords = stopwords.words('english')
        self.stop_feature = set(self.stopwords)
        self.stop_feature.update(
            {'only', 'always', 'properly', 'rather', 'thus', 'already', 'yet', 'else', 'also', 'regardless',
             'similarly', 'typically', 'additionally', 'firstly', 'secondly', "however", "actual", "otherwise",
             "often", "therefore", "first", "second", "still", "rarely", "true",
             "usually", "most likely", "so far", "instead", "possibly", "exactly", "generally",
             "explicitly", "even", "later", "to do this", "simply", "as well", 'where', 'whenever', 'wherever', 'to',
             'once', 'twice', "new"})
        self.allow_like_word = {'allow', 'permit', 'grant'}
        self.depend_on_like_word = {'depend', 'rely', 'count'}
        self.limit_like_word = {'limit', 'confine', 'restrict'}
        self.guarantee_like_word = {'guarantee', 'ensure', 'assure'}
        self.prohibit_like_word = {'prohibit', 'forbid', 'disallow', 'veto'}
        self.same_word_list = {'same', 'similar', 'like', 'equivalent', 'difference', 'different'}
        self.mark_filter_words = {'if', 'when'}
        self.condition_words = {"if ", "when ", "during ", "only ", "where ", "case ",
                                "what ", "condition ", "event ", "whenever ", "whatever ",
                                "however ", "nevertheless ", "while ", "yet ", "but ", "whereas "}
        self.inflect_engine = inflect.engine()
        self.lemmatizer = WordNetLemmatizer()
        self.statement_extractor_pipeline = statement_extractor_pipeline

    def extract_from_simple_sentence(self, simple_sentence: SimpleSentence):
        return self.extract_from_simple_sentence(simple_sentence)

    def extract_from_text(self, text, api_from="", check=True):
        simple_sentence_list = self.sentence_split.create_sentence_list(text, api_from)
        statement_record_list = []
        for simple_sentence in simple_sentence_list:
            statement_record_list.extend(self.extract_from_simple_sentence(simple_sentence))
        return Tool.post_process(statement_record_list, check)

    def print_nlp_analysis(self, sent_doc):
        np_chunk_detail = [chunk for chunk in sent_doc.noun_chunks]
        print("np_chunk_detail for sentence", np_chunk_detail)
        SEP = " - "
        for chunk in sent_doc.noun_chunks:
            print(chunk.text, SEP, chunk.root.text, SEP,
                  chunk.root.dep_, SEP,
                  chunk.root.head.text)
        print("----chunk detail")
        for chunk in sent_doc.noun_chunks:
            for token in chunk:
                print(token.text, SEP, token.pos_, SEP, token.tag_, SEP)
        print("-----------end chunk print----------")
        for token in sent_doc:
            print(token.text, SEP, token.pos_, SEP, token.tag_, SEP, token.dep_, SEP, token.head.text, SEP,
                  token.head.pos_, SEP,
                  [child for child in token.children],
                  SEP,
                  [child for child in token.lefts],
                  SEP,
                  [child for child in token.rights],
                  )
        print("-----------end tree print----------")
        print("-----------subtree----------")
        print("subject of is:", DependencyTreeUtil.get_subject(doc=sent_doc),
              DependencyTreeUtil.get_subject_text(sent_doc))
        print("predicate is:", DependencyTreeUtil.get_main_predicate(doc=sent_doc))
        print("-----------end subtree----------")

    def new_split_span_into_parallel(self, doc, span):
        sub_doc = self.self_doc(span.text)
        find_token_set = set()
        span_list = []
        for t in sub_doc:
            if t.dep_ == "appos" or t.dep_ == "cc":
                find_token_set.add(t.head)
                span_list.append(DependencyTreeUtil.get_left_subtree_and_itself_span(doc, t.head))
        for find_token in find_token_set:
            for child in find_token.rights:
                if child.tag_ != "CC":
                    span_list.append(DependencyTreeUtil.get_left_subtree_and_itself_span(doc, child))
        if len(find_token_set) == 0:
            span_list.append(span)
        return span_list

    def check_has_condition(self, candidate_condition_text, func_name):
        if func_name is None or func_name == "":
            return False
        for key_word in self.condition_words:
            if func_name.find(key_word) >= 0:
                return True
        if candidate_condition_text is None or candidate_condition_text == "":
            return False
        for key_word in self.condition_words:
            if candidate_condition_text.find(key_word) >= 0:
                return True
        return False

    def self_doc(self, text):
        doc = self.nlp(text)
        doc = DependencyTreeUtil.merge_np_chunks(doc)
        doc = DependencyTreeUtil.merge_np_of_np(doc)
        return doc

    def is_extractable(self, simple_sentence: SimpleSentence):
        # api_name = simple_sentence.api_from
        # doc = simple_sentence.doc
        # full_doc = simple_sentence.full_doc
        return True

    def is_belong_to_like(self, sent_doc, predicate):
        if re.search(r'belong[a-z]* to', sent_doc.text) and predicate.lemma_ == 'belong':
            return True
        if predicate.lemma_ == 'have' and not predicate.dep_.startswith('aux'):
            return True
        if re.search(' (is|are) like ', sent_doc.text) is not None and predicate.lemma_ == 'be':
            return True
        if re.search(r'represent', sent_doc.text) and predicate.lemma_ == 'represent':
            return True
