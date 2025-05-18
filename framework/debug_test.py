from cop_python.runtime import StandardCOPSystem

system = StandardCOPSystem()

# Push a context
print("Before push, contexts:", hasattr(system.thread_contexts, "contexts"))
system.push_context("test_context", "test_value")
print("After push, contexts exists:", hasattr(system.thread_contexts, "contexts"))

# Access contexts directly
print("Direct access to contexts:", system.contexts)
print("Direct access to test_context:", system.contexts.test_context)

# Get the context using get_contexts
contexts = system.get_contexts("test_context")
print("get_contexts result:", contexts)
print("Type of result:", type(contexts))

# Check what's in the namespace
print("\nNamespace contents:")
for key in system.contexts.keys():
    print(f"  {key}: {getattr(system.contexts, key)}")