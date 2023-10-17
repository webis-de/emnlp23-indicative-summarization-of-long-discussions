import re
from collections import defaultdict

import hdbscan
import numpy as np
import pandas as pd
from .argument_noise import ARGUMENT_NOISE
from sbert import SBERT

EMPTY_RE = re.compile("^[^a-zA-Z0-9]*$")
URL_RE = re.compile(r"https?:\/\/[^ \t]*", flags=re.MULTILINE)


def dimensionality_reduction(
    embeddings,
    n_neighbors,
    n_components,
    min_dist,
    metric="cosine",
    random_state=None,
    return_model=False,
):
    from umap import UMAP

    model = UMAP(
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist,
        metric=metric,
        random_state=random_state,
        low_memory=False,
    )
    reduced = model.fit_transform(embeddings)
    if return_model:
        return reduced, model
    return reduced


def extract_lambda_values(hdbscan_model):
    tree = hdbscan_model.condensed_tree_._raw_tree
    leaves = tree[tree["child"] < len(hdbscan_model.labels_)]
    sort_idx = np.argsort(leaves["child"])
    return leaves[sort_idx]["lambda_val"]


def hdbscan_cluster(
    embeddings,
    min_cluster_size,
    min_samples,
    cluster_selection_method,
    cluster_selection_epsilon,
    max_number_of_joined_clusters=None,
    return_lambda_values=False,
):
    hdbscan_model = hdbscan.HDBSCAN(
        min_cluster_size=min_cluster_size,
        min_samples=min_samples,
        metric="euclidean",
        cluster_selection_method=cluster_selection_method,
        cluster_selection_epsilon=cluster_selection_epsilon,
        prediction_data=True,
        max_number_of_joined_clusters=max_number_of_joined_clusters,
    )
    hdbscan_model.fit(embeddings)
    labels = hdbscan_model.labels_
    probabilities = hdbscan.all_points_membership_vectors(hdbscan_model)
    return_args = (labels, probabilities)
    if return_lambda_values:
        return_args += (extract_lambda_values(hdbscan_model),)
    return return_args


def dimensionality_reduction_with_argument_noise(
    sentence_embeddings,
    noise_embeddings,
    n_neighbors,
    n_components,
    min_dist,
    random_state=None,
):
    reduced_embeddings = dimensionality_reduction(
        np.concatenate(
            [e for e in (sentence_embeddings, noise_embeddings) if len(e) > 0]
        ),
        n_neighbors=n_neighbors,
        n_components=n_components,
        min_dist=min_dist,
        metric="euclidean",
        random_state=random_state,
    )
    reduced_sentence_embeddings, reduced_noise_embeddings = np.split(
        reduced_embeddings, [len(sentence_embeddings)]
    )
    return reduced_sentence_embeddings, reduced_noise_embeddings


def classify_noise(sentences, sentence_labels, noise_labels, sentence_probabilities):
    cluster_sizes = pd.Series(sentence_labels).value_counts()
    noise_per_cluster = pd.Series(noise_labels).value_counts()
    merged = (
        pd.merge(
            cluster_sizes.rename("sentence"),
            noise_per_cluster.rename("noise"),
            left_index=True,
            right_index=True,
            how="outer",
        )
        .fillna(0)
        .astype(int)
        .drop(index=-1, errors="ignore")
    )
    noise_score = merged["noise"] / (merged["sentence"] + merged["noise"])
    cutoff_value = 2 / 3 * merged["noise"].sum() / merged.values.sum()
    noise_clusters = set(noise_score[noise_score > cutoff_value].index.tolist())
    soft_labels = sentence_probabilities.argmax(axis=1)
    is_empty = np.array(
        [
            bool(EMPTY_RE.match(s)) or len(s.replace(" ", "").replace("\t", "")) < 8
            for s in sentences
        ]
    )
    is_noise = (
        np.array(
            [
                label in noise_clusters or soft_label in noise_clusters
                for soft_label, label in zip(soft_labels, sentence_labels)
            ]
        )
        | is_empty
    )
    return is_noise


def get_min_cluster_size(num_sentences, min_value=None, scale=None):
    value = 0.421 * num_sentences**0.559
    if scale is not None:
        value *= scale
    if min_value is not None:
        value = max(value, min_value)
    value = round(value)
    return value


class ArgumentNoiseClassifier:
    def __init__(self, model=None):
        self.model = SBERT() if model is None else model

    def __call__(
        self,
        sentences,
        n_neighbors=30,
        n_components=10,
        random_state=0,
        num_argument_noise=0.5,
        min_samples=1,
        cluster_selection_method="leaf",
    ):
        num_arg_noise = min(
            max(
                round(num_argument_noise * len(sentences)),
                300,
            ),
            len(ARGUMENT_NOISE),
        )
        argument_noise_sentences = np.random.choice(
            ARGUMENT_NOISE, size=num_arg_noise, replace=False
        )
        cleaned_sentences = [URL_RE.sub("", sent).strip() for sent in sentences]
        sentence_embeddings = self.model(cleaned_sentences)
        noise_embeddings = self.model(argument_noise_sentences)
        (
            reduced_sentence_embeddings,
            reduced_noise_embeddings,
        ) = dimensionality_reduction_with_argument_noise(
            sentence_embeddings=sentence_embeddings,
            noise_embeddings=noise_embeddings,
            n_neighbors=n_neighbors,
            n_components=n_components,
            min_dist=0.0,
            random_state=random_state,
        )
        labels, probabilities = hdbscan_cluster(
            np.concatenate([reduced_sentence_embeddings, reduced_noise_embeddings]),
            min_cluster_size=get_min_cluster_size(
                len(sentences), min_value=15, scale=0.9
            ),
            min_samples=min_samples,
            cluster_selection_method=cluster_selection_method,
            cluster_selection_epsilon=0.0,
        )
        sentence_labels, noise_labels = np.split(
            labels, [len(reduced_sentence_embeddings)]
        )
        sentence_probabilities, _ = np.split(
            probabilities, [len(reduced_sentence_embeddings)]
        )
        classified_as_noise = classify_noise(
            cleaned_sentences, sentence_labels, noise_labels, sentence_probabilities
        )
        return classified_as_noise


class ThreadClusterer:
    def __init__(self):
        self.model = None
        self.argument_noise_classifier = None

    def _lazy_init(self):
        if self.model is None:
            self.model = SBERT()
            self.argument_noise_classifier = ArgumentNoiseClassifier(model=self.model)

    def embed(self, texts):
        self._lazy_init()
        return self.model(texts)

    def classify_noise(self, sentences):
        self._lazy_init()
        return self.argument_noise_classifier(sentences, num_argument_noise=1.0)

    def __call__(
        self,
        thread,
        n_neighbors=30,
        n_components=10,
        min_dist=0.0,
        min_samples=None,
        cluster_selection_method="eom",
        cluster_selection_epsilon=0.0,
        max_number_of_joined_clusters=2,
    ):
        root = thread["root"]
        texts = {root["name"]: root["text"]}
        for post in thread["comments"]:
            texts[post["name"]] = post["text"]
        empty_posts = {}
        non_empty_posts = {}
        for k, v in texts.items():
            if v:
                non_empty_posts[k] = v
            else:
                empty_posts[k] = v
        ids, sents = (
            e.tolist()
            for _, e in pd.DataFrame(non_empty_posts.items(), dtype=object)
            .explode(1)
            .items()
        )
        is_argument_noise = self.classify_noise(sents)
        _argument_noise_sents = np.array(sents, dtype=object)[
            is_argument_noise
        ].tolist()
        _non_argument_noise_sents = np.array(sents, dtype=object)[
            ~is_argument_noise
        ].tolist()
        sentence_embeddings = self.embed(_non_argument_noise_sents)
        _result_posts = [{"text": sent} for sent in _non_argument_noise_sents]
        reduced_sentence_embeddings = dimensionality_reduction(
            embeddings=sentence_embeddings,
            n_neighbors=n_neighbors,
            n_components=n_components,
            min_dist=min_dist,
            random_state=0,
        )
        min_cluster_size = get_min_cluster_size(len(sentence_embeddings), scale=0.9)
        original_sentence_label, probabilities, lambda_values = hdbscan_cluster(
            reduced_sentence_embeddings,
            min_cluster_size=min_cluster_size,
            min_samples=min_samples,
            cluster_selection_method=cluster_selection_method,
            cluster_selection_epsilon=cluster_selection_epsilon,
            max_number_of_joined_clusters=max_number_of_joined_clusters,
            return_lambda_values=True,
        )
        sentence_labels = probabilities.argmax(axis=1)
        for data, original_label, label, prob_array, lambda_value in zip(
            _result_posts,
            original_sentence_label,
            sentence_labels,
            probabilities,
            lambda_values,
        ):
            data["cluster"] = {
                "value": int(label),
                "trueValue": int(label) if original_label != -1 else -1,
                "probability": float(prob_array[label]),
            }
            data["lambda"] = lambda_value
        plot_sentence_embeddings = (
            reduced_sentence_embeddings
            if n_components == 2
            else dimensionality_reduction(
                embeddings=sentence_embeddings,
                n_neighbors=n_neighbors,
                n_components=2,
                min_dist=min_dist,
                random_state=0,
            )
        )
        for data, (x, y) in zip(_result_posts, plot_sentence_embeddings):
            data["x"] = float(x)
            data["y"] = float(y)
        data_df = pd.DataFrame({"id": ids, "data": None}, dtype=object)
        if not _argument_noise_sents:
            data_df["data"] = _result_posts
        else:
            data_df["data"][~is_argument_noise] = _result_posts
            data_df["data"][is_argument_noise] = [
                {"text": sent, "cluster": {"value": -2, "trueValue": -2}}
                for sent in _argument_noise_sents
            ]
        result_posts = dict(data_df.groupby("id").apply(lambda x: x["data"].tolist()))
        result_posts.update(empty_posts)
        assert len(result_posts) == len(texts)
        return result_posts


def result_to_clusters(result):
    clusters = defaultdict(list)
    for post in result.values():
        for e in post:
            clusters[e["cluster"]["trueValue"]].append(e)
    clusters = {key: value for key, value in clusters.items() if key >= 0}
    return clusters
