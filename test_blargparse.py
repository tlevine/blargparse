import argparse

import pytest

import blargparse

def get_blargparser(left, right):
    blargparser = blargparse.BlargParser()
    blargparser.add_argument('--force', '-F', action = 'store_true')
    blargparser.add_argument('--left', '-l', type = int, default = left)
    blargparser.add_argument('--right', '-r', type = int, default = right)
    return blargparser

def make_range(args):
    return range(args.left, args.right)

def make_range_mutate(args):
    args.numbers = range(args.left, args.right)

def make_range_and_delete(args):
    r = make_range(args)
    del(args.left, args.right)
    return r

testcases_aggregates = [
    (get_blargparser(0, 1000), 'range', make_range, {'range'}),
    (get_blargparser(0, 1000), None, make_range_mutate, set()),
]

@pytest.mark.parametrize('blargparser, dest, func, expected_aggregates', testcases_aggregates)
def test_add_aggregate(blargparser, dest, func, expected_aggregates):
    blargparser.add_aggregate(dest, func = func)
    assert blargparser._aggregate_dests == expected_aggregates

def test_aggregate_dest():
    bp = get_blargparser(0, 100)
    bp.add_aggregate(func = lambda:None)
    bp.add_aggregate('two', lambda:None)
    bp.add_aggregate(dest = 'three', func = lambda:None)
    with pytest.raises(TypeError):
        bp.add_aggregate(4, func = lambda:None)
    bp.add_aggregate(dest = None, func = lambda:None)

def test_parse_args_args():
    bp = get_blargparser(0, 100)
    bp.add_aggregate('range', make_range_and_delete)
    expected = argparse.Namespace(range = range(0, 100), force = False)
    assert bp.parse_args([]) == expected

def test_parse_args_kwargs():
    bp = get_blargparser(0, 100)
    bp.add_aggregate(dest = 'range', func = make_range_and_delete)
    expected = argparse.Namespace(range = range(0, 100), force = False)
    assert bp.parse_args([]) == expected

def test_parse_args_collision():
    bp = get_blargparser(0, 10)
    bp.add_aggregate('something', lambda x:None)
    with pytest.raises(AttributeError):
        bp.add_aggregate('something', lambda:3)

def test_parse_args_mutate():
    bp = get_blargparser(0, 10)
    bp.add_aggregate('range1', make_range_and_delete)
    bp.add_aggregate('range2', make_range_and_delete)
    with pytest.raises(AttributeError):
        bp.parse_args([])

def test_subparser():
    bp = blargparse.BlargParser()
    sps = bp.add_subparsers(dest = 'command')
    sp = sps.add_parser('abc')
    assert hasattr(sp, 'add_aggregate')

    sp.add_argument('--numerator', '-n', type = float, default = 10.0)
    sp.add_argument('--denominator', '-d', type = float, default = 4.0)
    sp.add_aggregate('frac', lambda args:args.numerator/args.denominator)

    assert sp.parse_args([]).frac == 2.5
    blargs = bp.parse_args(['abc'])
    assert blargs.command == 'abc'
    assert hasattr(blargs, 'frac')
    assert blargs.frac == 2.5

def test_subsubparser():
    zero = blargparse.BlargParser()
    one = zero.add_subparsers(dest = 'one').add_parser('aa')
    two = one.add_subparsers(dest = 'two').add_parser('bb')
    assert hasattr(two, 'add_aggregate')

    two.add_argument('--numerator', '-n', type = float, default = 10.0)
    two.add_argument('--denominator', '-d', type = float, default = 4.0)
    two.add_aggregate('frac', lambda args:args.numerator/args.denominator)

    assert two.parse_args([]).frac == 2.5
    blargs = zero.parse_args(['aa', 'bb'])
    assert blargs.one == 'aa'
    assert blargs.two == 'bb'
    assert hasattr(blargs, 'frac')
    assert blargs.frac == 2.5

def test_multiple_subparsers():
    bp = blargparse.BlargParser()
    sps = bp.add_subparsers(dest = 'command')

    a = sps.add_parser('a')
    a.add_argument('--aaa', '-a')
    a.add_aggregate('AAA', lambda args:args.aaa.upper())

    b = sps.add_parser('b')
    b.add_argument('--bbb', '-b')
    a.add_aggregate('BBB', lambda args:args.bbb.upper())

    assert bp.parse_args([]) == argparse.Namespace(command = None)
    assert bp.parse_args(['a', '--aaa', 'tom']) == argparse.Namespace(command = None, aaa = 'tom', AAA = 'TOM')
