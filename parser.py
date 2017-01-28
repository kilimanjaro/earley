""" A simple implementation of Earley's CFG parsing algorithm, as described
at http://loup-vaillant.fr/tutorials/earley-parsing/

Right now, it recognizes a sequence of tokens (but does not
produce any resulting parse trees). For usage, see test_example. """

from collections import namedtuple

Item = namedtuple('Item', 'lhs done rest i')
Grammar = namedtuple('Grammar', 'rules terminals start')


def initial_item(rule,i=0):
    """ The initial item associated with a grammar rule. """
    lhs,rhs = rule
    return Item(lhs,(),tuple(rhs),i)


def predictions(item,grammar,i):
    """Return the grammar items predicted by the first
unprocessed symbol in item."""
    if item.rest == () or item.rest[0] in grammar.terminals:
        return []
    return [initial_item(rule,i) for rule in grammar.rules
            if rule[0] == item.rest[0]]


def advance(item):
    "Advance one unprocessed symbol in the given item."
    lhs,done,rest,i = item
    return Item(lhs,done+rest[0:1],rest[1:],i)


def completions(item,states):
    """Returns parent items associated with the given item.
Note that if item has unprocessed symbols, then there are no completions."""
    return [advance(prev) for prev in states[item.i]
            if prev.rest != () and prev.rest[0] == item.lhs]


def earley_table(grammar,tokens):
    """ Generates a state table for parsing, using Earley's algorithm. """
    states = []
    items = []
    next_items = [initial_item(rule) for rule in grammar.rules
                  if rule[0] == grammar.start]
    tokens += [""] # sentinel character
    for i,t in enumerate(tokens):
        items,next_items = next_items,[]
        state = set()
        while items:
            item = items.pop(0)
            if item not in state:
                state.add(item)
                if item.rest == ():
                    items += completions(item,states)
                elif item.rest[0] in grammar.terminals and item.rest[0] == t:
                    next_items += [advance(item)]
                else:
                    items += predictions(item,grammar,i)
        states.append(state)
    return states


# helpful for debugging

def itemstring(item):
    """ Pretty print Earley item. """
    lhs,a,b,i = item
    rep = "(%d) %-12s -> %s . %s" % (i,lhs,' '.join(a),' '.join(b))
    return rep

def print_states(states):
    """ Print a state table generated by earley_table. """
    for i,state in enumerate(states):
        print("=== %d ===" % i)
        for item in state:
            print(itemstring(item))
        print("")


def recognizer(grammar,tokens):
    """ Returns true if the sequence of tokens is in the language
generated by the given grammar. """
    states = earley_table(grammar,tokens)
    return final_item(states,grammar) is not None


def final_item(states,grammar):
    """ Returns the final Earley item in a successful parse, 
or None if parse was unsuccessful. """
    for item in states[-1]:
        if item.lhs == grammar.start and item.i == 0 and item.rest == ():
            return item
    return None


def test_example():
    """ An extended example, recognizing arithmetic expressions. """
    
    rules = [('sum', ('sum', '+', 'product')),
             ('sum', ('product',)),
             ('product', ('product', '*', 'factor')),
             ('product', ('factor',)),
             ('factor', ('(', 'sum', ')')),
             ('factor', ('number',)),
             ('number', ('0',)),
             ('number', ('1',))]

    terminals = "01+*()"

    start_state = 'sum'

    simple_grammar = Grammar(rules,terminals,start_state)

    assert(recognizer(simple_grammar, "0 + 1 + 1".split()) == True)
    assert(recognizer(simple_grammar, "1 * ( 1 + 1 )".split()) == True)
    assert(recognizer(simple_grammar, "0 + 1 * 1 ".split()) == True)
    assert(recognizer(simple_grammar, "0 + ( 1 * )".split()) == False)
    


def test():
    rule = ("a",["b"])
    assert(initial_item(rule) == ("a",(),("b",),0))
    assert(initial_item(("a",["bcd"])) == ("a", (), ("bcd",), 0))
    item = Item("a",(),("b",),0)
    assert(advance(item) == Item("a",("b",),(),0))

    rule2 = ("b", ["0"])
    simple_grammar = Grammar([rule,rule2],"0","a")
    assert(predictions(item,simple_grammar,1) == [Item('b',(),('0',),1)])
    assert(predictions(Item('b',(),('0',),0),simple_grammar,0) == [])

    i1,i2 = initial_item(rule), initial_item(rule2)
    i3 = advance(i2)
    states = [[i1,i2], [i3]]
    assert(completions(i3,states) == [Item('a',('b',),(),0)])

    test_example()
    
    return "tests passed!"
