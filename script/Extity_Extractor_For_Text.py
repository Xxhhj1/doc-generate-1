import re
import time
from collections import Counter
from pathlib import Path

import gensim
import numpy as np
from gensim import corpora
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize
from pattern.text import parsetree

"""
   给定一段文本，从中抽取实体,如果是其他格式的文本，请转成纯文本的输入
   update: 老的实体抽取，抽取出的内容需要再过滤，从文本中抽取实体目前使用entity_extractor.py
"""


# TODO 迁移tfidf，和新词发现

class EntityExtractorForText:
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

    def __init__(self, tf_idf_model_dir=None, corpus_list=None):

        self.n_gram_num = 3
        self.tfidf_sim = 0.4
        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.min_e = 1  #左右熵的最小阈值
        self.min_p = 2  #互信息的最小阈值
        self.tf_idf_flag = False
        self.lemma_map = {}

        if tf_idf_model_dir:
            self.tf_idf_model_dir = tf_idf_model_dir
            self.dictionary_path = str(Path(self.tf_idf_model_dir) / "dictionary.bin")
            self.corpus_path = str(Path(self.tf_idf_model_dir) / " corpus.mm")
            self.model_path = str(Path(self.tf_idf_model_dir) / "tfidf.model")
            self.tf_idf_flag = True
            self.corpus_list = corpus_list
            self.__init_model__()

    def update_n_gram_num(self, n_gram_num):
        self.n_gram_num = n_gram_num

    def update_tfidf_sim(self, tfidf_sim):
        self.tfidf_sim = tfidf_sim

    def update_min_e(self, min_e):
        self.min_e = min_e

    def update_min_p(self, min_p):
        self.min_p = min_p

    def __init_model__(self):
        if Path(self.dictionary_path).exists():
            self.dictionary = corpora.Dictionary.load(self.dictionary_path)
        else:
            self.dictionary = self.generate_dictionary(self.corpus_list)
        if Path(self.corpus_path).exists():
            self.corpus = gensim.corpora.MmCorpus(self.corpus_path)

        if Path(self.model_path).exists():
            self.tfidf_model = gensim.models.TfidfModel.load(self.model_path)
        else:
            print(self.corpus)
            self.tfidf_model = gensim.models.TfidfModel(corpus=self.corpus, id2word=self.dictionary, smartirs="dtc")

    def extract_chunk(self, text):
        """
        return all the chunk extracted form the text
        :param text: the text
        :return: list of chunk of object pattern.text.Chunk
        """
        result = []
        pst = parsetree(text)
        for sentence in pst:
            for chunk in sentence.chunks:
                if chunk.type == "NP":
                    result.append(chunk)
                    # print chunk.type, [(w.string, w.type) for w in chunk.words]
        return result

    def filter_chunk(self, chunk_list):
        """
        return all the chunk extracted form the text
        :param text: the text
        :return: list of chunk of object pattern.text.Chunk
        """
        result = []

        for chunk in chunk_list:
            # print(chunk.words[0])
            # if chunk.words[0].string=="The":
            #     chunk.words.remove(chunk.words[0])
            if self.is_valid_chunk_string(chunk.string):
                result.append(chunk)
        return result

    def lemma(self, text):
        """
        词形还原
        :param text:
        :return:
        """
        lemma_words = []
        for word in text.split():
            if word in self.lemma_map:
                lemma_words.append(self.lemma_map[word])
            else:
                lemma = self.lemmatizer.lemmatize(self.lemmatizer.lemmatize(word, "n"), "v")
                lemma_words.append(lemma)
                if lemma != word:
                    self.lemma_map[word] = lemma
        return " ".join(lemma_words)

    def is_valid_chunk_string(self, chunk_string):
        """
        判断是否有效的chunk
        :param chunk_string: str
        :return: True/False
        """
        if chunk_string == "" or chunk_string == None:
            return False
        chunk_string = chunk_string.lower()

        if chunk_string.split()[-1] in self.stopwords:
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
        if chunk_string.endswith((".java", ".gif", "demo", "ly", "ing", "ed")):
            return False
        if "https://" in chunk_string or "http://" in chunk_string:
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

    def get_clean_entity_name_for_string(self, chunk_string):
        """
        get the valid entity name, for example, "an Activity"=>"Activity","activities"=>"activity"
        :param chunk_string:
        :return: None, the cleaned entity name can be got. otherwise, return the clean entity
        """

        if self.is_valid_chunk_string(chunk_string) == False:
            return None
        return self.clean_np_text(chunk_string)

    def extract_chunks_strings(self, text):
        """
        从文本中抽取chunk，没有对chunk进行一些清理操作
        :param text:
        :return:
        """
        if text == "" or text == None:
            return []
        chunk_list = self.extract_chunk(text)
        chunk_list = self.filter_chunk(chunk_list)
        chunk_strings = [chunk.string for chunk in chunk_list]
        return list(set(chunk_strings))

    def extract_clean_entity_name_from_text(self, text):
        """
        从文本中抽取chunk，对chunk进行一些清理操作
        :param text:
        :return:
        """
        chunk_list = self.extract_chunks_strings(text)
        entity_name_list = []
        for chunk in chunk_list:
            entity_name = self.get_clean_entity_name_for_string(chunk)
            if entity_name:
                entity_name_list.append(entity_name)
        return list(set(entity_name_list))

    def is_valid_date(self, input_str):
        """
        Determine if it is a valid date string
        """
        word_list = input_str.split(' ', 1)
        for w in word_list:
            try:
                if ":" in w:
                    time.strptime(w, "%Y-%m-%d %H:%M:%S")
                else:
                    time.strptime(w, "%Y-%m-%d")
                return True
            except:
                pass
        return False

    def is_link_by_num(self, np_text):
        """
        判断是不是用数字连接
        :param np_text:
        :return:
        """
        pattern = re.compile(r'(\d+)-(\d+)')
        m = pattern.findall(np_text)
        if m is None or len(m) == 0:
            return False

        return True

    def remove_start_or_end_stop_word_for_one_time(self, np_text):
        """
        去除文本开头和结尾的停用词"
        :param np_text:
        :return:
        """
        word_list = np_text.lower().split(' ')
        if word_list[0] in self.stopwords:
            word_list = word_list[1:]
        if len(word_list) == 0:
            return None
        if word_list[-1] in self.stopwords:
            word_list = word_list[:-1]
        if len(word_list) == 0:
            return None

        return " ".join(word_list)

    def remove_start_dot(self, np_text):
        """
        去除文本开头的"."
        :param np_text:
        :return:
        """
        while len(np_text) > 0 and np_text[0] == '.':
            np_text = np_text[1:]
        return np_text

    def remove_other_start(self, np_text):
        """
        判断文本是否以"0x","/","1/"开始
        :param np_text:
        :return:
        """
        if np_text.find('0x') == 0 or np_text.find('/ ') == 0 or np_text.find('1/') == 0:
            return True
        return False

    def end_with_point(self, np_text):
        """
        去除文本末尾的"."
        :param np_text:
        :return:
        """
        if np_text[-1] == '.':
            return np_text[0:-1]
        return np_text

    def remove_all_stop_words_in_start_and_end(self, np_text):
        """
        去除开头和结尾中的所有停用词
        :param np_text:
        :return:
        """
        while True:
            new_np_text = self.remove_start_or_end_stop_word_for_one_time(np_text)
            if new_np_text == None:
                return None

            if np_text == new_np_text:
                return np_text
            np_text = new_np_text

    def clean_np_text(self, np_text):
        """
        clean np text
        :param np_text:
        :return:
        """
        np_text = np_text.lower()
        '''
        eg: merge
        3166-1 two-letter country code
        3166-1 two letters country code
        to lower case
        start with stop word
        remove ‘-’
        lemmatize_chunk
        '''
        np_text = self.remove_start_dot(np_text)
        np_text = self.end_with_point(np_text)
        if np_text.isspace():
            return None
        if self.remove_other_start(np_text):
            return None
        is_valid_date = self.is_valid_date(np_text)
        np_text = self.lemma(np_text)
        is_link_by_num = self.is_link_by_num(np_text)
        if is_valid_date or is_link_by_num:
            return None
        np_text = self.remove_all_stop_words_in_start_and_end(np_text)
        if np_text == None:
            return None
        words = np_text.split(" ")
        if np_text[0] == "@" and len(words) >= 2:
            np_text = words[0] + " ".join(words[1:])
        if np_text == "extended data":
            np_text = "data"
        np_text = np_text.replace("-", " ")
        return np_text

    def extract_single_verb(self, text):
        """
        return all the chunk extracted form the text
        :param text: the text
        :return: list of chunk of object pattern.text.Chunk
        """
        result = []
        pst = parsetree(text)
        for sentence in pst:
            for chunk in sentence.chunks:
                if chunk.type == "VP":
                    result.append(chunk.string.split(" ")[0])

        candidates = set(result)

        final_result = []
        for candidate in candidates:
            candidate = self.lemmatizer.lemmatize(candidate)
            if candidate not in self.stopwords:
                final_result.append(candidate)

        return list(set(final_result))

    def extract_verb_and_entity_name_from_text(self, text):

        verb_result = []
        np_result = []

        pst = parsetree(text)
        for sentence in pst:
            for chunk in sentence.chunks:
                if chunk.type == "NP":
                    np_result.append(chunk)
                    continue
                if chunk.type == "VP":
                    word_tagged_list = chunk.tagged
                    for word in word_tagged_list:
                        if word[1][0] == "V":
                            verb_result.append(word[0])
                    continue

        verb_result = set(verb_result)

        final_result = []
        for candidate in verb_result:
            candidate = self.lemmatizer.lemmatize(candidate)
            if candidate not in self.stopwords:
                final_result.append(candidate)

        for np in np_result:
            entity_name = self.get_clean_entity_name_for_string(np.string)
            if entity_name:
                final_result.append(entity_name)

        return list(set(final_result))

    def expand_the_chunk_by_words(self, final_chunk_list):
        final_set = []
        for chunk in final_chunk_list:
            final_set.append(chunk)
            for word in chunk.split(" "):
                if word not in self.stopwords:
                    final_set.append(word)
        return list(set(final_set))

    def get_all_possible_key_word_from_text(self, text):
        key_words_list = self.extract_verb_and_entity_name_from_text(text)

        final_key_words_list = self.expand_the_chunk_by_words(key_words_list)

        return final_key_words_list

    def clean_text(self, text):
        """
        清理文本，去除标点
        :param text:
        :return:
        """
        text = re.sub('\[.*?\]', '', text)

        punctuation = ['【', '】', ')', '(', '、', '，', '“', '”', '。', '\n', '《', '》', ' ', '-', '！', '？', '.', '\'', '[',
                       ']', ':', "：", '/', '.', '"', '\u3000', '’', '．', ',', '…', '?', '+', "(", ")", "=", "："]
        for i in punctuation:
            text = text.replace(i, " ")
        text = " ".join(text.split())
        return text

    # n-gram-list
    def create_ngram_list(self, sentence, n, is_clean=True):
        """
        creat ngram list
        :param sentence:  clean sentence, str
        :param n: n of ngram
        :param n: 是否清理生成的N-gram-list
        :return:
        """
        ngram_list = []
        for ngram_num in range(1, n + 1):
            if len(sentence) <= ngram_num:
                ngram_list.append(sentence)
            else:
                input_words = sentence.split()
                for tmp in zip(*[input_words[i:] for i in range(ngram_num)]):
                    tmp = " ".join(tmp).lower()
                    if is_clean:
                        if self.clean_np_text(tmp):
                            ngram_list.append(tmp)
                    else:
                        if tmp and tmp not in self.stopwords:
                            ngram_list.append(tmp)
        return ngram_list

    def find_new_words(self, ngram_list: list, clean_sentence: str):
        """
        find new words by PMI and Entropy_left_right,需要输入多一点语料
        :param ngram_list: ngram_list,list
        :param clean_sentence: sentences, str
        :return:
        """
        if not ngram_list:
            return []
        min_e = self.min_e
        min_p = self.min_p
        words_freq = dict(Counter(ngram_list))
        candidate = self.PMI_filter(words_freq, min_p)
        entity_list = self.Entropy_left_right_filter(candidate, clean_sentence, min_e)
        return entity_list

    def PMI_filter(self, word_freq_dic, min_p):
        """
        To get words witch  PMI  over the threshold
        input: word frequency dict , min threshold of PMI
        output: condinated word list

        """
        new_words = []
        for words in word_freq_dic:
            # print(words)
            split_word = words.split()
            if len(split_word) == 1:
                pass
            else:
                p_x_y = min(
                    [word_freq_dic.get(" ".join(split_word[:i]), 0) * word_freq_dic.get(" ".join(split_word[i:]), 0) for
                     i in range(1, len(split_word))])
                # print("p_x_y:", p_x_y)
                mpi = p_x_y / word_freq_dic.get(words)
                if mpi > min_p:
                    new_words.append(words)
        return new_words

    def calculate_entropy(self, char_list):
        """
        To calculate entropy for  list  of char
        input: char list
        output: entropy of the list  of char
        """
        char_freq_dic = dict(Counter(char_list))
        entropy = (-1) * sum(
            [char_freq_dic.get(i) / len(char_list) * np.log2(char_freq_dic.get(i) / len(char_list)) for i in
             char_freq_dic])
        return entropy

    def Entropy_left_right_filter(self, condinate_words, text, min_entropy):
        """
        To filter the final new words from the condinated word list by entropy threshold
        input:  condinated word list ,min threshold of Entropy of left or right
        output: final word list
        """
        final_words = []
        # print(text)
        for word in condinate_words:
            try:

                left_right_char = re.findall('([^\s]*)\s%s\s([^\s]*)' % word, text)
                left_char = [i[0] for i in left_right_char]
                left_entropy = self.calculate_entropy(left_char)

                right_char = [i[1] for i in left_right_char]
                right_entropy = self.calculate_entropy(right_char)

                if min(right_entropy, left_entropy) > min_entropy:
                    final_words.append(word)
            except:
                pass
        return final_words

    def filter_by_tf_idf(self, ngram_list):
        """
        利用tf-idf选取得分高的n-gram
        :param ngram_list:
        :return:
        """
        sentence_bow, missing_words = self.dictionary.doc2bow(ngram_list, return_missing=True,
                                                              allow_update=True)
        sentence_tfidf_vec = list(self.tfidf_model[sentence_bow])
        sentence_tfidf_vec = [sim for index, sim in sentence_tfidf_vec]
        np_array = np.array(sentence_tfidf_vec)
        over_thred = np.where(np_array > self.tfidf_sim)
        sentence_bow_filter = np.array(sentence_bow)[over_thred]
        entity = []
        for key, sim in list(sentence_bow_filter):
            if key in self.dictionary and self.is_valid_chunk_string(self.dictionary[key]):
                entity.append({"entity_name": self.lemma(self.dictionary[key]), "tf-idf": sim})
        return entity

    def generate_dictionary(self, text_list: list):
        """
        generate n-gram dictionary
        :param text_list: crops
        :return: dictionary
        """
        crops = []
        for text in text_list:
            ngram_list = []
            for sentence in sent_tokenize(text.replace('\n', '')):
                clean_sentence = self.clean_text(sentence)
                if not clean_sentence:
                    continue
                tmp_ngram_list = self.create_ngram_list(clean_sentence, 3)
                if tmp_ngram_list:
                    print(sentence)
                    print(tmp_ngram_list)
                    ngram_list += tmp_ngram_list
            if ngram_list:
                crops.append(ngram_list)
        dictionary = corpora.Dictionary(crops)
        dictionary.save(self.dictionary_path)
        self.corpus = [dictionary.doc2bow(text) for text in crops]
        gensim.corpora.MmCorpus.serialize(self.corpus_path, self.corpus)
        return dictionary

    def entity_add(self, new_entity_list, entity_dic, extract_way="chunk"):
        """
        保存entity的dic的合并，将新增的合并到旧的中
        :param new_entity_list:
        :param entity_dic:
        :param extract_way: 新entity的抽取方式
        :return:
        """
        for entity in new_entity_list:
            if entity not in entity_dic.keys():
                entity_dic[entity] = {extract_way}
            else:
                entity_dic[entity].add(extract_way)
        return entity_dic

    def extract(self, corpus):
        """
        给很多语料[text1,text2...]从中抽取实体
        :param corpus:
        :return:
        """
        all_clean_sentence = []
        all_n_gram = []
        entity_dic = {}

        for text in corpus:
            for sentence in sent_tokenize(text.replace('\n', '')):
                clean_sentence = self.clean_text(text)
                if clean_sentence:
                    chunk_strings = self.extract_clean_entity_name_from_text(sentence)
                    entity_dic = self.entity_add(chunk_strings, entity_dic, "chunk")
                    all_clean_sentence.append(clean_sentence)
                    ngram_list = self.create_ngram_list(clean_sentence, self.n_gram_num)
                    if not ngram_list:
                        continue
                    all_n_gram += ngram_list
                    if not self.tf_idf_flag:
                        continue
                    entity_tf_idf = self.filter_by_tf_idf(ngram_list)
                    entity_dic = self.entity_add(entity_tf_idf, entity_dic, "tf_idf")

        entity_new = self.find_new_words(all_n_gram, " ".join(all_clean_sentence))
        entity_dic = self.entity_add(entity_new, entity_dic, "new_words")

        return entity_dic


if __name__ == '__main__':
    processor = EntityExtractorForText()
    text = """
        If you create a custom component, make sure it supports accessibility. In particular, be aware that subclasses of JComponent are not automatically accessible. Custom components that are descendants of other Swing components should override inherited accessibility information as necessary.
        """
    # 只抽取名词
    r = processor.extract_clean_entity_name_from_text(text)
    print(r)
    # 抽取名词和动词
    r = processor.get_all_possible_key_word_from_text(text)
    print(r)
    # 基于互信息和左右熵的新词发现，需要较大规模语料，还需要调整参数 self.min_e，self.min_p，这两个参数越大，说明单词的质量高，当然，相应的数量也就会减少，自行调整
    n_gram_list = processor.create_ngram_list(processor.clean_text(text), n=3)
    r = processor.find_new_words(n_gram_list, text)
    print(r)
    # 综合抽取，目前只是简单合并每一种抽取方式，需要修改，比如单纯的名词抽取可能不可靠，会抽取一些很少出现的名词，可以结合TF-IDF一起过滤
    # 目前新词发现和TF-IDF的语料都是N-gram处理的
    # 注意:使用TF-IDF，需要先构建模型和字典，processor = EntityExtractorForText(tf_idf_model_dir=None, corpus_list=None)，这两个参数必填
    # tf-idf,调整参数：self.tfidf_sim
    r = processor.extract([text])
    print(r)
