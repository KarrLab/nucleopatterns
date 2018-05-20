""" Language for describing whole-cell models

:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from obj_model import core
from wc_rules import graph_utils
from wc_rules import utils
import uuid
import random


# Seed for creating ids
# To modify this seed, load base module, then execute base.idgen.seed(<new_seed>)
idgen = random.Random()
idgen.seed(0)

###### Structures ######
class BaseClass(core.Model):
    """ Base class for bioschema objects.

    Attributes:
        id (:obj:`str`): unique id that can be used to pick object from a list

    Properties:
        label (:obj:`str`): name of the leaf class from which object is created
    """
    id = core.StringAttribute(primary=True, unique=True)
    attribute_properties = dict()

    class GraphMeta(graph_utils.GraphMeta):
        outward_edges = tuple()
        semantic = tuple()

    def __init__(self, **kwargs):
        super(BaseClass, self).__init__(**kwargs)
        if 'id' not in kwargs.keys():
            self.id = str(uuid.UUID(int=idgen.getrandbits(128)))

        self.attribute_properties = self.make_attribute_properties_dict()

    def make_attribute_properties_dict(self):
        attrdict = dict()
        cls = self.__class__

        def populate_attribute(attrname, attr, check='related_class'):
            x = {'related': False, 'append': False, 'related_class': None}
            if check == 'related_class' and hasattr(attr, 'related_class'):
                x['related'] = True
                x['related_class'] = attr.related_class
                if isinstance(attr, (core.OneToManyAttribute, core.ManyToManyAttribute,)):
                    x['append'] = True
            elif check == 'primary_class' and hasattr(attr, 'primary_class'):
                x['related'] = True
                x['related_class'] = attr.primary_class
                if isinstance(attr, (core.ManyToManyAttribute, core.ManyToOneAttribute,)):
                    x['append'] = True
            return x

        for attrname, attr in cls.Meta.attributes.items():
            attrdict[attrname] = dict()
            attrdict[attrname].update(populate_attribute(attrname, attr, 'related_class'))
        for attrname, attr in cls.Meta.related_attributes.items():
            if attrname not in attrdict:
                attrdict[attrname] = dict()
            attrdict[attrname].update(populate_attribute(attrname, attr, 'primary_class'))

        return attrdict

    def set_id(self, id):
        """ Sets id attribute.

        Args:
            id (:obj:`str`)

        Returns:
            self
        """
        self.id = id
        return self

    def get_id(self): return self.id

    @property
    def label(self):
        """ Name of the leaf class from which object is created.
        """
        return self.__class__.__name__

    ##### Graph Methods #####
    def get_graph(self, recurse=True, memo=None):
        return graph_utils.get_graph(self, recurse=recurse, memo=memo)

    @property
    def graph(self):
        return self.get_graph(recurse=True)
