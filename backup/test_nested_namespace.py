"""Test nested COPNamespace behavior."""

from cop_python.core import COPNamespace
from cop_python.runtime import enable_cop

enable_cop()

# Test nested COPNamespace
registry = COPNamespace(default_factory=COPNamespace)

print(f"Registry type: {type(registry)}")

# Access invariant - should create a COPNamespace
invariant_registry = registry.invariant
print(f"\nType of registry.invariant: {type(invariant_registry)}")
print(f"Is it a COPNamespace? {isinstance(invariant_registry, COPNamespace)}")

# Try to use it like a dictionary
try:
    invariant_registry["component_id"] = []
    print("\nSuccessfully used dictionary-style assignment")
except Exception as e:
    print(f"\nFailed with: {type(e).__name__}: {e}")

# Try attribute style
component_list = invariant_registry.component_id
print(f"\nType of invariant_registry.component_id: {type(component_list)}")
print(f"Value: {component_list}")

# Can we append to it?
component_list.append("test_record")
print(f"After append: {component_list}")

# Does it persist?
print(f"Getting again: {invariant_registry.component_id}")

# What about a factory that creates dict?
print("\n--- Testing with dict factory ---")
registry2 = COPNamespace(default_factory=dict)
type_registry = registry2.invariant
print(f"Type of registry2.invariant: {type(type_registry)}")

# Can we use it as a dict?
type_registry["component_id"] = []
print(f"After assignment: {type_registry}")