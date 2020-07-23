from project.extractor_module.data_model.statement_extractor_pipeline import StatementExtractorPipeline
from project.extractor_module.text_builder import TextBuilder
from project.utils.graph_load_util import GraphLoadUtil

if __name__ == '__main__':
    pro_name = "jabref"
    document_collection = GraphLoadUtil.load_doc(pro_name, "v1.2")
    pipeline = StatementExtractorPipeline()
    builder = TextBuilder(document_collection, pipeline)
    builder.extract_all_pattern_from_text()

    builder.save_result()
