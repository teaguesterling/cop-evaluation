"""Debug verification issue."""

from cop_python.runtime import enable_cop, disable_cop
from cop_python.testing.verification import _get_verification_registry, clear_verification_registry
from cop_python.core import COPNamespace
from cop_python.utils import COPAnnotationReference
from cop_python.testing.foundation import COPTestData

enable_cop()
clear_verification_registry()

def test_func():
    pass

def component_func():
    pass

annotation_ref = COPAnnotationReference(
    annotation_type="invariant",
    annotation_value="Must be valid",
    metadata_keys={}
)

test_data = COPTestData(
    test_id="test.module.test_func",
    annotation_reference=annotation_ref,
    test_metadata={},
    source_info=None
)

# Get the registry
registry = _get_verification_registry()
print(f"Initial registry type: {type(registry)}")
print(f"Initial registry dir: {dir(registry)}")

# Initialize if needed
anno_type = annotation_ref.annotation_type
print(f"\nChecking for '{anno_type}' attribute...")
if not hasattr(registry, anno_type):
    print(f"Creating '{anno_type}' attribute as dict")
    setattr(registry, anno_type, {})

type_registry = getattr(registry, anno_type)
print(f"\nType of registry.{anno_type}: {type(type_registry)}")
print(f"Value: {type_registry}")

# Use component_id as key for better lookup
component_id = "test.module.component_func"
print(f"\nChecking if '{component_id}' in type_registry...")
if component_id not in type_registry:
    print(f"Adding empty list for '{component_id}'")
    type_registry[component_id] = []

print(f"\nFinal type_registry: {type_registry}")

disable_cop()