from pathlib import Path

from sekg.pipeline.base import KGBuildPipeline

from definitions import OUTPUT_DIR
from project.extractor_module.characteristic_structure_extractor import CharacteristicStructureExtractor
from project.utils.path_util import PathUtil

if __name__ == '__main__':
    pipeline = KGBuildPipeline()
    pro_name = "jabref"
    graph_data_v1_path = PathUtil.graph_data(pro_name=pro_name, version="v1")
    pipeline.load_graph(graph_data_v1_path)
    component1 = CharacteristicStructureExtractor()
    component1.set_json_save_path(Path(OUTPUT_DIR) / "json" / "name_characteristic.json")
    component1.set_save_path(PathUtil.graph_data(pro_name=pro_name, version="v1.1"))
    pipeline.add_component("从名称和结构中抽取特征", component1)
    pipeline.run()
