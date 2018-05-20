"""
:Author: John Sekar <johnarul.sekar@gmail.com>
:Date: 2017-12-13
:Copyright: 2017, Karr Lab
:License: MIT
"""

from wc_rules import base
from wc_rules import variables


class Entity(base.BaseClass):

    def __init__(self, **kwargs):
        super(Entity, self).__init__(**kwargs)
        attrdict = self.attribute_properties

        vardict = self.get_variable_dict()
        for attrname in vardict:
            self.attribute_properties[attrname]['variable'] = vardict[attrname]

    @classmethod
    def get_classnames(cls):
        classnames = []
        x = cls
        while x.__name__ is not 'Entity':
            classnames.append(x.__name__)
            x = x.__bases__[0]
        return classnames
