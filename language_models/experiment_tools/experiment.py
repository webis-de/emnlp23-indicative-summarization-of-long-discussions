from client import LLMClient, OpenAIClient

from .template import Template


class Experiment:
    def __init__(
        self,
        client,
        name,
        template,
        bias=None,
        skip=[],
        client_kwargs={},
        extra_arguments={},
    ):
        self.client = client
        self.client_meta = client.meta()
        self.name = name
        self.template = (
            template.copy(ensure_complete=True)
            if isinstance(template, Template)
            else Template(template)
        )
        self.is_chat = hasattr(self.client, "is_chat") and self.client.is_chat
        supports_bias = bias is not None and not self.is_chat
        if supports_bias:
            self.template.append(bias)
        self.bias = bias if supports_bias else None
        self.skip = skip
        self.client_kwargs = client_kwargs
        self.extra_arguments = extra_arguments

    def meta(self):
        return {
            **self.client_meta,
            "name": (self.major, self.minor),
            "is_openai": isinstance(self.client, OpenAIClient),
        }

    def get_name(self):
        major, minor = self.name
        if minor is not None:
            return f"{major}.{minor}"
        return major

    def __call__(
        self, input, format_items={}, ensure_complete=True, verbose=False, **kwargs
    ):
        client_kwargs = self.client_kwargs.copy()
        client_kwargs.update(kwargs)
        template = self.template.copy(ensure_complete=ensure_complete).format(
            format_items
        )
        if self.is_chat:
            batch = (str(template), input)
        else:
            batch = str(template.format({"input": input}))
        result, meta = self.client(batch, **client_kwargs, with_meta=True)
        generated = result["generated"]
        if verbose:
            size = result["size"]
            overflow = size["overflow"]
            input_size = size["input"]
            output_size = size["output"]
            model_max_length = meta["model_max_length"]
            size_generated = input_size + output_size + overflow
            print(model_max_length, size_generated, input_size, output_size, overflow)
            if "stopping_reason" in result:
                stopping_reason = result["stopping_reason"]
                print(f"stopping_reason: {stopping_reason}")
        if self.bias is not None:
            generated = self.bias + generated
        return generated


class Experiments:
    def __init__(self, experiments, host=None, api_key=None):
        self.experiments = experiments
        self.host = host
        self.api_key = api_key

    def get_experiment_args(self, experiment):
        major, *minor = experiment.split(".")
        minor = ".".join(minor)
        if not minor:
            minor = None
        meta = self.experiments[major]
        return {
            "name": (
                major,
                minor,
            ),
            "is_openai": meta["model"].lower() in OpenAIClient.MODELS,
            "meta": meta,
            "kwargs": meta["experiments"][minor],
        }

    def get(self, experiment, **kwargs):
        args = self.get_experiment_args(experiment)
        experiment_kwargs = args["kwargs"]
        name = args["name"]
        experiment_kwargs["template"] = Template(experiment_kwargs["template"]).format(
            {"instruction": experiment_kwargs.pop("instruction")}
        )
        if args["is_openai"]:
            client = OpenAIClient(
                model=args["meta"]["model"].lower(), api_key=self.api_key
            )
        else:
            client = LLMClient(model=name[0], host=self.host)
        experiment_kwargs.update(kwargs)
        return Experiment(client, name, **experiment_kwargs)
