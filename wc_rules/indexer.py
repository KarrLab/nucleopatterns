"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2018-05-21
:Copyright: 2018, Karr Lab
:License: MIT
"""
from wc_rules import utils
class Slicer(dict):
    ''' A hashmap between keys (literals or namedtuples) and Boolean values.
    Slicers are used for composing logical expressions and subsetting Indexers.

    Slicers have the following dict-like operations:
        [key]                 returns the value of key
        update(dict_obj)      updates the hashmap

    A slicer is a positive slicer if,
        it returns a value of True for any key it contains
        it returns a default value of False for any other key.
    A slicer is a negative slicer if,
        it returns a value of False for any key it contains
        it returns a default value of True for any other key.
    To create a positive slicer, call Slicer(default=False)
    To create a negative slicer, call Slicer(default=True)

    Note: A slicer does not make a claim about an existence of an object.
    That should be managed externally using Indexers.

    The operators & | ~ are overloaded to mean key-wise AND, OR, and NOT respectively.
    With slicers I & J,
    I & J returns True for any key for which that both I and J will return True.
    I | J returns True for any key for which either I or J will return True.
    ~I returns True for any key for which I returns False, and vice versa.

    When & | ~ mixes positive & negative slicers, deMorgan's laws are used to determine the output/
    Let A , A' denote positive & negative slicers matching corresponding sets of objects on a Venn diagram.
    Similarly, B, B' ...
    The following hold:
        A & B   = a positive slicer corresponding to intersection(A,B)
        A & B'  = a positive slicer corresponding to A - intersection(A,B)
        A' & B  = a positive slicer corresponding to B - intersection(A,B)
        A' & B' = a negative slicer corresponding to complement(union(A,B))
        A | B   = a positive slicer corresponding to union(A,B)
        A | B'  = a negative slicer corresponding to complement(B - intersection(A,B))
        A' | B  = a negative slicer corresponding to complement(A - intersection(A,B))
        A' | B' = a negative slicer corresponding to complement(intersection(A,B))
        ~A  = a negative slicer corresponding to complement(A)
        ~~A = a positive slicer corresponds to A
    '''
    def __init__(self,default=False):
        if not isinstance(default,bool):
            raise utils.SlicerError('`default` argument must be bool.')
        self.default = default

    def __getitem__(self,key):
        if key in self:
            return dict.__getitem__(self,key)
        return self.default

    def add_keys(self,keys):
        for key in keys:
            self[key] = not self.default
        return self

    def delete_keys(self,keys):
        for key in keys:
            self.pop(key)
        return self

    def update(self,dict_obj):
        not_default = not self.default
        keys = (key for key in dict_obj if dict_obj[key] is not_default)
        self.add_keys(keys)
        keys = (key for key in dict_obj if dict_obj[key] is self.default)
        keys1 = (key for key in keys if key in self)
        self.delete_keys(keys1)
        return self

    def union(self,other):
        if self.default != other.default:
            raise utils.SlicerError('Cannot merge positive and negative slicers.')
        keys = set(self.keys()) | set(other.keys())
        return Slicer(default=self.default).add_keys(keys)

    def intersection(self,other):
        if self.default != other.default:
            raise utils.SlicerError('Cannot intersect positive and negative slicers.')
        keys = set(self.keys()) & set(other.keys())
        return Slicer(default=self.default).add_keys(keys)

    def __and__(self,other):
        [x1,x2] = sorted([self,other],key=len)
        if self.default==other.default==False:
            return x1.intersection(x2)
        elif self.default==other.default==True:
            return x2.union(x1)
        elif self.default==False:
            keys = (key for key in self if other[key])
            return Slicer(default=False).add_keys(keys)
        return other & self

    def __or__(self,other):
        [x1,x2] = sorted([self,other],key=len)
        if self.default==other.default==False:
            return x2.union(x1)
        elif self.default==other.default==True:
            return x1.intersection(x2)
        elif self.default==True:
            keys = (key for key in self if not other[key])
            return Slicer(default=True).add_keys(keys)
        return other | self

    def __invert__(self):
        return Slicer(default= not self.default).add_keys(self.keys())

class Indexer(dict):
    primitive_type = None

    def __init__(self):
        self.value_cache = {}
        self.last_updated = set()

    # Internal methods
    def value_is_compatible(self,value):
        if self.primitive_type is not None:
            if not isinstance(value,self.primitive_type):
                raise utils.IndexerError('Value is not compatible with indexer type')
        return True

    def delete_key_from_value_cache(self,key):
        value = self[key]
        self.value_cache[value].pop(key)
        if len(self.value_cache[value])==0:
            self.value_cache.pop(value)
        return self

    def add_key_to_value_cache(self,key,value):
        if value not in self.value_cache:
            self.value_cache[value] = Slicer(default=False)
        self.value_cache[value].add_keys([key])
        return self

    def update_last_updated(self,key):
        self.last_updated.add(key)
        return self

    # Methods available externally
    def update(self,dict_obj):
        for key,value in dict_obj.items():
            if key in self and self[key]==value: continue
            self.value_is_compatible(value)
            if key in self: self.delete_key_from_value_cache(key)
            self[key] = value
            self.add_key_to_value_cache(key,value)
            self.update_last_updated(key)
        return self

    def remove(self,keylist):
        keys = (key for key in keylist if key in self)
        for key in keylist:
            self.delete_key_from_value_cache(key)
            self.pop(key)
            self.update_last_updated(key)
        return self

    def flush(self):
        self.last_updated.clear()
        return self

class BooleanIndexer(Indexer):
    primitive_type=bool
