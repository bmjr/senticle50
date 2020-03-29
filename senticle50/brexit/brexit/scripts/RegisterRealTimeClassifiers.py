import glob
import json

from classifiers.ClassifierRegistry import ClassifierRegistry
from classifiers.RealTimeClassifierRegistry import RealTimeClassifierRegistry


def register_real_time_classifiers():
    for filename in glob.iglob("**/config/*.json", recursive=True):
        print(filename)
        config = json.load(open(filename))
        if 'classifier_name' in config:
            classifier = ClassifierRegistry().get(config['classifier_name'])
            if 'is_real_time' in config and config['is_real_time']:
                if 'model' in config:
                    RealTimeClassifierRegistry().add(config['name'],
                                                     config)
