import argparse

class BlargParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(BlargParser, self).__init__(*args, **kwargs)
        self._aggregates = []
        self._aggregate_dests = set()

    def add_aggregate(self, dest = None, func = lambda args:None):
        if dest:
            if dest in self._aggregate_dests:
                raise AttributeError('Aggregate named %s already exists' % dest)
            elif not isinstance(dest, str):
                raise TypeError('Aggregate dest must be str type.')
            else:
                self._aggregate_dests.add(dest)
                def g(args):
                    setattr(args, dest, func(args))
        else:
            g = func

        self._aggregates.append(g)

    def add_subparsers(self, **kwargs):
        out = super(BlargParser, self).add_subparsers(**kwargs)
        self._blarg_subparsers = out
        return out

    def parse_args(self, *args, **kwargs):
        namespace = super(BlargParser, self).parse_args(*args, **kwargs)

        if hasattr(self, '_blarg_subparsers'):
            for subparser in dict(self._blarg_subparsers._get_kwargs())['choices'].values():
                for func in subparser._aggregates:
                    func(namespace)

        for func in self._aggregates:
            func(namespace)
        return namespace
