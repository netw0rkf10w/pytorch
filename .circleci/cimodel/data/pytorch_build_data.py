from cimodel.lib.conf_tree import ConfigNode, X, XImportant


CONFIG_TREE_DATA = [
    ("xenial", [
        ("rocm", [
            ("3.5.1", [
                ("3.6", [
                    ('build_only', [XImportant(True)]),
                ]),
            ]),
        ]),
        ("gcc", [
            ("5.4", [  # All this subtree rebases to master and then build
                ("3.6", [
                    ("important", [X(True)]),
                    ("parallel_tbb", [X(True)]),
                    ("parallel_native", [X(True)]),
                    ("pure_torch", [X(True)]),
                ]),
            ]),
            # TODO: bring back libtorch test
            ("7", [X("3.6")]),
        ]),
        ("clang", [
            ("5", [
                ("3.6", [
                    ("asan", [XImportant(True)]),
                ]),
            ]),
        ]),
        ("cuda", [
            ("9.2", [
                ("3.6", [
                    X(True),
                    ("cuda_gcc_override", [
                        ("gcc5.4", [
                            ('build_only', [XImportant(True)]),
                        ]),
                    ]),
                ])
            ]),
            ("10.1", [
                ("3.6", [
                    ('build_only', [X(True)]),
                ]),
            ]),
            ("10.2", [
                ("3.6", [
                    ("important", [X(True)]),
                    ("libtorch", [X(True)]),
                ]),
            ]),
            ("11.0", [
                ("3.8", [
                    X(True),
                    ("libtorch", [XImportant(True)])
                ]),
            ]),
        ]),
    ]),
    ("bionic", [
        ("clang", [
            ("9", [
                XImportant("3.6"),
            ]),
            ("9", [
                ("3.6", [
                    ("xla", [XImportant(True)]),
                    ("vulkan", [XImportant(True)]),
                ]),
            ]),
        ]),
        ("gcc", [
            ("9", [
                ("3.8", [
                    ("coverage", [XImportant(True)]),
                ]),
            ]),
        ]),
    ]),
]


def get_major_pyver(dotted_version):
    parts = dotted_version.split(".")
    return "py" + parts[0]


class TreeConfigNode(ConfigNode):
    def __init__(self, parent, node_name, subtree):
        super(TreeConfigNode, self).__init__(parent, self.modify_label(node_name))
        self.subtree = subtree
        self.init2(node_name)

    def modify_label(self, label):
        return label

    def init2(self, node_name):
        pass

    def get_children(self):
        return [self.child_constructor()(self, k, v) for (k, v) in self.subtree]


class TopLevelNode(TreeConfigNode):
    def __init__(self, node_name, subtree):
        super(TopLevelNode, self).__init__(None, node_name, subtree)

    # noinspection PyMethodMayBeStatic
    def child_constructor(self):
        return DistroConfigNode


class DistroConfigNode(TreeConfigNode):
    def init2(self, node_name):
        self.props["distro_name"] = node_name

    def child_constructor(self):
        distro = self.find_prop("distro_name")

        next_nodes = {
            "xenial": XenialCompilerConfigNode,
            "bionic": BionicCompilerConfigNode,
        }
        return next_nodes[distro]


class PyVerConfigNode(TreeConfigNode):
    def init2(self, node_name):
        self.props["pyver"] = node_name
        self.props["abbreviated_pyver"] = get_major_pyver(node_name)

    # noinspection PyMethodMayBeStatic
    def child_constructor(self):
        return ExperimentalFeatureConfigNode


class ExperimentalFeatureConfigNode(TreeConfigNode):
    def init2(self, node_name):
        self.props["experimental_feature"] = node_name

    def child_constructor(self):
        experimental_feature = self.find_prop("experimental_feature")

        next_nodes = {
            "asan": AsanConfigNode,
            "xla": XlaConfigNode,
            "vulkan": VulkanConfigNode,
            "parallel_tbb": ParallelTBBConfigNode,
            "parallel_native": ParallelNativeConfigNode,
            "libtorch": LibTorchConfigNode,
            "important": ImportantConfigNode,
            "build_only": BuildOnlyConfigNode,
            "cuda_gcc_override": CudaGccOverrideConfigNode,
            "coverage": CoverageConfigNode,
            "pure_torch": PureTorchConfigNode,
        }
        return next_nodes[experimental_feature]


class PureTorchConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "PURE_TORCH=" + str(label)

    def init2(self, node_name):
        self.props["is_pure_torch"] = node_name

    def child_constructor(self):
        return ImportantConfigNode


class XlaConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "XLA=" + str(label)

    def init2(self, node_name):
        self.props["is_xla"] = node_name

    def child_constructor(self):
        return ImportantConfigNode


class AsanConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "Asan=" + str(label)

    def init2(self, node_name):
        self.props["is_asan"] = node_name

    def child_constructor(self):
        return ImportantConfigNode


class VulkanConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "Vulkan=" + str(label)

    def init2(self, node_name):
        self.props["is_vulkan"] = node_name

    def child_constructor(self):
        return ImportantConfigNode


class ParallelTBBConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "PARALLELTBB=" + str(label)

    def init2(self, node_name):
        self.props["parallel_backend"] = "paralleltbb"

    def child_constructor(self):
        return ImportantConfigNode


class ParallelNativeConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "PARALLELNATIVE=" + str(label)

    def init2(self, node_name):
        self.props["parallel_backend"] = "parallelnative"

    def child_constructor(self):
        return ImportantConfigNode


class LibTorchConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "BUILD_TEST_LIBTORCH=" + str(label)

    def init2(self, node_name):
        self.props["is_libtorch"] = node_name

    def child_constructor(self):
        return ImportantConfigNode


class CudaGccOverrideConfigNode(TreeConfigNode):
    def init2(self, node_name):
        self.props["cuda_gcc_override"] = node_name

    def child_constructor(self):
        return ExperimentalFeatureConfigNode

class BuildOnlyConfigNode(TreeConfigNode):

    def init2(self, node_name):
        self.props["build_only"] = node_name

    def child_constructor(self):
        return ExperimentalFeatureConfigNode


class CoverageConfigNode(TreeConfigNode):

    def init2(self, node_name):
        self.props["is_coverage"] = node_name

    def child_constructor(self):
        return ExperimentalFeatureConfigNode


class ImportantConfigNode(TreeConfigNode):
    def modify_label(self, label):
        return "IMPORTANT=" + str(label)

    def init2(self, node_name):
        self.props["is_important"] = node_name

    def get_children(self):
        return []


class XenialCompilerConfigNode(TreeConfigNode):

    def modify_label(self, label):
        return label or "<unspecified>"

    def init2(self, node_name):
        self.props["compiler_name"] = node_name

    # noinspection PyMethodMayBeStatic
    def child_constructor(self):

        return XenialCompilerVersionConfigNode if self.props["compiler_name"] else PyVerConfigNode


class BionicCompilerConfigNode(TreeConfigNode):

    def modify_label(self, label):
        return label or "<unspecified>"

    def init2(self, node_name):
        self.props["compiler_name"] = node_name

    # noinspection PyMethodMayBeStatic
    def child_constructor(self):

        return BionicCompilerVersionConfigNode if self.props["compiler_name"] else PyVerConfigNode


class XenialCompilerVersionConfigNode(TreeConfigNode):
    def init2(self, node_name):
        self.props["compiler_version"] = node_name

    # noinspection PyMethodMayBeStatic
    def child_constructor(self):
        return PyVerConfigNode


class BionicCompilerVersionConfigNode(TreeConfigNode):
    def init2(self, node_name):
        self.props["compiler_version"] = node_name

    # noinspection PyMethodMayBeStatic
    def child_constructor(self):
        return PyVerConfigNode
