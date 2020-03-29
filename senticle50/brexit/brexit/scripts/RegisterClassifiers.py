import glob
import importlib.util


def register_classifiers():
    for filename in glob.iglob("classifiers/*Classifier.py",
                               recursive=True):
        module_name = filename.split("/")
        module_name = module_name[len(module_name) - 1]
        module_name = module_name[:module_name.rfind('.py')]
        spec = importlib.util.spec_from_file_location(module_name,
                                                      filename)
        foo = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(foo)
        except Exception as error:
            print(error)
