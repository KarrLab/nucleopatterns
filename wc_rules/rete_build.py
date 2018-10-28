from . import rete_nodes as rn
from .utils import BuildError
from collections import defaultdict
from numpy import argmax

# Building the rete-net incremenetally
# the following methods check a node's successors for a particular type of node
# if found, they return it
# if not found, they create it, add it as a successor to current node and return it
def check_attribute_and_add_successor(net,current_node,_class_to_init,attr,value):
    x = [e for e in current_node.successors if getattr(e,attr,None)==value]
    existing_successors = [e for e in x if e.__class__.__name__==_class_to_init.__name__]
    if len(existing_successors)==0:
        new_node = _class_to_init(value)
        net.add_edge(current_node,new_node)
        return new_node
    elif len(existing_successors)==1:
        return list(existing_successors)[0]
    else:
        BuildError('Duplicates on the Rete net. Bad!')
    return None

def add_mergenode(net,node1,node2):
    varnames = tuple(sorted(set(node1.variable_names + node2.variable_names)))
    new_node = rn.merge(varnames)
    net.add_edge(node1,new_node)
    net.add_edge(node2,new_node)
    return new_node

def add_checkTYPE_path(net,current_node,type_vec):
    for (kw,_class) in type_vec:
        current_node = check_attribute_and_add_successor(net,current_node,rn.checkTYPE,'_class',_class)
    return current_node

def add_checkATTR_path(net,current_node,attr_vec):
    new_tuples = sorted([tuple(x[1:]) for x in attr_vec])
    if len(new_tuples)  > 0:
        current_node = check_attribute_and_add_successor(net,current_node,rn.checkATTR,'tuple_of_attr_tuples',tuple(new_tuples))
    return current_node

def add_store(net,current_node,number_of_variables):
    existing_stores = [x for x in current_node.successors if isinstance(x,rn.store)]
    if len(existing_stores) == 1:
        current_node = existing_stores[0]
    elif len(existing_stores) == 0:
        new_node = rn.store(number_of_variables=number_of_variables)
        net.add_edge(current_node,new_node)
        current_node = new_node
    else:
        raise BuildError('Duplicates on the Rete net! Bad!')
    return current_node

def add_alias(net,current_node,keymap,is_not_in=False):
    # keymap = {source_var:target_var}
    _class = rn.alias
    if is_not_in:
        _class = rn.is_not_in
    var = tuple(sorted(keymap.values()))
    current_node = check_attribute_and_add_successor(net,current_node,_class,'variable_names',var)
    for key in keymap:
        current_node.set_keymap(key,keymap[key])
    return current_node

def add_checkEDGE(net,current_node,attr1,attr2):
    attrpair = tuple([attr1,attr2])
    current_node = check_attribute_and_add_successor(net,current_node,rn.checkEDGE,'attribute_pair',attrpair)
    return current_node

def add_mergenode_path(net,list_of_nodes):
    current_node = list_of_nodes.pop(0)
    for node in list_of_nodes:
        new_node = node
        merge_node = add_mergenode(net,current_node,new_node)
        current_node = merge_node
    return current_node

def sort_tuples(vartuples):
    right = vartuples
    left = []
    flatten_left = set()
    tuple_scorer = lambda x,set1: sum(y in set1 for y in x)
    while len(right) > 0:
        max_index = argmax(list(tuple_scorer(x,flatten_left) for x in right))
        elem = right.pop(max_index)
        left.append(elem)
        for x in elem:
            flatten_left.add(x)
    return left

# Main builder method for incrementing rete-net given a pattern
def increment_net_with_pattern(net,pattern,existing_patterns):
    ''' Steps through the queries generated by a pattern and increments the Rete net. '''
    qdict = pattern.generate_queries()
    varnames = sorted(qdict['type'].keys())
    new_varnames = { v:str(pattern.id+':'+v) for v in varnames }
    vartuple_nodes = defaultdict(set)

    for var in varnames:
        # compile types
        type_vec = qdict['type'][var]
        attr_vec = qdict['attr'][var]
        new_varname = new_varnames[var]
        # for each variable (i.e. each node in the pattern)
        # start from root, add checkTYPE(s), checkATTR(s), store and varname_node
        current_node = net.get_root()
        current_node = add_checkTYPE_path(net,current_node,type_vec)
        current_node = add_checkATTR_path(net,current_node,attr_vec)
        current_node = add_store(net,current_node,1)
        keymap = {'node':new_varname}
        current_node = add_alias(net,current_node,keymap)
        vartuple_nodes[(new_varname,)].add(current_node)

    for rel in qdict['rel']:
        # Processes both edges and is_empty relations
        # in an is_empty relation, either var1 or var2 is None
        (kw,var1,attr1,attr2,var2) = rel
        keymap = dict()
        if var1 is not None:
            keymap['node1'] = new_varnames[var1]
        if var2 is not None:
            keymap['node2'] = new_varnames[var2]
        vartuple = tuple(sorted(keymap.values()))
        is_empty = var1 is None or var2 is None

        current_node = net.get_root()
        current_node = add_checkEDGE(net,current_node,attr1,attr2)
        current_node = add_store(net,current_node,2)
        current_node = add_alias(net,current_node,keymap,is_empty)
        vartuple_nodes[vartuple].add(current_node)

    existence_checks = qdict['is_in'] + qdict['is_not_in']
    for item in existence_checks:
        is_not_in = item[0]=='is_not_in'
        target_varlist = [new_varnames[x] for x in item[1][0]]
        source_pattern = item[1][1]
        source_varlist = [source_pattern+':'+x for x in item[1][2]]
        if source_pattern not in existing_patterns:
            raise BuildError('Pattern `'+source_pattern+'` referenced before adding.')
        current_node = existing_patterns[source_pattern]
        keymap = dict(zip(source_varlist,target_varlist))
        current_node = add_alias(net,current_node,keymap,is_not_in)
        vartuple_nodes[tuple(sorted(target_varlist))].add(current_node)

    vartuple_nodes2 = dict()
    for vartuple, nodeset in vartuple_nodes.items():
        if len(nodeset) > 1:
            current_node = add_mergenode_path(net,sorted(nodeset))
            vartuple_nodes2[vartuple] = current_node
        if len(nodeset) == 1:
            vartuple_nodes2[vartuple] = list(nodeset)[0]

    sorted_vartuples = sort_tuples(sorted(vartuple_nodes2))
    sorted_nodes = list(vartuple_nodes2[x] for x in sorted_vartuples)
    current_node = add_mergenode_path(net,sorted_nodes)
    return current_node
