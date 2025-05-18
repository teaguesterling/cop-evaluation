"""Debug script to test COPAnnotation issues"""

from cop_python.runtime import enable_cop
from cop_python.core import COPAnnotation

# Enable the system first
enable_cop()

# Create a simple annotation
class TestAnnotation(COPAnnotation):
    annotation_type = "test"

try:
    # Create an annotation
    annotation = TestAnnotation("test value")
    print(f"Created annotation: {annotation}")
    
    # Apply to a function
    @annotation
    def test_function():
        pass
    
    print(f"Applied to function: {test_function}")
    print(f"Function annotations: {getattr(test_function, '__cop_annotations__', 'None')}")
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()