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
        self._blarg_children = out
        return out

    def parse_args(self, *args, **kwargs):
        if hasattr(self, '_blarg_children'):
            assert False, dict(self._blarg_children._get_kwargs())['choices']
        namespace = super(BlargParser, self).parse_args(*args, **kwargs)

      # if hasattr(self, '_blarg_children'):
      #     print(self._blarg_children)
      # for func in self._all_aggregates():
      #     print(func)
      #     func(namespace)

        return namespace

    def _all_aggregates(self):
       #yield self._aggregates
        parent = self
        if hasattr(parent, '_blarg_children'):
            for child in dict(parent._blarg_children_get_kwargs())['choices'].values():
                print(child)
       #        yield from child._all_aggregates()
