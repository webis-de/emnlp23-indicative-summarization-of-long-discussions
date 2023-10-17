from clients import get_llm_client
from clustering import ThreadClusterer, result_to_clusters
from config import MODEL_HOSTS
from models import PostModel
from reddit import Reddit
from task import ClusterToLabel, LabelToMediaFrame
from util.tree import thread_to_tree


class Summarizer:
    def __init__(
        self,
        label_model,
        frame_model,
        host=None,
        api_key=None,
        max_new_tokens=64,
    ):
        if host is None:
            host = MODEL_HOSTS
        self.label_model = label_model
        self.frame_model = frame_model
        self.clients = {}
        self.host = host
        self.api_key = api_key
        self.max_new_tokens = max_new_tokens
        self.extra_kwargs = {}

    def _get_client(self, model):
        if model not in self.clients:
            self.clients[model] = get_llm_client(
                model=model, host=self.host, api_key=self.api_key
            )
        return self.clients[model]

    def label(
        self,
        tree,
        direct_instruction=None,
        dialogue_instruction=None,
        max_tokens_per_cluster=None,
        temperature=0,
        top_p=0,
        templates=None,
    ):
        client = self._get_client(self.label_model)
        extra_kwargs = {}
        if templates is not None:
            extra_kwargs["templates"] = templates
        labeler = ClusterToLabel(
            client=client,
            direct_instruction=direct_instruction,
            dialogue_instruction=dialogue_instruction,
            max_length=max_tokens_per_cluster,
            max_new_tokens=self.max_new_tokens,
            **extra_kwargs
        )
        clusters = result_to_clusters(tree["result"])
        labels = {
            str(key): labeler(
                value,
                temperature=temperature,
                top_p=top_p,
            )
            for key, value in clusters.items()
        }
        tree["labels"][self.label_model] = labels
        meta = labeler.meta()
        meta.update(
            {
                "max_tokens_per_cluster": max_tokens_per_cluster,
                "top_p": top_p,
                "temperature": temperature,
            }
        )
        tree["meta"].setdefault("labels", {})[self.label_model] = meta
        return tree

    def frame(
        self,
        tree,
        direct_instruction=None,
        dialogue_instruction=None,
        temperature=0,
        top_p=0,
        templates=None,
    ):
        client = self._get_client(self.frame_model)
        extra_kwargs = {}
        if templates is not None:
            extra_kwargs["templates"] = templates
        framer = LabelToMediaFrame(
            client=client,
            direct_instruction=direct_instruction,
            dialogue_instruction=dialogue_instruction,
            max_new_tokens=self.max_new_tokens,
            **extra_kwargs
        )
        frames = {
            key: framer(value, temperature=temperature, top_p=top_p)
            for key, value in tree["labels"][self.label_model].items()
        }
        tree["frames"].setdefault(self.label_model, {}).update(
            {self.frame_model: frames}
        )
        meta = framer.meta()
        meta.update(
            {
                "top_p": top_p,
                "temperature": temperature,
            }
        )
        tree["meta"].setdefault("frames", {}).setdefault(self.label_model, {})[
            self.frame_model
        ] = meta
        return tree


class Pipeline:
    def __init__(self):
        self.reddit = Reddit()
        self.clusterer = ThreadClusterer()

    def __call__(
        self,
        url,
        model=None,
        host=None,
        api_key=None,
        direct_label_instruction=None,
        dialogue_label_instruction=None,
        direct_frame_instruction=None,
        dialogue_frame_instruction=None,
        max_tokens_per_cluster=None,
        top_p=0.0,
        temperature=0.0,
        max_new_tokens=64,
    ) -> PostModel:
        url = str(url)
        thread = self.reddit.get_thread(url)
        tree = thread_to_tree(thread)
        tree["result"] = self.clusterer(
            thread,
            n_neighbors=30,
            n_components=10,
            min_dist=0.0,
            min_samples=None,
            cluster_selection_epsilon=0.0,
            cluster_selection_method="leaf",
        )
        tree["cluster_model"] = self.clusterer.model.model_name
        if model is not None:
            summarizer = Summarizer(
                label_model=model,
                frame_model=model,
                host=host,
                api_key=api_key,
                max_new_tokens=max_new_tokens,
            )
            tree = summarizer.label(
                tree,
                direct_instruction=direct_label_instruction,
                dialogue_instruction=dialogue_label_instruction,
                max_tokens_per_cluster=max_tokens_per_cluster,
                top_p=top_p,
                temperature=temperature,
            )
            tree = summarizer.frame(
                tree,
                direct_instruction=direct_frame_instruction,
                dialogue_instruction=dialogue_frame_instruction,
            )
        return tree
