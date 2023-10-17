from .safe_format import SafeFormatter


class Template:
    def __init__(self, template, ensure_complete=True):
        self.template = template
        self.ensure_complete = ensure_complete

    def copy(self, ensure_complete=None):
        ensure_complete = (
            ensure_complete if ensure_complete is not None else self.ensure_complete
        )
        return Template(self.template, ensure_complete=ensure_complete)

    def append(self, string):
        self.template += string

    def format(self, items, raise_unused=True):
        self.template = SafeFormatter(raise_unused=raise_unused).format(
            self.template, **items
        )
        return self

    def raw(self):
        return self.template

    def __repr__(self):
        return self.template

    def __str__(self):
        if self.ensure_complete:
            self.template.format()
        return self.template
