from abc import ABCMeta, abstractmethod

'''
    Classes for named and simple entity
'''


class Entity:
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_entity_name(self):
        pass


'''
    Subclass for named entities
'''


class NamedEntity(Entity):
    def __init__(self, named_entity):
        self.entity = named_entity

    def get_entity_name(self):
        return self.entity


'''
    Subclass for non-named entities
'''


class SimpleEntity(Entity):
    def __init__(self, simple_entity):
        self.entity = simple_entity

    def get_entity_name(self):
        return self.entity
