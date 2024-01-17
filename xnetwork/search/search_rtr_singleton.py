import os, sys

# Get the directory of your current file
current_file_dir = os.path.dirname(__file__)

# Calculate the path to the 'ml-model' directory
ml_model_dir = os.path.join(current_file_dir, '../../ml-model/model-inference')
# Add the 'ml-model' directory to sys.path
sys.path.append(ml_model_dir)

# Now you can import your module
from inference import load_rtr_model, get_feature_store


class SearchRTR:
    _instance = None

    @classmethod
    def get_instance(cls, path_prefix=None):
        if cls._instance is None and path_prefix is not None:
            cls._instance = load_rtr_model(path_prefix)
        return cls._instance


class FeatureStore:
    _instance = None

    @classmethod
    def get_instance(cls, feature_store_path=None):
        if cls._instance is None and feature_store_path is not None:
            cls._instance = get_feature_store(feature_store_path)
        return cls._instance
