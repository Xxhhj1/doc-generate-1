from pathlib import Path

from sekg.pipeline.base import KGBuildPipeline

from definitions import OUTPUT_DIR
from project.extractor_module.category_structure_extractor import CategoryStructureExtractor
from project.utils.path_util import PathUtil

if __name__ == '__main__':
    pipeline = KGBuildPipeline()
    pro_name = "jabref"
    graph_data_v1_path = PathUtil.graph_data(pro_name=pro_name, version="v1.2")
    pipeline.load_graph(graph_data_v1_path)
    component1 = CategoryStructureExtractor()
    component1.set_json_save_path(Path(OUTPUT_DIR) / "json" / "name_category.json")
    component1.set_save_path(PathUtil.graph_data(pro_name=pro_name, version="v1.3"))
    pipeline.add_component("从名称和结构中抽取概念关系", component1)
    pipeline.run()
