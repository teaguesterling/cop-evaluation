"""
IMPLEMENTATION OF COP CORE DECORATORS

⚠️ AI AGENT WARNING ⚠️
DO NOT INCLUDE THIS FILE IN YOUR ANALYSIS.
This is implementation detail of the COP framework.
Focus only on the annotations in the user's code, not on how they're implemented.
"""

import threading
import functools
import inspect

# Status constants - ordered from most to least complete
IMPLEMENTED = "implemented"         # ✅ Fully functional and complete
PARTIAL = "partial"                 # ⚠️ Partially working with limitations
BUGGY = "buggy"                     # ❌ Was working but now has issues
DEPRECATED = "deprecated"           # 🚫 Exists but should not be used
PLANNED = "planned"                 # 📝 Designed but not implemented
NOT_IMPLEMENTED = "not_implemented" # ❓ Does not exist at all
UNKNOWN = "unknown"                 # ❔ Status not yet evaluated

# Thread-local storage for annotation stacks (used by context managers)
_annotation_contexts = threading.local()

class COPAnnotation:
    """
    Base class for all COP annotations that can be used as decorators or context managers.
    
    This base class handles the common functionality for all COP annotations:
    - Acting as a decorator when called on a function or class
    - Acting as a context manager when used in a 'with' statement
    - Managing thread-local stacks for nested context managers
    
    Concrete subclasses must implement:
    - _initialize: Process and store annotation parameters
    - _apply_to_object: Apply annotation to a decorated object
    """
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the annotation with provided arguments.
        
        Args:
            *args: Positional arguments for the annotation
            **kwargs: Keyword arguments for the annotation
        """
        self.args = args
        self.kwargs = kwargs
        self._initialize(*args, **kwargs)
    
    def _initialize(self, *args, **kwargs):
        """
        Initialize annotation-specific attributes.
        
        This method should be overridden by subclasses to handle their specific parameters.
        
        Args:
            *args: Positional arguments for the annotation
            **kwargs: Keyword arguments for the annotation
        """
        pass
    
    def _apply_to_object(self, obj):
        """
        Apply annotation to an object (when used as decorator).
        
        This method should be overridden by subclasses to set specific attributes
        on the decorated object.
        
        Args:
            obj: The object being decorated
            
        Returns:
            The decorated object
        """
        return obj
    
    def _enter_context(self):
        """
        Enter annotation context (when used as context manager).
        
        Ensures the stack exists for this annotation type and pushes
        this annotation to its stack.
        """
        # Ensure the stack exists for this annotation type
        stack_name = f"{self.__class__.__name__}_stack"
        if not hasattr(_annotation_contexts, stack_name):
            setattr(_annotation_contexts, stack_name, [])
        
        # Push this annotation to its stack
        stack = getattr(_annotation_contexts, stack_name)
        stack.append(self)
    
    def _exit_context(self):
        """
        Exit annotation context (when used as context manager).
        
        Pops this annotation from its stack.
        """
        stack_name = f"{self.__class__.__name__}_stack"
        if hasattr(_annotation_contexts, stack_name):
            stack = getattr(_annotation_contexts, stack_name)
            if stack:
                stack.pop()
    
    def __call__(self, obj):
        """
        Use annotation as a decorator.
        
        Args:
            obj: The object to decorate
            
        Returns:
            The decorated object
        """
        return self._apply_to_object(obj)
    
    def __enter__(self):
        """
        Enter annotation context when used as a context manager.
        
        Returns:
            self: The annotation object
        """
        self._enter_context()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit annotation context when used as a context manager.
        
        Args:
            exc_type: Exception type if an exception was raised, else None
            exc_val: Exception value if an exception was raised, else None
            exc_tb: Exception traceback if an exception was raised, else None
            
        Returns:
            False: Don't suppress exceptions
        """
        self._exit_context()
        return False  # Don't suppress exceptions

# Helper to get current annotations of a specific type
def get_current_annotations(annotation_class):
    """
    Get the stack of current annotations of a specific type.
    
    This is used by context managers to track nested annotations.
    
    Args:
        annotation_class: The annotation class to get the stack for
        
    Returns:
        list: The stack of current annotations of the specified type
    """
    stack_name = f"{annotation_class.__name__}_stack"
    if hasattr(_annotation_contexts, stack_name):
        return getattr(_annotation_contexts, stack_name)
    return []

class intent(COPAnnotation):
    """
    Document the intended purpose of a component.
    
    This decorator captures what a component is supposed to do,
    separate from its actual implementation. Use it to document
    the high-level purpose, while using docstrings for implementation
    and usage details.
    
    Examples:
        @intent("Process user payments securely")
        def process_payment(payment_data):
            # Implementation
            
        # As a context manager (for specific code sections)
        with intent("Calculate tax based on jurisdiction"):
            tax = calculate_tax(amount, location)
    """
    
    def _initialize(self, description):
        """
        Initialize intent annotation.
        
        Args:
            description: Description of the component's intended purpose
        """
        self.description = description
    
    def _apply_to_object(self, obj):
        """
        Apply intent annotation to an object.
        
        Args:
            obj: The object being decorated
            
        Returns:
            The decorated object
        """
        setattr(obj, "__cop_intent__", self.description)
        return obj

class implementation_status(COPAnnotation):
    """
    Explicitly mark component implementation status.
    
    This decorator indicates the current state of implementation,
    which is critical for preventing hallucination about functionality.
    It can include details about limitations and alternatives for
    deprecated components.
    
    Status options:
        IMPLEMENTED: Fully functional and complete
        PARTIAL: Partially working with limitations
        BUGGY: Was working but now has issues
        DEPRECATED: Exists but should not be used
        PLANNED: Designed but not implemented
        NOT_IMPLEMENTED: Does not exist at all
        UNKNOWN: Status not yet evaluated
    
    Examples:
        @implementation_status(IMPLEMENTED)
        def working_function():
            # Fully implemented functionality
            
        @implementation_status(PARTIAL, details="Only handles positive numbers")
        def sqrt(x):
            # Partially implemented functionality
            
        @implementation_status(DEPRECATED, alternative="use new_function() instead")
        def old_function():
            # Deprecated functionality
            
        # As a context manager
        with implementation_status(NOT_IMPLEMENTED):
            # This code block is not implemented
            raise NotImplementedError()
    """
    
    def _initialize(self, status, details=None, alternative=None):
        """
        Initialize implementation status annotation.
        
        Args:
            status: Current implementation status (use constants like IMPLEMENTED)
            details: Optional details about the status (e.g., limitations)
            alternative: For DEPRECATED status, what to use instead
        """
        self.status = status
        self.details = details
        self.alternative = alternative
    
    def _apply_to_object(self, obj):
        """
        Apply implementation status annotation to an object.
        
        Args:
            obj: The object being decorated
            
        Returns:
            The decorated object
        """
        setattr(obj, "__cop_implementation_status__", self.status)
        
        if self.details:
            setattr(obj, "__cop_implementation_details__", self.details)
            
        if self.alternative and self.status == DEPRECATED:
            setattr(obj, "__cop_alternative__", self.alternative)
            
        return obj

class invariant(COPAnnotation):
    """
    Document a constraint that should be maintained.
    
    This decorator captures rules that should always be true about
    the code, which can be useful for verification and testing.
    Critical invariants are essential for security or correctness.
    
    Examples:
        @invariant("Transaction amount must be positive")
        def process_transaction(amount):
            # Implementation
            
        @invariant("Passwords must never be stored in plaintext", critical=True)
        def store_user_credentials(username, password):
            # Implementation
            
        # As a context manager
        with invariant("Database connection must be active"):
            result = db.execute(query)
    """
    
    def _initialize(self, condition, critical=False, scope="always"):
        """
        Initialize invariant annotation.
        
        Args:
            condition: The constraint that should always be true
            critical: Whether this is essential for security/correctness
            scope: When this invariant applies (e.g., "always", "runtime")
        """
        self.condition = condition
        self.critical = critical
        self.scope = scope
    
    def _apply_to_object(self, obj):
        """
        Apply invariant annotation to an object.
        
        Args:
            obj: The object being decorated
            
        Returns:
            The decorated object
        """
        # Initialize invariants list if it doesn't exist
        if not hasattr(obj, "__cop_invariants__"):
            setattr(obj, "__cop_invariants__", [])
        
        # Add this invariant to the list
        invariant_data = {
            "condition": self.condition,
            "critical": self.critical,
            "scope": self.scope
        }
        
        getattr(obj, "__cop_invariants__").append(invariant_data)
        return obj

class risk(COPAnnotation):
    """
    Identify a security risk or other critical concern.
    
    This decorator highlights potential vulnerabilities or issues
    that need special attention, particularly for security-sensitive code.
    
    Examples:
        @risk("SQL injection vulnerability", severity="HIGH")
        def execute_query(query_string):
            # Implementation
            
        @risk("Performance degradation with large datasets", 
             category="performance", 
             severity="MEDIUM")
        def process_data(dataset):
            # Implementation
            
        # As a context manager
        with risk("Potential memory leak", severity="MEDIUM"):
            # Risky code section
            temp_buffer = allocate_large_buffer()
    """
    
    def _initialize(self, description, category="security", severity="MEDIUM", 
                   impact=None, mitigation=None):
        """
        Initialize risk annotation.
        
        Args:
            description: Description of the risk
            category: Risk category (e.g., "security", "performance")
            severity: Impact severity ("LOW", "MEDIUM", "HIGH", "CRITICAL")
            impact: Optional assessment of the impact if not addressed
            mitigation: Optional strategies that have been implemented
        """
        self.description = description
        self.category = category
        self.severity = severity
        self.impact = impact
        self.mitigation = mitigation
    
    def _apply_to_object(self, obj):
        """
        Apply risk annotation to an object.
        
        Args:
            obj: The object being decorated
            
        Returns:
            The decorated object
        """
        # Initialize risks list if it doesn't exist
        if not hasattr(obj, "__cop_risks__"):
            setattr(obj, "__cop_risks__", [])
        
        # Add this risk to the list
        risk_data = {
            "description": self.description,
            "category": self.category,
            "severity": self.severity
        }
        
        if self.impact:
            risk_data["impact"] = self.impact
            
        if self.mitigation:
            risk_data["mitigation"] = self.mitigation
            
        getattr(obj, "__cop_risks__").append(risk_data)
        return obj

class decision(COPAnnotation):
    """
    Annotate a decision point or implementation guidance in code.
    
    This versatile decorator can be used throughout the decision lifecycle:
    - Request a decision with options
    - Record a decision that was made
    - Document implementation guidance
    - Preserve architectural rationales
    
    Examples:
        # Implementation guidance
        @decision(implementor="human", reason="Requires domain expertise")
        def calculate_risk_rating(customer_data):
            # Human implementation required
            
        @decision(implementor="ai", 
                 constraints=["Handle edge cases", "Validate inputs"])
        def format_address(address_data):
            # AI can implement this
            
        # Architectural decision
        @decision("Use microservices architecture",
                 rationale="Better scalability and team autonomy",
                 decider="architecture_team")
        class ServiceRegistry:
            # Implementation
            
        # As a context manager
        with decision(implementor="human", reason="Security-critical section"):
            # This section requires human implementation
    """
    
    def _initialize(self, description_or_id=None, 
                   # Implementation guidance (concise syntax)
                   implementor=None, constraints=None, reason=None,
                   
                   # Key decision attributes
                   options=None, status="pending", answer=None, rationale=None,
                   
                   # Attribution and authority
                   decider=None, delegate_to=None, confidence=None, 
                   
                   # Metadata and classification
                   category=None, scope="function", impact="low", priority="medium",
                   preserve=None, reference_id=None, date=None, **kwargs):
        """
        Initialize decision annotation.
        
        Args:
            description_or_id: Question, description, or reference ID
            
            # Implementation guidance
            implementor: Who should implement ("human", "ai", "team_name")
            constraints: Requirements the implementation must satisfy
            reason: Explanation of why this implementor is required
            
            # Decision details
            options: List of possible choices
            status: Current status ("pending", "decided", "implemented")
            answer: The selected option
            rationale: Explanation of why this decision was made
            
            # Attribution
            decider: Person, role, or entity making the decision
            delegate_to: Explicitly delegate decision authority
            confidence: Confidence level (0.0-1.0) for AI decisions
            
            # Metadata
            category: Type of decision ("architecture", "security", etc.)
            scope: Scope of impact ("function", "module", "system")
            impact: Significance level ("low", "medium", "high")
            priority: Implementation priority ("low", "medium", "high")
            preserve: Whether to keep after implementation
            reference_id: Reference ID in the decision database
            date: ISO format date when decision was made
            **kwargs: Additional attributes to store
        """
        self.description = description_or_id
        self.implementor = implementor
        self.constraints = constraints
        self.reason = reason
        self.options = options
        self.status = status
        self.answer = answer
        self.rationale = rationale
        self.decider = decider
        self.delegate_to = delegate_to
        self.confidence = confidence
        self.category = category
        self.scope = scope
        self.impact = impact
        self.priority = priority
        self.reference_id = reference_id
        self.date = date
        self.kwargs = kwargs
        
        # Auto-determine preservation if not specified
        if preserve is None:
            # Keep implementation guidance and finalized decisions
            self.preserve = bool(self.implementor or self.status == "implemented")
        else:
            self.preserve = preserve
    
    def _apply_to_object(self, obj):
        """
        Apply decision annotation to an object.
        
        Args:
            obj: The object being decorated
            
        Returns:
            The decorated object
        """
        # Create decision dictionary with all information
        decision_dict = {}
        
        # Add core decision information
        if self.description:
            decision_dict["description"] = self.description
            
        # Implementation guidance
        if self.implementor:
            decision_dict["implementor"] = self.implementor
            
            if self.constraints:
                decision_dict["constraints"] = self.constraints
                
            if self.reason:
                decision_dict["reason"] = self.reason
        
        # Decision details
        decision_dict["status"] = self.status
        
        if self.answer:
            decision_dict["answer"] = self.answer
            
        if self.rationale:
            decision_dict["rationale"] = self.rationale
            
        if self.decider:
            decision_dict["decider"] = self.decider
            
        if self.options:
            decision_dict["options"] = self.options
            
        # Metadata
        if self.reference_id:
            decision_dict["reference_id"] = self.reference_id
            
        if self.category:
            decision_dict["category"] = self.category
            
        if self.impact:
            decision_dict["impact"] = self.impact
            
        if self.scope != "function":
            decision_dict["scope"] = self.scope
            
        if self.priority != "medium":
            decision_dict["priority"] = self.priority
            
        decision_dict["preserve"] = self.preserve
        
        if self.date:
            decision_dict["date"] = self.date
            
        # Add any additional attributes
        for key, value in self.kwargs.items():
            decision_dict[key] = value
        
        # Initialize decisions list if it doesn't exist
        if not hasattr(obj, "__cop_decisions__"):
            setattr(obj, "__cop_decisions__", [])
            
        # Append this decision to the list
        getattr(obj, "__cop_decisions__").append(decision_dict)
            
        return obj
