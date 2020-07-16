from sekg.graph.exporter.graph_data import NodeInfo, GraphData
from sekg.ir.doc.wrapper import MultiFieldDocumentCollection, MultiFieldDocument

from project.utils.path_util import PathUtil

pro_name = "jabref"
doc_path = PathUtil.doc(pro_name=pro_name, version="v1")
graph_data_path = PathUtil.graph_data(pro_name="jabref", version="v1")
graph_data = GraphData.load(graph_data_path)
doc_collection: MultiFieldDocumentCollection = MultiFieldDocumentCollection.load(doc_path)
# e.g. org.jabref.model.metadata.event.MetaDataChangedEvent
api_name = "org.jabref.model.metadata.event.MetaDataChangedEvent"
node = graph_data.find_one_node_by_property(property_name='qualified_name', property_value=api_name)
api_id = node["id"]
doc: MultiFieldDocument = doc_collection.get_by_id(api_id)
return_data = dict()
return_data['doc_info'] = dict()
return_data['api_name'] = api_name
return_data['doc_info']['full_html_description'] = doc.get_doc_text_by_field('full_html_description')
return_data['doc_info']['full_description'] = doc.get_doc_text_by_field('full_description')
return_data['doc_info']['sentence_description'] = doc.get_doc_text_by_field('sentence_description')
print(return_data)
