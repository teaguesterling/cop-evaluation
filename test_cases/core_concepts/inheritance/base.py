# test_cases/core_concepts/inheritance/base.py
class Animal:
    def __init__(self, name, species):
        self.name = name
        self.species = species
        
    def make_sound(self):
        return "Some generic animal sound"
        
class Dog(Animal):
    def __init__(self, name, breed):
        super().__init__(name, "Dog")
        self.breed = breed
        
    def make_sound(self):
        return "Woof!"
        
    def fetch(self, item):
        return f"{self.name} fetched the {item}!"
        
class Cat(Animal):
    def __init__(self, name, color):
        super().__init__(name, "Cat")
        self.color = color
        
    def make_sound(self):
        return "Meow!"
        
    def scratch(self):
        return f"{self.name} scratches!"
