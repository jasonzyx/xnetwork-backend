from django.apps import AppConfig
from .elasticsearch_singleton import ElasticsearchIndex
from .faiss_singleton import FaissIndex
from .search_rtr_singleton import SearchRTR, FeatureStore


class SearchConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = 'search'

    def ready(self):
        ElasticsearchIndex.get_instance()
        SearchRTR.get_instance("../ml-model/model-artifacts/mlp_model.pth")
        FeatureStore.get_instance("../ml-model/feast-feature-store/main_pangolin/feature_repo")
        # FaissIndex.get_instance("../ml-model/model-artifacts")

