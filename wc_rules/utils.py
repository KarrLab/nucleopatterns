"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""
import uuid
import random
import math

import itertools,functools,collections,operator


############ functional programming
def merge_lists(list_of_lists):
    return list(itertools.chain(*list_of_lists))

def merge_dicts(list_of_dicts):
    # ensure keys dont overlap
    return dict(collections.ChainMap(*list_of_dicts))

def no_overlaps(list_of_iters):
    joint_set = set.union(*[set(x) for x in list_of_iters])
    return len(joint_set) == len(merge_lists(list_of_iters))

def pipe_map(operations,inputs):
    if len(operations)==0:
        return inputs
    #item = list_of_operations.pop(0)
    return pipe_map(operations[1:],map(operations[0],inputs))

def listmap(op,inputs):
    return list(map(op,inputs))

def split_string(s,sep='\n'):
    return [y for y in [x.strip() for x in s.split(sep)] if len(y)>0]

def grouper(n,inputs):
    # assume len(input) is a multiple of n:
    # grouper(2,[1,2,3,4,5,6]) -> [[1,2],[3,4],[5,6]]
    return [inputs[n*i:n*i+n] for i in range(0,len(inputs)//n)]

# Seed for creating ids
# To modify this seed, load utils module, then execute utils.idgen.seed(<new_seed>)
idgen = random.Random()
idgen.seed(0)

###### Methods ######
def iter_to_string(iterable):
    return '\n'.join([str(x) for x in list(iterable)])

def generate_id():
    return str(uuid.UUID(int=idgen.getrandbits(128)))

def print_as_tuple(x):
    if isinstance(x,str):
        return x
    if isinstance(x,tuple):
        return '(' + ','.join((print_as_tuple(y) for y in x)) + ')'
    if isinstance(x,list):
        return '[' + ','.join((print_as_tuple(y) for y in x)) + ']'
    return str(x)

def listify(x):
    if isinstance(x,list): 
        return x
    return [x]

def subdict(d,keys):
    return {k:d[k] for k in keys}


def strgen(n,template='abcdefgh'):
    # the +0.01 is to handle the case when n==0
    digits = math.ceil((math.log(n) + 0.01)/math.log(len(template)))
    enumerator = enumerate(itertools.product(template,repeat=digits))
    return list(''.join(x) for i,x in enumerator if i<n)

def concat(LL):
    return [x for L in LL for x in L if x]

def printvars(vars,vals,sep=',',breakline=False):
    strs = ['{x}={y}'.format(x=x,y=y) for x,y in zip(vars,vals)]
    return sep.join(strs)

def invert_dict(_dict):
    out = collections.defaultdict(list)
    for k,v in _dict.items():
        out[v].append(k)
    return dict(out)

def verify_list(_list,_types):
    if not isinstance(_list,list):
        return isinstance(_list,_types)
    return all([verify_list(elem,_types) for elem in _list]) 

    
###### Error ######
class GenericError(Exception):

    def __init__(self, msg=None):
        if msg is None:
            msg = ''
        super(GenericError, self).__init__(msg)

class ReteNetworkError(GenericError):pass

class IndexerError(GenericError):pass
class SlicerError(GenericError):pass

class ValidateError(GenericError):pass

class BuildError(GenericError):
    pass

class AddError(GenericError):
    pass


class RemoveError(GenericError):
    pass


class SetError(GenericError):
    pass


class FindError(GenericError):
    pass

class SeqError(GenericError):
    pass

class ParseExpressionError(GenericError):pass

class AddObjectError(Exception):

    def __init__(self, parentobject, currentobject, allowedobjects, methodname='add()'):
        msg = '\nObject of type ' + self.to_str(currentobject) + ' cannot be added to ' + \
            self.to_str(parentobject) + ' using ' + methodname + '. '
        if (len(allowedobjects) == 1 or isinstance(allowedobjects, str)):
            msg2 = str(allowedobjects)
        else:
            msg2 = ', '.join(allowedobjects)
        msg = msg + 'Only objects of type ' + msg2 + ' are allowed for this method.'
        super(AddObjectError, self).__init__(msg)

    @staticmethod
    def to_str(obj):
        msg = str(type(obj))
        msg = ''.join(filter(lambda ch: ch not in "<>", msg))
        return msg


class RemoveObjectError(Exception):

    def __init__(self, parentobject, currentobject, allowedobjects, methodname='remove()', notfound=False):
        if notfound == False:
            msg = '\nObject of type ' + self.to_str(currentobject) + ' cannot be removed from ' + \
                self.to_str(parentobject) + ' using ' + methodname + '. '
            if (len(allowedobjects) == 1 or isinstance(allowedobjects, str)):
                msg2 = str(allowedobjects)
            else:
                msg2 = ', '.join(allowedobjects)
            msg = msg + 'Only objects of type ' + msg2 + ' are allowed for this method.'
        else:
            msg = '\nObject ' + self.to_str(currentobject) + ' not found!'
        super(AddObjectError, self).__init__(msg)

    @staticmethod
    def to_str(obj):
        msg = str(type(obj))
        msg = ''.join(filter(lambda ch: ch not in "<>", msg))
        return msg
