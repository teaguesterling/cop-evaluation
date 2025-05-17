import importlib
import inspect
import threading
import datetime
from typing import Any, Dict, List, Optional, Union, NamedTuple


class SourceInfo(NamedTuple):
    """Source code location information."""
    file: str                      # Source file path
    line: int                      # Line number
    function: str                  # Function name
    module: Optional[str] = None   # Module name (optional)


class TraceEntry(NamedTuple):
    """Structured representation of a trace entry."""
    action: str                               # Action performed (enter_context, exit_context)
    annotation_type: str                      # Type of annotation (intent, risk, etc.)
    timestamp: str                            # ISO-format timestamp
    source_info: Optional[SourceInfo] = None  # Source location information
    args: Optional[Tuple] = None              # Annotation arguments (if available)
    kwargs: Optional[Dict[str, Any]] = {}     # Annotation keyword arguments
    extras: Optional[Dict[str, Any]] = {}     # Additional trace-specific information
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trace entry to dictionary format for serialization."""
        result = self._asdict()
        # Convert nested SourceInfo to dict if present
        if self.source_info:
            result["source_info"] = self.source_info._asdict()
        return result
        

class COPSystem:
    """Base class for COP system implementations."""
    
    def is_enabled(self) -> bool:
        """Check if the system is enabled."""
        raise NotImplementedError()
    
    def is_tracing(self) -> bool:
        """Check if the system is tracing source positions."""
        raise NotImplementedError()
    
    def get_source_info(self, skip_frames: int = 1) -> Optional[SourceInfo]:
        """Get source information for the current call site."""
        raise NotImplementedError()
    
    def push_context(self, context_type: str, context: Any) -> None:
        """Push a context to its stack."""
        raise NotImplementedError()
    
    def pop_context(self, context_type: str) -> None:
        """Pop a context from its stack."""
        raise NotImplementedError()
    
    def get_contexts(self, context_type: str) -> List:
        """Get all contexts of a specific type."""
        raise NotImplementedError()


class NoOpCOPSystem(COPSystem):
    """COP system that does nothing (disabled mode)."""
    
    def is_enabled(self) -> bool:
        """Check if the system is enabled."""
        return False

    def is_tracing(self) -> bool:
        """Check if the system is tracing source positions."""
        return False

    def get_source_info(self, skip_frames: int = 1) -> Optional[SourceInfo]:
        """Placeholder for source information for the current call site."""
        return None
    
    def push_context(self, context_type: str, context: Any) -> None:
        """No-op implementation."""
        pass
    
    def pop_context(self, context_type: str) -> None:
        """No-op implementation."""
        pass
    
    def get_contexts(self, context_type: str) -> List:
        """Return empty list."""
        return []


class StandardCOPSystem(COPSystem):
    """Standard COP system implementation."""
    
    def __init__(self):
        """Initialize the COP system."""
        self.contexts = threading.local()

    
    def is_enabled(self) -> bool:
        """Check if the system is enabled."""
        return True

    def is_tracing(self) -> bool:
        """Check if the system is tracing source positions."""
        return False

    def get_source_info(self, skip_frames: int = 1) -> Optional[SourceInfo]:
        """Placeholder for source information for the current call site."""
        return None
    
    def push_context(self, context_type: str, context: Any) -> None:
        """Push a context to its stack."""
        stack_name = f"{context_type}_stack"
        if not hasattr(self.contexts, stack_name):
            setattr(self.contexts, stack_name, [])
        
        stack = getattr(self.contexts, stack_name)
        stack.append(context)
    
    def pop_context(self, context_type: str) -> None:
        """Pop a context from its stack."""
        stack_name = f"{context_type}_stack"
        if hasattr(self.contexts, stack_name):
            stack = getattr(self.contexts, stack_name)
            if stack:
                stack.pop()
    
    def get_contexts(self, context_type: str) -> List:
        """Get all contexts of a specific type."""
        stack_name = f"{context_type}_stack"
        if hasattr(self.contexts, stack_name):
            return getattr(self.contexts, stack_name)
        return []


class TracingCOPSystem(StandardCOPSystem):
    """COP system with tracing capabilities."""
    
    def __init__(self):
        """Initialize the tracing COP system."""
        super().__init__()
        self.traces = []
    
    def is_tracing(self) -> bool:
        """Check if the system is in tracing mode."""
        return True

    def get_source_info(self, skip_frames: int = 1) -> Dict:
        """
        Get source information for the current call site.
        
        Args:
        skip_frames: Number of frames to skip, not including this function
            - Use 1 for immediate caller (default)
            - Use 2 for context manager 
            - Use 3 for annotation initialization
                       
        Returns:
            Dict with source info
        """
        # Get the appropriate frame based on skip_frames
        frame = inspect.currentframe()
        for _ in range(skip_frames + 1):  # +1 for this function's frame
            if frame is None:
                break
            frame = frame.f_back
            
        if frame is None:
            return {}
            
        # Extract the source info
        frame_info = inspect.getframeinfo(frame)
        module_name = None
        if frame.f_globals and "__name__" in frame.f_globals:
            module_name = frame.f_globals["__name__"]
            
        return SourceInfo(
            file=frame_info.filename,
            line=frame_info.lineno,
            function=frame_info.function,
            module=module_name
        )
    
    def push_context(self, context_type: str, context: Any) -> None:
        """Push a context to its stack with tracing."""
        super().push_context(context_type, context)
        
        # Get source info with appropriate frame skipping
        source_info = self.get_source_info(skip_frames=2)  # Skip push_context and caller
        self._add_trace("enter_context", context_type, context, source_info)
    
    def pop_context(self, context_type: str) -> None:
        """Pop a context from its stack with tracing."""
        stack_name = f"{context_type}_stack"
        context = None
        
        if hasattr(self.contexts, stack_name):
            stack = getattr(self.contexts, stack_name)
            if stack:
                context = stack[-1]  # Get the context before popping
        
        super().pop_context(context_type)
        
        if context:
            # Get source info with appropriate frame skipping
            source_info = self.get_source_info(skip_frames=2)  # Skip pop_context and caller
            self._add_trace("exit_context", context_type, context, source_info)
    
        def _add_trace(self, action: str, annotation_type: str, 
                  annotation: Any, source_info: SourceInfo) -> None:
        """
        Add a trace entry.
        
        Args:
            action: Action being performed
            annotation_type: Type of annotation
            annotation: The annotation object
            source_info: Source location information
        """
        # Extract annotation details if available
        args = getattr(annotation, "args", None)
        kwargs = getattr(annotation, "kwargs", {})
        
        # Create the trace entry
        trace = TraceEntry(
            action=action,
            annotation_type=annotation_type,
            timestamp=datetime.datetime.now().isoformat(),
            source_info=source_info,
            args=args,
            kwargs=kwargs
        )
        
        self.traces.append(trace)
    
    def get_traces(self, as_dict: bool = False) -> Union[List[TraceEntry], List[Dict]]:
        """
        Get the collected traces.
        
        Args:
            as_dict: Whether to convert traces to dictionary format
            
        Returns:
            List of TraceEntry objects or dictionaries
        """
        if as_dict:
            return [trace.to_dict() for trace in self.traces]
        return self.traces


DISABLED = NoOpCOPSystem()
ENABLED = StandardCOPSystem()

_current_system = DISABLED


def get_system() -> COPSystem:
    """Get the current COP system."""
    return _current_system


def set_system(system: COPSystem) -> None:
    """Set the current COP system."""
    global _current_system
    _current_system = system


def enable_cop() -> None:
    """Enable COP annotations."""
    set_system(STANDARD)


def enable_cop_tracing() -> None:
    """Enable COP annotations with tracing."""
    set_system(TRACING)


def disable_cop() -> None:
    """Disable COP annotations."""
    set_system(DISABLED)


def resolve_component(component: Union[Any, str], 
                     base_module: Optional[str] = None) -> Any:
    """
    Resolve a component from an object or dotted path string.
    
    Args:
        component: The component to resolve. Can be an actual object or a 
                  dotted path string (e.g., "module.submodule.component")
        base_module: Optional base module to use for relative imports
        
    Returns:
        The resolved component object
        
    Raises:
        ValueError: If the component cannot be resolved
        
    Examples:
        # Resolve from object (returns the same object)
        resolve_component(process_payment)
        
        # Resolve from absolute path
        resolve_component("payment_system.process_payment")
        
        # Resolve from relative path with base module
        resolve_component("process_payment", base_module="payment_system")
    """
    # If component is already an object (not a string), return it directly
    if not isinstance(component, str):
        return component
    
    try:
        # Handle relative imports with base_module
        if base_module and '.' not in component:
            full_path = f"{base_module}.{component}"
        else:
            full_path = component
        
        # Split into module path and attribute name
        if '.' in full_path:
            module_path, attr_name = full_path.rsplit('.', 1)
            
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the attribute from the module
            resolved = getattr(module, attr_name)
            return resolved
        else:
            # It's just a module name
            return importlib.import_module(full_path)
            
    except (ImportError, AttributeError, ValueError) as e:
        raise ValueError(f"Could not resolve component path '{component}': {e}")
