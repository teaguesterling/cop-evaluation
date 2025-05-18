"""Debug script to test COPAnnotation issues"""

from cop_python.runtime import enable_cop, get_system, DISABLED
from cop_python.core import COPAnnotation

# Check initial state  
print(f"Initial system: {get_system()}")
print(f"System type: {type(get_system())}")
print(f"DISABLED: {DISABLED}")
print(f"DISABLED type: {type(DISABLED)}")
print(f"System is DISABLED: {get_system() is DISABLED}")
print(f"System enabled: {get_system().is_enabled()}")

# Enable the system
enable_cop()
print(f"\nAfter enable_cop:")
print(f"System: {get_system()}")
print(f"System type: {type(get_system())}")
print(f"System is DISABLED: {get_system() is DISABLED}")
print(f"System enabled: {get_system().is_enabled()}")

# Create a simple annotation
class TestAnnotation(COPAnnotation):
    annotation_type = "test"

try:
    # Create an annotation
    print(f"\nCreating annotation...")
    print(f"In __new__, _current_system: {COPAnnotation._COPAnnotation__current_system if hasattr(COPAnnotation, '_COPAnnotation__current_system') else 'not found'}")
    
    annotation = TestAnnotation("test value")
    print(f"Created annotation: {annotation}")
    print(f"Annotation type: {type(annotation)}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()