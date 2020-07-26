from pathlib import Path

from sekg.graph.exporter.graph_data import GraphData
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection

from definitions import OUTPUT_DIR
from project.utils.path_util import PathUtil
import json


class EntityService():
    def __init__(self, doc_collection):
        graph_data_path = PathUtil.graph_data(pro_name="jabref", version="v1.5")
        self.graph_data = GraphData.load(graph_data_path)
        self.doc_collection = doc_collection
        self.entity_words = set()
        self.entity_2_score = dict()
        self.counter = 0
        self.entity_path = str(Path(OUTPUT_DIR) / "entity.json")

    def link_all_api_entity(self):
        if len(self.entity_words) == 0:
            self.load_entity_words()
        document_list = self.doc_collection.get_document_list()
        for i, document in enumerate(document_list):
            full_description = str(document.get_doc_text_by_field('full_description'))
            for word in self.entity_words:
                if full_description.find(" " + word + " ") >= 0 or full_description.startswith(
                        word) or full_description.endswith(word):
                    self.link_api_entity(document, word)
                    # print("word: "+word)
                    # print("full_description: "+full_description)

    def link_api_entity(self, doc, word):
        end_id = self.create_entity(word)
        self.add_relations(doc.id, "has terminology", end_id)

    def create_entity(self, word):
        label_info = {"entity"}
        label_info.add("terminology")
        node_properties = dict()
        node_properties["score"] = self.entity_2_score[word]
        node_properties["terminology_name"] = word
        graph_id = self.graph_data.add_node(label_info, node_properties,
                                            primary_property_name="terminology_name")
        return graph_id

    def add_relations(self, start_id, relation_str, end_id):
        """
        添加图中的关系
        @param start_id:
        @param end_id:
        @param relation_str:
        @return:
        """
        try:
            self.counter += 1
            print(self.counter)
            self.graph_data.add_relation(start_id, relation_str, end_id)
        except Exception as e:
            print(e)

    def load_entity_words(self):
        load_dict = self.load_json(self.entity_path)
        for each in load_dict:
            self.entity_words.add(each["entity_name"])
            self.entity_2_score[each["entity_name"]] = each["tf_idf"]

    def load_json(self, path):
        with open(path, "r") as load_f:
            load_dict = json.load(load_f)
            return load_dict

    def save_graph(self, output_path):
        self.graph_data.save(output_path)


if __name__ == '__main__':
    pro_name = "jabref"
    data_dir = PathUtil.doc(pro_name=pro_name, version="v1.1")
    doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(data_dir)
    entity_service = EntityService(doc_collection)
    entity_service.link_all_api_entity()
    entity_service.save_graph(str(PathUtil.graph_data(pro_name="jabref", version="v1.6")))
    print("counter:" + str(entity_service.counter))
