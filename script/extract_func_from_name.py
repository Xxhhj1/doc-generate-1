from sekg.pipeline.base import KGBuildPipeline

from project.extractor_module.func_name_extractor import FuncNameExtractor
from project.utils.path_util import PathUtil

if __name__ == '__main__':
    pipeline = KGBuildPipeline()
    pro_name = "jabref"
    graph_data_v1_path = PathUtil.graph_data(pro_name=pro_name, version="v1.1")
    pipeline.load_graph(graph_data_v1_path)
    component1 = FuncNameExtractor()
    component1.set_save_path(PathUtil.graph_data(pro_name=pro_name, version="v1.2"))
    pipeline.add_component("从名称中抽取动词关系", component1)
    pipeline.run()
