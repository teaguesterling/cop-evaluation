from concept_python import intent, invariant, human_decision, ai_implement


class Animal:
    """COP Annotations:
@intent("Represent animals and their behaviors")"""

    def __init__(self, name, species):
        self.name = name
        self.species = species

    def make_sound(self):
        """COP Annotations:
@intent("Produce the sound characteristic of this animal")"""
        return 'Some generic animal sound'


class Dog(Animal):
    """COP Annotations:
@intent("Represent dog-specific attributes and behaviors")"""

    def __init__(self, name, breed):
        super().__init__(name, 'Dog')
        self.breed = breed

    def make_sound(self):
        """COP Annotations:
@intent("Produce a dog's barking sound")
@invariant("Must return a string representing a bark")"""
        return 'Woof!'

    def fetch(self, item):
        """COP Annotations:
@intent("Simulate a dog fetching an item")"""
        return f'{self.name} fetched the {item}!'


class Cat(Animal):
    """COP Annotations:
@intent("Represent cat-specific attributes and behaviors")"""

    def __init__(self, name, color):
        super().__init__(name, 'Cat')
        self.color = color

    def make_sound(self):
        """COP Annotations:
@intent("Produce a cat's meowing sound")
@invariant("Must return a string representing a meow")"""
        return 'Meow!'

    def scratch(self):
        """COP Annotations:
@intent("Simulate a cat scratching")"""
        return f'{self.name} scratches!'
