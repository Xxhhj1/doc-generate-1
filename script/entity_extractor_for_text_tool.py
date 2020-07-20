#!/usr/bin/env python
# -*- coding: utf-8 -*-


import re

from bs4 import BeautifulSoup
from nltk import WordNetLemmatizer
from nltk.corpus import wordnet as wn, stopwords
from sekg.text.extractor.domain_entity.nlp_util import SpacyNLPFactory
from sekg.util.code import CodeElementNameUtil


class EntityExtractorTool(object):
    MAX_STRING_LEN = 60
    MAX_WORD_NUM = 8
    invalid_content = [
        "0x",
        "|",
        "^ ",
        "_ ",
        ":[ ",
        "\\u",
        "\\u",
        "<",
        ">",
        "</",
        "/>",
        "//",
        "::",
    ]
    VALID_CHAR_STRING = "qwertyuiopasdfghjklzxcvbnm./1234567890()@_<>/- "

    def __init__(self):
        self.nlp = SpacyNLPFactory.create_spacy_nlp_for_domain_extractor()
        self.pattern = re.compile(r"NP_\w+ of NP_\w+")
        self.stopwords = stopwords.words('english')
        self.stopwords.append("-PRON-")
        self.stopwords = set(self.stopwords)
        self.lemmatizer = WordNetLemmatizer()
        self.code_patterns = [
            re.compile(r'^(?P<ELE>[a-zA-Z0-9_]*[a-z0-9][A-Z][a-z]+[a-zA-Z0-9_]*)(<.*>)?$'),
            # re.compile(r'^(?P<ELE>[a-zA-Z0-9_\.<>]+)\([a-zA-Z0-9_\,.<>)]*?$'),
            re.compile(r'^(?P<ELE>[a-zA-Z0-9_\.<>]+)\)[a-zA-Z0-9_\,.<>)]*?$'),
            re.compile(r'^(?P<ELE>[a-zA-Z]{2,}(\.[a-zA-Z0-9_]+)+)(<.*>)?$'),
        ]

        self.camel_cache = {}
        self.CODE_NAME_UTIL = CodeElementNameUtil()

    def uncamelize(self, camel_case):
        if camel_case in self.camel_cache:
            return self.camel_cache[camel_case]
        sub = self.CODE_NAME_UTIL.uncamelize_by_stemming(camel_case)
        self.camel_cache[camel_case] = sub
        return sub

    def extract_from_sentence(self, sent):
        """
        extract concept from one sentence.
        :param sent:
        :return: a set of concepts.
        """
        # code_elements = self.extract_code_element(sent)

        domain_terms = set()
        doc = self.nlp(sent)
        for chunk in doc.noun_chunks:
            chunk = self.clean_chunk(chunk)

            if len(chunk) == 0:
                continue
            if len(chunk) == 1 and self.is_word_common(chunk.text):
                continue
            # if chunk.text in code_elements:
            #     continue
            domain_terms.add(self.__chunk_lemmatize(chunk))
            domain_terms.update(self.extract_abbreviation_from_chunk(chunk))
            domain_terms.update(self.extract_NNPs_from_chunk(chunk))
        domain_terms.update(self.extract_np_of_np(doc))
        # print('sent: ' + sent)
        # print('result: ', result)
        domain_terms = self.__post_process(domain_terms)
        return domain_terms

    def extract_code_element(self, sent):
        elements = set()
        for word in sent.split():
            word = word.lstrip("#(").rstrip(",;.!?")
            # print(word)
            flag = False
            for index, pattern in enumerate(self.code_patterns):
                search_rs = pattern.search(word)
                if search_rs is not None and search_rs.group("ELE"):
                    # print(index, pattern, search_rs.group("ELE"))
                    elements.add(search_rs.group("ELE"))
                    flag = True
                # 若是不符合上述任何一种pattern,则考虑当前分词中是否存在驼峰式
                elif index == len(self.code_patterns) - 1 and not flag:
                    p = re.compile(r'(([a-z_]+([A-Z])[a-z_]+)+)|(([A-Z_]([a-z_]+))+)')
                    search_rs = p.search(word)
                    if search_rs is not None:
                        # print("camel:", search_rs.groups())
                        elements.add(search_rs.group(0))
        return elements

    def extract_np_of_np(self, doc):
        result = set([])
        sentence_text = doc[:].lemma_
        for chunk in doc.noun_chunks:
            chunk_arr = []
            chunk = self.clean_chunk(chunk)
            if len(chunk) == 0:
                continue
            for token in chunk:
                chunk_arr.append(token.lemma_)
            chunk_lemma = " ".join(chunk_arr)
            # print("chunk_lemma", chunk_lemma)
            replacement_value = "NP_" + "_".join(chunk_arr)
            # print("replacement_value", replacement_value)
            sentence_text = sentence_text.replace(chunk_lemma, replacement_value)
        # print("sentence_text", sentence_text)
        matches = re.findall(self.pattern, sentence_text)
        if len(matches) > 0:
            # print('matched: ', matches)
            for m in matches:
                result.add(m.replace("NP_", "").replace("_", " "))
        return result

    def is_valid_chunk_string(self, chunk_string):
        if chunk_string == "" or chunk_string == None:
            return False
        chunk_string = chunk_string.lower()

        if chunk_string in self.stopwords:
            return False

        for char in chunk_string:
            if char not in self.VALID_CHAR_STRING:
                return False
        if len(chunk_string.split(" ")) >= self.MAX_WORD_NUM:
            return False
        if chunk_string.endswith(".") and len(chunk_string) == 2:
            return False
        if len(chunk_string) > self.MAX_STRING_LEN or len(chunk_string) <= 2:
            return False

        if "https://" in chunk_string or "http://" in chunk_string:
            return False
        if chunk_string.endswith((".java", ".gif", "demo")):
            return False

        if "(" in chunk_string and ")" not in chunk_string:
            return False
        if ")" in chunk_string and "(" not in chunk_string:
            return False

        for invalid in self.invalid_content:
            if invalid in chunk_string:
                return False
        for word in chunk_string.replace(".", " ").replace("x", " ").split(" "):
            if word.isdigit():
                return False
        count = 0
        for word in chunk_string.split():
            if word in self.stopwords:
                count += 1
        if len(chunk_string.split()) == count:
            return False
        return True

    def clean_chunk(self, chunk):
        """
        remove the stopwords, digits and pronouns at the start of the chunk.
        pass the result which contains invalid symbol.
        :param chunk:
        :return:
        """
        if chunk.text.lower() in self.stopwords:
            return []
        while len(chunk) > 1:
            start_token = chunk[0]
            if start_token.text.lower() in self.stopwords or start_token.text.isdigit() or start_token.tag_ == 'PRP':
                chunk = chunk[1:]
            else:
                break
        if len(chunk) == 1:
            start_token = chunk[0]
            if start_token.text.lower() in self.stopwords or start_token.text.isdigit() or start_token.tag_ == 'PRP':
                return []
        if not re.match(r'^[a-zA-Z0-9][a-zA-Z0-9\' -]*[a-zA-Z0-9]$', chunk.text):
            return []
        return chunk

    def is_word_common(self, word):
        """
        check if the word is common word.
        :param word:
        :return:
        """
        if word in self.stopwords:
            return True
        if re.match(r'[a-zA-Z]+[a-zA-Z]$', word):
            word = self.lemmatizer.lemmatize(word, pos='n')
            synset = wn.synsets(word)
            if len(synset) > 0:
                return True
            else:
                return False
        return False

    def extract_abbreviation_from_chunk(self, chunk):
        result = set([])
        for token in chunk:
            if re.match(r'[A-Z]{2,}[0-9]*$', token.text):
                result.add(token.text)
        return result

    def extract_NNPs_from_chunk(self, chunk):
        result = set([])
        p = 0
        while p < (len(chunk) - 1):
            if chunk[p].tag_.startswith('NNP'):
                for i in range(p + 1, len(chunk)):
                    if not chunk[i].tag_.startswith('NNP'):
                        t_w = chunk[p:i]
                        p = i
                        if len(t_w) > 1:
                            result.add(self.__chunk_lemmatize(t_w))
                        break
                    elif i == len(chunk) - 1:
                        t_w = chunk[p:]
                        p = i
                        if len(t_w) > 1:
                            result.add(self.__chunk_lemmatize(t_w))
                        break
            else:
                p = p + 1
        return result

    def __chunk_lemmatize(self, chunk):
        """
        lemmatize the last word of chunk.
        :param chunk:
        :return:
        """

        word = self.lemmatizer.lemmatize(chunk.text, pos='n')

        return word

    def __post_process(self, result):
        new_result = set([])
        for item in result:
            if len(item) == 1 or item.isdigit():
                continue
            new_result.add(item)
        return new_result

    def extract_from_comment(self, comment):
        """
        extract domain_terms, code_elements from comment text
        :param comment:
        :return:
        """
        comment = re.sub(r'\s+', ' ', comment.strip().strip("/*").strip())
        if len(comment) == 0:
            return set(), set()
        domain_terms, code_elements = self.extract_from_sentence(comment)
        return domain_terms, code_elements

    def extract_from_html(self, html):
        terms = set()
        soup = BeautifulSoup(html, "lxml")
        tts = {tt.get_text() for tt in soup.findAll("tt")}
        terms.update({tt for tt in tts if len(tt.split()) <= 3})
        sent = soup.get_text()
        sent = re.sub(r'\s+', ' ', sent.strip().strip("/*").strip())
        domain_terms, code_elements = self.extract_from_sentence(sent)
        for term in domain_terms:
            terms.add(term)
        return terms, code_elements


if __name__ == "__main__":
    sent = "public void addComponent(String label, Component comp)\n" + \
           "{\n" + \
           "JLabel l = newLabel(label, comp);\n" + \
           "l.setBorder(new EmptyBorder(0,0,0,12));\n" + \
           "addComponent(l, comp, GridBagConstraints.BOTH);\n" + \
           "} //}}\n"
    print(sent)
    text = """
           If you create a custom component, make sure it supports accessibility. In particular, be aware that subclasses of JComponent are not automatically accessible. Custom components that are descendants of other Swing components should override inherited accessibility information as necessary.
           """
    extractor = EntityExtractorTool()
    terms = extractor.extract_code_element(sent)
    for term in terms:
        print(term)

    terms=extractor.extract_from_sentence(text)
    for term in terms:
        print(term)
