# test_cases/core_concepts/inheritance/cop.py
from concept_python import intent, invariant, human_decision, ai_implement

@intent("Represent animals and their behaviors")
class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        
    @intent("Produce the sound characteristic of this animal")
    def make_sound(self):
        return "Some generic animal sound"
        
@intent("Represent dog-specific attributes and behaviors")
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Dog")
        self.breed = breed
        
    @intent("Produce a dog's barking sound")
    @invariant("Must return a string representing a bark")
    def make_sound(self):
        return "Woof!"
        
    @intent("Simulate a dog fetching an item")
    def fetch(self, item):
        return f"{self.name} fetched the {item}!"
        
@intent("Represent cat-specific attributes and behaviors")
class Cat(Animal):
    def __init__(self, name, color):
        super().__init__(name, "Cat")
        self.color = color
        
    @intent("Produce a cat's meowing sound")
    @invariant("Must return a string representing a meow")
    def make_sound(self):
        return "Meow!"
        
    @intent("Simulate a cat scratching")
    def scratch(self):
        return f"{self.name} scratches!"
