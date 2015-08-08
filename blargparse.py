import argparse

class BlargParser(argparse.ArgumentParser):
    def __init__(self, *args, **kwargs):
        super(BlargParser, self).__init__(*args, **kwargs)
        self._aggregates = {}

    def add_aggregate(self, dest, func = lambda args:None):
        if dest in self._aggregates:
            raise AttributeError('aggregate named %s already exists' % dest)
        else:
            self._aggregates[dest] = func

    def parse_args(self, *args, **kwargs):
        namespace = super(BlargParser, self).parse_args(*args, **kwargs)
        for dest, func in self._aggregates.items():
            setattr(namespace, dest, func(namespace))
        return namespace
