# tests/test_runtime.py
import unittest
import threading
from cop_python.runtime import (
    COPSystem, StandardCOPSystem, TracingCOPSystem, 
    COPNamespace, get_system, set_system,
    enable_cop, disable_cop, enable_cop_tracing, DISABLED,
    SourceInfo, TraceEntry, _current_system
)

class TestCOPNamespace(unittest.TestCase):
    """Test the COPNamespace class."""
    
    def test_attribute_access(self):
        """Test that attributes are created with default values."""
        namespace = COPNamespace()
        
        # Access a non-existent attribute
        test_list = namespace.test_attr
        
        # Should create a new empty list
        self.assertEqual(test_list, [])
        self.assertIs(namespace.test_attr, test_list)
        
    def test_attribute_assignment(self):
        """Test that attributes can be assigned."""
        namespace = COPNamespace()
        namespace.test_attr = "value"
        self.assertEqual(namespace.test_attr, "value")
        
    def test_dictionary_access(self):
        """Test dictionary-style access."""
        namespace = COPNamespace()
        value = namespace["test_attr"]
        self.assertEqual(value, [])
        
    def test_keys_values_items(self):
        """Test keys, values, and items methods."""
        namespace = COPNamespace()
        namespace.attr1 = [1, 2, 3]
        namespace.attr2 = [4, 5, 6]
        
        self.assertEqual(set(namespace.keys()), {"attr1", "attr2"})
        self.assertEqual(sorted(namespace.get_all()), [1, 2, 3, 4, 5, 6])
        
class TestStandardCOPSystem(unittest.TestCase):
    """Test the StandardCOPSystem class."""
    
    def setUp(self):
        self.system = StandardCOPSystem()
        set_system(self.system)

    def test_set_system(self):
        """Test that the system can be set"""
        self.assertTrue(get_system() is self.system)
        
    def test_is_enabled(self):
        """Test that the system is enabled."""
        self.assertTrue(self.system.is_enabled())
        
    def test_is_tracing(self):
        """Test that standard system doesn't trace."""
        self.assertFalse(self.system.is_tracing())
        
    def test_push_pop_context(self):
        """Test pushing and popping context."""
        context_value = "test_value"
        
        # Push a context
        self.system.push_context("test_context", context_value)
        
        # Get the context
        contexts = self.system.get_contexts("test_context")
        self.assertEqual(contexts, [context_value])
        
        # Pop the context
        popped = self.system.pop_context("test_context")
        self.assertEqual(popped, context_value)
        
        # Context should be empty now
        contexts = self.system.get_contexts("test_context")
        self.assertEqual(contexts, [])
        
    def test_get_current_context(self):
        """Test getting the current (most recent) context."""
        self.system.push_context("test_context", "value1")
        self.system.push_context("test_context", "value2")
        
        current = self.system.get_current_context("test_context")
        self.assertEqual(current, "value2")
        
    def test_thread_local_storage(self):
        """Test that contexts are thread-local."""
        self.system.push_context("test_context", "main_thread")
        
        other_thread_value = [None]  # Use a list to store value from other thread
        
        def other_thread():
            # This thread should have its own empty context
            contexts = self.system.get_contexts("test_context")
            other_thread_value[0] = contexts
            
        thread = threading.Thread(target=other_thread)
        thread.start()
        thread.join()
        
        # Main thread should have its context
        main_contexts = self.system.get_contexts("test_context")
        self.assertEqual(main_contexts, ["main_thread"])
        
        # Other thread should have its own empty context
        self.assertEqual(other_thread_value[0], [])

class TestTracingCOPSystem(unittest.TestCase):
    """Test the TracingCOPSystem class."""
    
    def setUp(self):
        self.system = TracingCOPSystem()
        
    def test_is_tracing(self):
        """Test that tracing system does trace."""
        self.assertTrue(self.system.is_tracing())
        
    def test_get_source_info(self):
        """Test getting source information."""
        # Need to skip 0 frames to get info about this function
        source_info = self.system.get_source_info(skip_frames=0)
        
        # Source info should include current file and function
        self.assertIsInstance(source_info, SourceInfo)
        self.assertIn("test_runtime.py", source_info.file)
        self.assertEqual(source_info.function, "test_get_source_info")
        
    def test_trace_recording(self):
        """Test that traces are recorded."""
        # Push a context to generate a trace
        self.system.push_context("test_context", "test_value")
        
        # Get the traces
        traces = self.system.get_traces()
        
        # Should have one trace
        self.assertEqual(len(traces), 1)
        
        # Verify trace properties
        trace = traces[0]
        self.assertIsInstance(trace, TraceEntry)
        self.assertEqual(trace.action, "enter_context")
        self.assertEqual(trace.annotation_type, "test_context")

class TestGlobalFunctions(unittest.TestCase):
    """Test the global system management functions."""
    
    def tearDown(self):
        # Reset to disabled after each test
        disable_cop()
        
    def test_get_set_system(self):
        """Test getting and setting the system."""
        # Initially should be disabled
        system = get_system()
        self.assertIs(system, DISABLED)
        
        # Set a new system
        new_system = StandardCOPSystem()
        set_system(new_system)
        
        # Should now be the new system
        system = get_system()
        self.assertIs(system, new_system)
        
    def test_enable_disable_cop(self):
        """Test enabling and disabling COP."""
        # Initially should be disabled
        self.assertIs(get_system(), DISABLED)
        
        # Enable COP
        enable_cop()
        self.assertIsInstance(get_system(), StandardCOPSystem)
        
        # Disable COP
        disable_cop()
        self.assertIs(get_system(), DISABLED)
        
    def test_enable_cop_tracing(self):
        """Test enabling COP with tracing."""
        enable_cop_tracing()
        self.assertIsInstance(get_system(), TracingCOPSystem)

if __name__ == "__main__":
    unittest.main()
