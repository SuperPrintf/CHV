# CHV(Class Hierarchy Visualizer)
import ast
import subprocess
import os

class CHV:
    def __init__(self, file_path, output_dir=".", output_name="class_hierarchy", dpi=300):
        """
        初始化 CHV

        参数:
        file_path (str): 要解析的 Python 文件路径。
        output_dir (str): 输出文件的目录。
        output_name (str): 输出文件的名称（不包括扩展名）。
        dpi (int): 图片的 DPI（清晰度），默认值为 300。
        """
        self.set_file_path(file_path)
        self.set_output_dir(output_dir)
        self.set_output_name(output_name)
        self.set_dpi(dpi)
        self._classes = None

    def set_file_path(self, file_path):
        if not os.path.isfile(file_path):
            raise ValueError("提供的文件路径无效。")
        self._file_path = file_path

    def set_output_dir(self, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        self._output_dir = output_dir

    def set_output_name(self, output_name):
        if not output_name:
            raise ValueError("输出文件名不能为空。")
        self._output_name = output_name
        self._dot_filename = os.path.join(self._output_dir, f"{self._output_name}.dot")
        self._png_filename = os.path.join(self._output_dir, f"{self._output_name}.png")

    def set_dpi(self, dpi):
        if dpi <= 0:
            raise ValueError("DPI 必须为正整数。")
        self._dpi = dpi

    def _analyze_file(self):
        with open(self._file_path, 'r') as file:
            source_code = file.read()
        self._classes = self._analyze_code(source_code)

    def _analyze_code(self, source_code):
        tree = ast.parse(source_code)
        visitor = self._ClassDefVisitor()
        visitor.visit(tree)
        return visitor.classes

    def _generate_dot(self):
        dot_lines = ["digraph G {"]

        # 节点定义
        for class_name, details in self._classes.items():
            method_label = f"Methods|{{{'|'.join(details['methods'])}}}" if details['methods'] else ""
            variable_label = f"Variables|{{{'|'.join(details['variables'])}}}" if details['variables'] else ""
            labels = [label for label in [method_label, variable_label] if label]
            if labels:
                label = f'{class_name}|{{{"|".join(labels)}}}'
            else:
                label = class_name
            dot_lines.append(f'    "{class_name}" [shape=record, label="{{{label}}}"];')

        # 继承关系
        for class_name, details in self._classes.items():
            for base in details['bases']:
                dot_lines.append(f'    "{base}" -> "{class_name}";')

        dot_lines.append("}")
        return "\n".join(dot_lines)

    def _save_dot_to_file(self):
        dot_content = self._generate_dot()
        with open(self._dot_filename, 'w') as f:
            f.write(dot_content)

    def _convert_dot_to_png(self):
        subprocess.run(['dot', f'-Gdpi={self._dpi}', '-Tpng', self._dot_filename, '-o', self._png_filename])

    def visualize(self):
        """
        执行所有步骤以生成类继承关系图。
        """
        self._analyze_file()
        self._save_dot_to_file()
        self._convert_dot_to_png()

    class _ClassDefVisitor(ast.NodeVisitor):
        def __init__(self):
            self.classes = {}

        def visit_ClassDef(self, node):
            class_name = node.name
            bases = [base.id for base in node.bases if isinstance(base, ast.Name)]
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            variables = [n.targets[0].id for n in node.body if isinstance(n, ast.Assign)]

            self.classes[class_name] = {
                'bases': bases,
                'methods': methods,
                'variables': variables
            }
            self.generic_visit(node)

# 示例用法
file_path = 'python_file.py'  # 替换为你的Python文件路径

visualizer = CHV(file_path, output_dir="output", output_name="class_hierarchy", dpi=300)
visualizer.visualize()

# 在Jupyter Notebook中显示图片
# from IPython.display import Image
# Image(filename=visualizer._png_filename)
