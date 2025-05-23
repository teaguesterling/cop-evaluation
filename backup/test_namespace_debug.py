"""Debug test for COPNamespace behavior."""

from cop_python.core import COPNamespace
from cop_python.runtime import enable_cop

enable_cop()

# Test COPNamespace behavior
registry = COPNamespace()

# Set a dictionary as an attribute
setattr(registry, "invariant", {})

# Get it back
type_registry = getattr(registry, "invariant")

print(f"Type of registry.invariant: {type(type_registry)}")
print(f"Value: {type_registry}")

# Test if it's still a dictionary
component_id = "test.component"
if component_id not in type_registry:
    type_registry[component_id] = []

print(f"After adding: {type_registry}")

# Test with COPNamespace default factory
registry2 = COPNamespace(default_factory=list)

# Getting a non-existent attribute should create a list
anno_list = registry2.invariant
print(f"\nType of registry2.invariant: {type(anno_list)}")
print(f"Value: {anno_list}")

# Now set it to a dictionary
setattr(registry2, "risk", {})
risk_registry = getattr(registry2, "risk")
print(f"\nType of registry2.risk: {type(risk_registry)}")
print(f"Value: {risk_registry}")