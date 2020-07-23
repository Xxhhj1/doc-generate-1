from pathlib import Path

from sekg.text.pretreatment.complete_subject import CompleteSubject
from sekg.text.spacy_pipeline.pipeline import PipeLineFactory

from definitions import OUTPUT_DIR
from project.utils.log_tool import logger
from project.utils.tool import Tool


class BaseExtractorBuilder:
    def __init__(self):
        self.api_id_2_record = dict()
        self.pickle_save_path = ""

    def post_process(self):
        """
        对结果进行后处理
        """
        for api_id in self.api_id_2_record:
            statement_record_set = self.api_id_2_record[api_id]
            pass

    def save_others(self):
        print("save others")

    def save_result(self):
        self.save_others()
        if self.pickle_save_path == "":
            raise Exception("未提供保存路径")
        Tool.save_2_pickle(self.api_id_2_record, self.pickle_save_path)


class TextBuilder(BaseExtractorBuilder):
    # extract from document collection text
    def __init__(self, document_collection, pipeline, graph=None):
        super().__init__()
        self.document_collection = document_collection
        self.pipeline = pipeline
        self.pickle_save_path = str(Path(OUTPUT_DIR) / "api_id_2_record.pickle")
        self.graph = graph
        self.complete_subject_tool = CompleteSubject()
        self.nlp = PipeLineFactory.full_pipeline()

    def extract_all_pattern_from_text(self):
        self.pipeline.init_pipeline()
        self.pipeline.add_all_text_extractor()
        document_list = self.document_collection.get_document_list()
        print(len(document_list))
        for i, document in enumerate(document_list):
            if i % 100 == 0:
                print(i)
            api_name = document.get_name()
            api_id = document.id
            description_sentences = document.get_doc_text_by_field('sentence_description')
            if len(description_sentences) == 0:
                continue
            self.api_id_2_record[api_id] = set()
            for text in description_sentences:
                try:
                    sent_doc = self.nlp(text)
                    text_after = self.complete_subject_tool.complete_subject_for_sentence(text, api_name, sent_doc)
                    statement_record_list = self.pipeline.extract_from_text(text_after, api_name)
                    if len(statement_record_list) > 0:
                        self.api_id_2_record[api_id].update(statement_record_list)
                except Exception as e:
                    logger.error('i' + str(i) + "&&" + text)
                    print(e)
