"""
CONCEPT-ORIENTED PROGRAMMING (COP) - EXTENDED IMPLEMENTATION

This module extends the core COP functionality with additional utilities,
introspection tools, and comprehensive examples. It serves as both a reference
implementation and a practical toolkit for applying COP in real-world code.

CONTENTS:
1. EXTENDED DECORATORS - Additional annotation capabilities
2. INTROSPECTION TOOLS - Utilities for analyzing COP annotations
3. DOCUMENTATION TOOLS - Generate documentation from COP annotations
4. VALIDATION TOOLS - Verify consistency between annotations and implementations
5. PRACTICAL EXAMPLES - Real-world examples of COP usage
6. HALLUCINATION PREVENTION - Detailed techniques for preventing AI hallucination

Import core annotations from cop_python.py:
    from cop_python import intent, invariant, human_decision, ai_implement, 
                           not_implemented, partially_implemented

    # Basic usage
    @intent("Process payment securely")
    @invariant("Payment amount must be positive")
    def process_payment(amount):
        # Implementation

Import extended functionality from this module:
    from cop_extended import roadmap, deprecated, requires, cop_check,
                             generate_documentation, verify_implementation

    # Extended usage
    @roadmap(milestone="Q4 2023", owner="Payment Team")
    @requires(["PaymentGateway", "Logger"])
    def process_international_payment(amount, currency):
        # Implementation
"""

from enum import Enum
import inspect
import functools
import sys
import textwrap
import warnings
from typing import List, Dict, Any, Optional, Callable, Union, TypeVar, Set, Tuple

# Import core COP annotations
from cop_python import (
    intent, invariant, human_decision, ai_implement, 
    not_implemented, partially_implemented,
    IMPLEMENTED, PARTIAL, PLANNED, NOT_IMPLEMENTED
)

# Additional implementation status constants
DEPRECATED = "deprecated"
IN_PROGRESS = "in_progress"


#-----------------------------------------------------------
# 1. EXTENDED DECORATORS
#-----------------------------------------------------------

@intent("Document implementation timeline and ownership")
def roadmap(milestone=None, planned_date=None, priority=None, owner=None):
    """
    Document implementation roadmap information.
    
    This decorator provides detailed information about when and how
    a component will be implemented, helping set appropriate expectations
    and track development progress.
    
    Args:
        milestone: Development milestone (e.g., "Sprint 5", "Q3 Release")
        planned_date: Expected implementation date 
        priority: Implementation priority ("high", "medium", "low")
        owner: Person or team responsible for implementation
        
    Example:
        @roadmap(milestone="Sprint 5", priority="high", owner="Auth Team")
        @not_implemented("Scheduled for next quarter")
        def enhanced_authentication():
            pass
    """
    def decorator(obj):
        setattr(obj, "__cop_roadmap__", {
            "milestone": milestone,
            "planned_date": planned_date,
            "priority": priority,
            "owner": owner
        })
        return obj
    return decorator


@intent("Mark a component as deprecated")
def deprecated(reason, alternative=None, removal_version=None):
    """
    Mark a component as deprecated.
    
    This decorator indicates that while functionality exists, it is
    scheduled for removal and should not be used in new code.
    
    Args:
        reason: Why the component is being deprecated
        alternative: Recommended alternative approach
        removal_version: When this will be removed
        
    Example:
        @deprecated("Security vulnerability", alternative="use secure_login()")
        def login(username, password):
            # Implementation
    """
    def decorator(obj):
        setattr(obj, "__cop_implementation_status__", DEPRECATED)
        setattr(obj, "__cop_deprecation_reason__", reason)
        setattr(obj, "__cop_deprecation_alternative__", alternative)
        setattr(obj, "__cop_deprecation_removal__", removal_version)
        
        # Add runtime warning when function is called
        if callable(obj):
            @functools.wraps(obj)
            def wrapper(*args, **kwargs):
                warning_msg = f"DEPRECATED: {obj.__qualname__} - {reason}"
                if alternative:
                    warning_msg += f". Use {alternative} instead"
                warnings.warn(warning_msg, DeprecationWarning, stacklevel=2)
                return obj(*args, **kwargs)
            return wrapper
        return obj
    return decorator


@intent("Document dependencies required by a component")
def requires(dependencies, optional=None):
    """
    Document dependencies required by a component.
    
    This decorator makes explicit what other components are required
    for this component to function correctly.
    
    Args:
        dependencies: List of required dependencies
        optional: List of optional dependencies
        
    Example:
        @requires(["DatabaseConnection", "Logger"])
        def save_user_data(user):
            # Implementation
    """
    def decorator(obj):
        setattr(obj, "__cop_dependencies__", dependencies)
        setattr(obj, "__cop_optional_dependencies__", optional or [])
        return obj
    return decorator


@intent("Mark components that are in active development")
def in_progress(developer=None, started_date=None, expected_completion=None):
    """
    Mark a component as currently being implemented.
    
    This indicates that implementation has started but is not yet complete.
    
    Args:
        developer: Person implementing this component
        started_date: When implementation began
        expected_completion: Expected completion date
        
    Example:
        @in_progress(developer="Alex", expected_completion="2023-06-15")
        def feature_under_development():
            # Partial implementation
    """
    def decorator(obj):
        setattr(obj, "__cop_implementation_status__", IN_PROGRESS)
        setattr(obj, "__cop_developer__", developer)
        setattr(obj, "__cop_started_date__", started_date)
        setattr(obj, "__cop_expected_completion__", expected_completion)
        return obj
    return decorator


@intent("Enhance a method with pre and post conditions")
def ensures(pre_conditions=None, post_conditions=None):
    """
    Define pre and post conditions for a method.
    
    This decorator explicitly states what conditions should be true
    before and after the method executes.
    
    Args:
        pre_conditions: Conditions that must be true before execution
        post_conditions: Conditions that must be true after execution
        
    Example:
        @ensures(
            pre_conditions=["account must exist", "amount must be positive"],
            post_conditions=["balance is updated", "transaction is logged"]
        )
        def withdraw(account, amount):
            # Implementation
    """
    def decorator(obj):
        setattr(obj, "__cop_pre_conditions__", pre_conditions or [])
        setattr(obj, "__cop_post_conditions__", post_conditions or [])
        return obj
    return decorator


#-----------------------------------------------------------
# 2. INTROSPECTION TOOLS
#-----------------------------------------------------------

@intent("Get all COP metadata from an object")
def get_cop_metadata(obj) -> Dict[str, Any]:
    """
    Extract all COP-related metadata from an object.
    
    Args:
        obj: The object to analyze (function, class, or module)
        
    Returns:
        Dictionary containing all COP metadata
        
    Example:
        metadata = get_cop_metadata(my_function)
        print(f"Intent: {metadata['intent']}")
        print(f"Status: {metadata['implementation_status']}")
    """
    # Base metadata (always check for these)
    metadata = {
        "intent": getattr(obj, "__cop_intent__", None),
        "implementation_status": getattr(obj, "__cop_implementation_status__", IMPLEMENTED),
        "invariants": getattr(obj, "__cop_invariants__", []),
    }
    
    # Decision point info
    if getattr(obj, "__cop_decision_point__", False):
        metadata["decision_point"] = {
            "description": getattr(obj, "__cop_decision_description__", None),
            "roles": getattr(obj, "__cop_decision_roles__", None)
        }
    
    # AI implementation info
    if getattr(obj, "__cop_ai_implemented__", False):
        metadata["ai_implementation"] = {
            "description": getattr(obj, "__cop_implementation_description__", None),
            "constraints": getattr(obj, "__cop_constraints__", [])
        }
    
    # Add implementation details based on status
    status = metadata["implementation_status"]
    
    if status == NOT_IMPLEMENTED:
        metadata["not_implemented"] = {
            "reason": getattr(obj, "__cop_implementation_reason__", None),
            "issue_id": getattr(obj, "__cop_issue_id__", None)
        }
    
    elif status == PARTIAL:
        metadata["partial_implementation"] = {
            "details": getattr(obj, "__cop_partial_details__", None)
        }
    
    elif status == DEPRECATED:
        metadata["deprecation"] = {
            "reason": getattr(obj, "__cop_deprecation_reason__", None),
            "alternative": getattr(obj, "__cop_deprecation_alternative__", None),
            "removal_version": getattr(obj, "__cop_deprecation_removal__", None)
        }
    
    elif status == IN_PROGRESS:
        metadata["in_progress"] = {
            "developer": getattr(obj, "__cop_developer__", None),
            "started_date": getattr(obj, "__cop_started_date__", None),
            "expected_completion": getattr(obj, "__cop_expected_completion__", None)
        }
    
    # Other metadata
    if hasattr(obj, "__cop_roadmap__"):
        metadata["roadmap"] = getattr(obj, "__cop_roadmap__")
    
    if hasattr(obj, "__cop_dependencies__"):
        metadata["dependencies"] = {
            "required": getattr(obj, "__cop_dependencies__", []),
            "optional": getattr(obj, "__cop_optional_dependencies__", [])
        }
    
    if hasattr(obj, "__cop_pre_conditions__") or hasattr(obj, "__cop_post_conditions__"):
        metadata["conditions"] = {
            "pre_conditions": getattr(obj, "__cop_pre_conditions__", []),
            "post_conditions": getattr(obj, "__cop_post_conditions__", [])
        }
    
    return metadata


@intent("Find all components of a specific type in a module")
def find_components(module, implementation_status=None, component_type=None) -> List[Dict[str, Any]]:
    """
    Find components with specific characteristics in a module.
    
    Args:
        module: The module to search in
        implementation_status: Filter by implementation status
        component_type: Filter by type (function, class, method)
        
    Returns:
        List of dictionaries with component info
        
    Example:
        # Find all components marked as not implemented
        todo_list = find_components(my_module, implementation_status=NOT_IMPLEMENTED)
    """
    results = []
    
    # Helper to process a component
    def process_component(name, obj, parent=None):
        if not name.startswith("_") or name.startswith("__cop"):
            status = getattr(obj, "__cop_implementation_status__", None)
            
            # Check if this matches our filter criteria
            status_match = implementation_status is None or status == implementation_status
            
            if status_match:
                # Determine component type
                if inspect.isfunction(obj):
                    comp_type = "function"
                elif inspect.ismethod(obj):
                    comp_type = "method"
                elif inspect.isclass(obj):
                    comp_type = "class"
                elif inspect.ismodule(obj):
                    comp_type = "module"
                else:
                    comp_type = "other"
                
                type_match = component_type is None or comp_type == component_type
                
                if type_match:
                    # Get basic metadata
                    intent_desc = getattr(obj, "__cop_intent__", None)
                    
                    component_info = {
                        "name": name,
                        "type": comp_type,
                        "parent": parent,
                        "implementation_status": status,
                        "intent": intent_desc,
                        "obj": obj
                    }
                    
                    results.append(component_info)
    
    # Process module contents
    for name, obj in inspect.getmembers(module):
        process_component(name, obj)
        
        # If it's a class, also process its methods
        if inspect.isclass(obj):
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                process_component(method_name, method, parent=name)
    
    return results


@intent("Find human decision points in a module")
def find_decision_points(module) -> List[Dict[str, Any]]:
    """
    Find all human decision points in a module.
    
    Args:
        module: The module to search in
        
    Returns:
        List of dictionaries with decision point info
        
    Example:
        decision_points = find_decision_points(my_module)
        for dp in decision_points:
            print(f"{dp['name']}: {dp['description']} (Roles: {dp['roles']})")
    """
    decision_points = []
    
    # Helper to check if component is a decision point
    def check_decision_point(name, obj, parent=None):
        if getattr(obj, "__cop_decision_point__", False):
            decision_points.append({
                "name": name,
                "parent": parent,
                "description": getattr(obj, "__cop_decision_description__", None),
                "roles": getattr(obj, "__cop_decision_roles__", None),
                "obj": obj
            })
    
    # Process module contents
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            check_decision_point(name, obj)
        
        # Also check class methods
        elif inspect.isclass(obj):
            for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                check_decision_point(method_name, method, parent=name)
    
    return decision_points


@intent("Check if a component is fully implemented")
def is_implemented(obj) -> bool:
    """
    Determine if a component is fully implemented.
    
    Args:
        obj: The object to check
        
    Returns:
        True if the component is fully implemented
        
    Example:
        if not is_implemented(my_function):
            print("This function is not yet implemented!")
    """
    status = getattr(obj, "__cop_implementation_status__", IMPLEMENTED)
    return status == IMPLEMENTED


#-----------------------------------------------------------
# 3. DOCUMENTATION TOOLS
#-----------------------------------------------------------

@intent("Generate documentation from COP annotations")
def generate_documentation(obj, format="markdown") -> str:
    """
    Generate documentation from COP annotations.
    
    Args:
        obj: The object to document (function, class, or module)
        format: Output format ("markdown" or "plaintext")
        
    Returns:
        Formatted documentation string
        
    Example:
        docs = generate_documentation(my_class)
        with open("docs.md", "w") as f:
            f.write(docs)
    """
    metadata = get_cop_metadata(obj)
    name = getattr(obj, "__name__", "Unnamed")
    
    if format == "markdown":
        docs = [f"# {name}"]
        
        # Intent section
        if metadata["intent"]:
            docs.append(f"\n## Intent\n{metadata['intent']}")
        
        # Implementation status
        status = metadata["implementation_status"]
        if status:
            docs.append(f"\n## Implementation Status\n**{status}**")
            
            # Status-specific details
            if status == NOT_IMPLEMENTED and "not_implemented" in metadata:
                if metadata["not_implemented"]["reason"]:
                    docs.append(f"\n**Reason:** {metadata['not_implemented']['reason']}")
                if metadata["not_implemented"]["issue_id"]:
                    docs.append(f"\n**Issue:** {metadata['not_implemented']['issue_id']}")
            
            elif status == PARTIAL and "partial_implementation" in metadata:
                if metadata["partial_implementation"]["details"]:
                    docs.append(f"\n**Details:** {metadata['partial_implementation']['details']}")
            
            elif status == DEPRECATED and "deprecation" in metadata:
                if metadata["deprecation"]["reason"]:
                    docs.append(f"\n**Reason:** {metadata['deprecation']['reason']}")
                if metadata["deprecation"]["alternative"]:
                    docs.append(f"\n**Alternative:** {metadata['deprecation']['alternative']}")
                if metadata["deprecation"]["removal_version"]:
                    docs.append(f"\n**Scheduled for removal in:** {metadata['deprecation']['removal_version']}")
            
            elif status == IN_PROGRESS and "in_progress" in metadata:
                progress_info = []
                if metadata["in_progress"]["developer"]:
                    progress_info.append(f"**Developer:** {metadata['in_progress']['developer']}")
                if metadata["in_progress"]["started_date"]:
                    progress_info.append(f"**Started:** {metadata['in_progress']['started_date']}")
                if metadata["in_progress"]["expected_completion"]:
                    progress_info.append(f"**Expected completion:** {metadata['in_progress']['expected_completion']}")
                
                if progress_info:
                    docs.append("\n" + "\n".join(progress_info))
        
        # Invariants
        if metadata["invariants"]:
            docs.append("\n## Invariants")
            for inv in metadata["invariants"]:
                docs.append(f"- {inv}")
        
        # Decision point
        if "decision_point" in metadata:
            docs.append("\n## Human Decision Point")
            if metadata["decision_point"]["description"]:
                docs.append(f"**Description:** {metadata['decision_point']['description']}")
            if metadata["decision_point"]["roles"]:
                roles = ", ".join(metadata["decision_point"]["roles"])
                docs.append(f"**Authorized roles:** {roles}")
        
        # AI implementation
        if "ai_implementation" in metadata:
            docs.append("\n## AI Implementation")
            if metadata["ai_implementation"]["description"]:
                docs.append(f"**Description:** {metadata['ai_implementation']['description']}")
            
            if metadata["ai_implementation"]["constraints"]:
                docs.append("\n**Constraints:**")
                for constraint in metadata["ai_implementation"]["constraints"]:
                    docs.append(f"- {constraint}")
        
        # Dependencies
        if "dependencies" in metadata:
            docs.append("\n## Dependencies")
            
            if metadata["dependencies"]["required"]:
                docs.append("\n**Required:**")
                for dep in metadata["dependencies"]["required"]:
                    docs.append(f"- {dep}")
            
            if metadata["dependencies"]["optional"]:
                docs.append("\n**Optional:**")
                for dep in metadata["dependencies"]["optional"]:
                    docs.append(f"- {dep}")
        
        # Conditions
        if "conditions" in metadata:
            if metadata["conditions"]["pre_conditions"]:
                docs.append("\n## Pre-conditions")
                for cond in metadata["conditions"]["pre_conditions"]:
                    docs.append(f"- {cond}")
            
            if metadata["conditions"]["post_conditions"]:
                docs.append("\n## Post-conditions")
                for cond in metadata["conditions"]["post_conditions"]:
                    docs.append(f"- {cond}")
        
        # Roadmap
        if "roadmap" in metadata:
            docs.append("\n## Roadmap")
            roadmap = metadata["roadmap"]
            if roadmap.get("milestone"):
                docs.append(f"**Milestone:** {roadmap['milestone']}")
            if roadmap.get("planned_date"):
                docs.append(f"**Planned date:** {roadmap['planned_date']}")
            if roadmap.get("priority"):
                docs.append(f"**Priority:** {roadmap['priority']}")
            if roadmap.get("owner"):
                docs.append(f"**Owner:** {roadmap['owner']}")
        
        return "\n".join(docs)
    else:
        # Plaintext format (simplified)
        return f"{name} - {metadata['intent']}"


@intent("Generate a development roadmap from COP annotations")
def generate_roadmap(module, sort_by="priority") -> str:
    """
    Generate a development roadmap from COP annotations.
    
    Args:
        module: The module to analyze
        sort_by: How to sort items ("priority", "date", "milestone")
        
    Returns:
        Markdown-formatted roadmap
        
    Example:
        roadmap = generate_roadmap(my_module)
        print(roadmap)
    """
    # Find components with roadmap information
    components = []
    
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__cop_roadmap__"):
            roadmap = getattr(obj, "__cop_roadmap__")
            status = getattr(obj, "__cop_implementation_status__", IMPLEMENTED)
            intent = getattr(obj, "__cop_intent__", "No intent specified")
            
            components.append({
                "name": name,
                "intent": intent,
                "status": status,
                "milestone": roadmap.get("milestone", "Unspecified"),
                "planned_date": roadmap.get("planned_date", "Unspecified"),
                "priority": roadmap.get("priority", "medium"),
                "owner": roadmap.get("owner", "Unassigned")
            })
    
    # Sort components based on criteria
    if sort_by == "priority":
        priority_order = {"high": 0, "medium": 1, "low": 2}
        components.sort(key=lambda x: priority_order.get(x["priority"].lower(), 999))
    elif sort_by == "date":
        components.sort(key=lambda x: x["planned_date"])
    elif sort_by == "milestone":
        components.sort(key=lambda x: x["milestone"])
    
    # Generate markdown
    if not components:
        return "No roadmap information found."
    
    roadmap = ["# Development Roadmap", ""]
    
    # Group by milestone
    milestones = {}
    for component in components:
        milestone = component["milestone"]
        if milestone not in milestones:
            milestones[milestone] = []
        milestones[milestone].append(component)
    
    # Generate roadmap by milestone
    for milestone, items in milestones.items():
        roadmap.append(f"## {milestone}")
        roadmap.append("")
        
        for item in items:
            status_indicator = {
                IMPLEMENTED: "✅",
                PARTIAL: "🟡",
                IN_PROGRESS: "🔄",
                PLANNED: "📅",
                NOT_IMPLEMENTED: "❌",
                DEPRECATED: "⛔"
            }.get(item["status"], "")
            
            roadmap.append(f"### {status_indicator} {item['name']}")
            roadmap.append(f"**Intent:** {item['intent']}")
            roadmap.append(f"**Status:** {item['status']}")
            roadmap.append(f"**Priority:** {item['priority']}")
            roadmap.append(f"**Owner:** {item['owner']}")
            if item["planned_date"] != "Unspecified":
                roadmap.append(f"**Planned date:** {item['planned_date']}")
            roadmap.append("")
    
    return "\n".join(roadmap)


#-----------------------------------------------------------
# 4. VALIDATION TOOLS
#-----------------------------------------------------------

@intent("Check implementation status for consistency with code")
def verify_implementation(obj) -> Dict[str, Any]:
    """
    Verify that implementation status is consistent with actual code.
    
    Args:
        obj: The object to verify (function, class, or module)
        
    Returns:
        Dictionary with verification results
        
    Example:
        results = verify_implementation(my_function)
        if not results['consistent']:
            print(f"Warning: {results['messages']}")
    """
    verification = {
        "consistent": True,
        "messages": [],
        "details": {}
    }
    
    # Get metadata
    status = getattr(obj, "__cop_implementation_status__", IMPLEMENTED)
    
    # Check functions and methods
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        source = inspect.getsource(obj)
        body = inspect.getsourcelines(obj)[0]
        
        # Skip decorator lines and function definition
        implementation_lines = []
        in_def = True
        for line in body:
            line = line.strip()
            if in_def and line.endswith(":"):
                in_def = False
                continue
            if not in_def and line and not line.startswith("@"):
                implementation_lines.append(line)
        
        # Check for empty function bodies or "pass" statements
        has_implementation = bool(implementation_lines)
        empty_or_pass = all(line.strip() in ("pass", "") for line in implementation_lines)
        has_todo = "# TODO" in source or "# FIXME" in source or "# To be implemented" in source
        
        verification["details"] = {
            "has_implementation": has_implementation,
            "empty_or_pass": empty_or_pass,
            "has_todo": has_todo
        }
        
        # Detect inconsistencies
        if status == IMPLEMENTED and (empty_or_pass or has_todo):
            verification["consistent"] = False
            verification["messages"].append(
                f"Function marked as IMPLEMENTED but contains pass/TODO comments"
            )
        
        if status == NOT_IMPLEMENTED and not (empty_or_pass or has_todo):
            verification["consistent"] = False
            verification["messages"].append(
                f"Function marked as NOT_IMPLEMENTED but contains actual implementation"
            )
    
    # Check classes
    elif inspect.isclass(obj):
        has_method_inconsistencies = False
        method_messages = []
        
        # Check each method in the class
        for name, method in inspect.getmembers(obj, inspect.isfunction):
            if not name.startswith("__"):  # Skip magic methods
                method_verification = verify_implementation(method)
                
                if not method_verification["consistent"]:
                    has_method_inconsistencies = True
                    method_messages.extend([
                        f"Method {name}: {msg}" for msg in method_verification["messages"]
                    ])
        
        if has_method_inconsistencies:
            verification["consistent"] = False
            verification["messages"].extend(method_messages)
    
    # Check modules
    elif inspect.ismodule(obj):
        # Similar approach to check functions and classes in the module
        pass
    
    return verification


@intent("Validate that code follows COP best practices")
def cop_check(obj) -> Dict[str, Any]:
    """
    Validate that code follows COP best practices.
    
    Args:
        obj: The object to check (function, class, or module)
        
    Returns:
        Dictionary with validation results
        
    Example:
        results = cop_check(my_module)
        for issue in results['issues']:
            print(f"- {issue}")
    """
    validation = {
        "issues": [],
        "warnings": [],
        "recommendations": []
    }
    
    # Helper to check a single component
    def check_component(obj, name=None):
        # Missing intent
        if not hasattr(obj, "__cop_intent__"):
            validation["issues"].append(
                f"{name or obj.__name__}: Missing @intent decorator"
            )
        
        # Check implementation consistency
        implementation_check = verify_implementation(obj)
        if not implementation_check["consistent"]:
            validation["issues"].extend([
                f"{name or obj.__name__}: {msg}" for msg in implementation_check["messages"]
            ])
        
        # AI implementation without constraints
        if getattr(obj, "__cop_ai_implemented__", False):
            constraints = getattr(obj, "__cop_constraints__", [])
            if not constraints:
                validation["warnings"].append(
                    f"{name or obj.__name__}: @ai_implement used without constraints"
                )
        
        # Human decision without roles
        if getattr(obj, "__cop_decision_point__", False):
            roles = getattr(obj, "__cop_decision_roles__", None)
            if not roles:
                validation["warnings"].append(
                    f"{name or obj.__name__}: @human_decision used without specifying roles"
                )
    
    # Check a function or method
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        check_component(obj)
    
    # Check a class
    elif inspect.isclass(obj):
        check_component(obj)
        
        # Check each method
        for name, method in inspect.getmembers(obj, inspect.isfunction):
            if not name.startswith("__"):  # Skip magic methods
                check_component(method, f"{obj.__name__}.{name}")
    
    # Check a module
    elif inspect.ismodule(obj):
        # Check each function and class in the module
        for name, item in inspect.getmembers(obj):
            if inspect.isfunction(item):
                check_component(item, name)
            elif inspect.isclass(item):
                check_component(item, name)
                
                # Check methods in the class
                for method_name, method in inspect.getmembers(item, inspect.isfunction):
                    if not method_name.startswith("__"):  # Skip magic methods
                        check_component(method, f"{name}.{method_name}")
    
    # Add recommendations
    if validation["issues"] or validation["warnings"]:
        validation["recommendations"].append(
            "Add @intent decorators to all public functions and classes"
        )
        validation["recommendations"].append(
            "Ensure implementation status matches actual code"
        )
        validation["recommendations"].append(
            "Add constraints to all @ai_implement decorators"
        )
        validation["recommendations"].append(
            "Specify roles for all @human_decision points"
        )
    
    return validation


#-----------------------------------------------------------
# 5. PRACTICAL EXAMPLES
#-----------------------------------------------------------

@intent("Demonstrate COP usage in a payment processing system")
class PaymentSystem:
    """
    Example payment processing system using COP annotations.
    
    This class demonstrates how to use COP annotations to document
    a system with both implemented and planned features.
    """
    
    @intent("Initialize the payment system with configuration")
    def __init__(self, config):
        self.config = config
        self.gateway = self._initialize_gateway(config["gateway_type"])
        self.payment_methods = []
    
    @intent("Get available payment methods")
    def get_payment_methods(self):
        """Return list of available payment methods."""
        return self.payment_methods
    
    @intent("Process a payment transaction")
    @invariant("Amount must be positive")
    @invariant("Payment method must be valid")
    @ensures(
        pre_conditions=["Customer account must exist", "Amount must be available"],
        post_conditions=["Transaction is recorded", "Receipt is generated"]
    )
    def process_payment(self, customer_id, amount, payment_method):
        """
        Process a payment transaction.
        
        Args:
            customer_id: The customer making the payment
            amount: The payment amount
            payment_method: The payment method to use
            
        Returns:
            Transaction result with ID and status
        """
        # Validate inputs
        if amount <= 0:
            raise ValueError("Amount must be positive")
            
        if payment_method not in self.payment_methods:
            raise ValueError("Invalid payment method")
        
        # Process the payment
        transaction = self.gateway.charge(customer_id, amount, payment_method)
        
        # Record transaction
        self._record_transaction(transaction)
        
        # Generate receipt
        receipt = self._generate_receipt(transaction)
        
        return {
            "transaction_id": transaction.id,
            "status": transaction.status,
            "receipt": receipt
        }
    
    @intent("Initialize the appropriate payment gateway")
    def _initialize_gateway(self, gateway_type):
        """Initialize and return the payment gateway."""
        # Implementation depends on gateway_type
        return MockGateway()
    
    @intent("Record transaction for future reference")
    def _record_transaction(self, transaction):
        """Record a transaction in the database."""
        # Implementation would save to database
        pass
    
    @intent("Generate a receipt for the customer")
    def _generate_receipt(self, transaction):
        """Generate a payment receipt."""
        # Implementation would format a receipt
        return f"Receipt for transaction {transaction.id}"
    
    @intent("Process an international payment")
    @not_implemented("Pending regulatory approval")
    @roadmap(milestone="Q3 2023", priority="high", owner="International Payments Team")
    def process_international_payment(self, customer_id, amount, currency, payment_method):
        """
        Process an international payment with currency conversion.
        
        This feature is planned but not yet implemented.
        """
        # To be implemented
        pass
    
    @intent("Set up recurring payments")
    @partially_implemented("Only monthly recurring payments are supported")
    def setup_recurring_payment(self, customer_id, amount, payment_method, frequency="monthly"):
        """
        Set up a recurring payment schedule.
        
        Currently only supports monthly payments. Weekly and annual
        payments are planned for future implementation.
        """
        if frequency != "monthly":
            raise NotImplementedError(f"Frequency {frequency} is not yet supported")
            
        # Implementation for monthly payments
        return {"schedule_id": "123", "status": "active"}
    
    @intent("Cancel a payment")
    @human_decision("Approve payment cancellation for large amounts", 
                   roles=["Payment Manager", "Customer Service Manager"])
    def cancel_payment(self, transaction_id, reason, approver=None):
        """
        Cancel a payment that has been processed.
        
        Large cancellations require manager approval.
        """
        # Get transaction
        transaction = self._get_transaction(transaction_id)
        
        # Check if approval needed
        requires_approval = transaction.amount > 1000
        
        if requires_approval and not approver:
            raise ValueError("Cancellation requires manager approval")
        
        # Process cancellation
        return {"cancelled": True, "refund_id": "R123"}
    
    @intent("Apply special discount to payment")
    @ai_implement("Implement dynamic discount calculation",
                 constraints=["Must consider customer history",
                              "Must respect maximum discount limits",
                              "Must log discount justification"],
                 implementation_status=IMPLEMENTED)
    def apply_discount(self, customer_id, transaction_amount):
        """
        Apply an intelligent discount based on customer history.
        
        This method uses AI to determine the optimal discount
        based on customer loyalty, purchase history, and current promotions.
        """
        # Simple implementation - would be more sophisticated in real AI version
        base_discount = 0.05  # 5%
        
        # Pretend to analyze customer history
        loyal_customer_bonus = 0.02  # 2% additional
        
        total_discount = min(base_discount + loyal_customer_bonus, 0.15)  # Cap at 15%
        
        discount_amount = transaction_amount * total_discount
        final_amount = transaction_amount - discount_amount
        
        return {
            "original_amount": transaction_amount,
            "discount_percentage": total_discount * 100,
            "discount_amount": discount_amount,
            "final_amount": final_amount
        }
    
    @intent("Get detailed payment analytics")
    @deprecated("Use enhanced_analytics() instead", removal_version="2.0.0")
    def get_analytics(self, time_period):
        """Get payment analytics for the specified time period."""
        warnings.warn("This method is deprecated", DeprecationWarning)
        return {"total_transactions": 100, "total_amount": 15000}
    
    @intent("Get enhanced payment analytics with visualizations")
    @in_progress(developer="Analytics Team", expected_completion="2023-07-01")
    def enhanced_analytics(self, time_period, metrics=None):
        """
        Get enhanced payment analytics with additional metrics.
        
        This method is currently being implemented and will replace
        the older get_analytics method.
        """
        # Basic implementation while full features are being developed
        return {
            "total_transactions": 100,
            "total_amount": 15000,
            "average_transaction": 150
        }
    
    def _get_transaction(self, transaction_id):
        """Helper to retrieve transaction details."""
        # Mock implementation
        class MockTransaction:
            def __init__(self):
                self.id = transaction_id
                self.amount = 1500
        
        return MockTransaction()


class MockGateway:
    """Mock payment gateway for example purposes."""
    
    def charge(self, customer_id, amount, payment_method):
        """Process a charge."""
        class MockTransaction:
            def __init__(self):
                self.id = "T12345"
                self.status = "completed"
        
        return MockTransaction()


#-----------------------------------------------------------
# 6. HALLUCINATION PREVENTION TOOLS
#-----------------------------------------------------------

@intent("Check if a component is safe to describe to users")
def implementation_safety_check(obj) -> Dict[str, Any]:
    """
    Check if a component is safe to describe as implemented functionality.
    
    This function helps prevent hallucination by explicitly checking
    whether a component should be described as working functionality.
    
    Args:
        obj: The object to check
        
    Returns:
        Dictionary with safety assessment
        
    Example:
        safety = implementation_safety_check(my_function)
        if not safety['safe_to_describe']:
            print(f"Warning: {safety['reason']}")
    """
    safety = {
        "safe_to_describe": True,
        "reason": None,
        "implementation_status": IMPLEMENTED,
        "missing_elements": []
    }
    
    # Get implementation status
    status = getattr(obj, "__cop_implementation_status__", IMPLEMENTED)
    safety["implementation_status"] = status
    
    # Check if it's safe based on status
    if status == NOT_IMPLEMENTED:
        safety["safe_to_describe"] = False
        safety["reason"] = "Component is explicitly marked as not implemented"
    
    elif status == PLANNED:
        safety["safe_to_describe"] = False
        safety["reason"] = "Component is planned but not yet implemented"
    
    elif status == DEPRECATED:
        safety["safe_to_describe"] = True  # Deprecated means it exists but shouldn't be used
        safety["reason"] = "Component is deprecated but functional"
    
    elif status == PARTIAL:
        safety["safe_to_describe"] = True  # Partially implemented
        details = getattr(obj, "__cop_partial_details__", None)
        if details:
            safety["reason"] = f"Component is partially implemented: {details}"
        else:
            safety["reason"] = "Component is partially implemented"
    
    elif status == IN_PROGRESS:
        safety["safe_to_describe"] = False
        safety["reason"] = "Component is currently being implemented"
    
    # For functions and methods, also check the implementation
    if inspect.isfunction(obj) or inspect.ismethod(obj):
        try:
            # Check source code
            source = inspect.getsource(obj)
            body = inspect.getsourcelines(obj)[0]
            
            # Skip decorator lines and function definition
            implementation_lines = []
            in_def = True
            for line in body:
                line = line.strip()
                if in_def and line.endswith(":"):
                    in_def = False
                    continue
                if not in_def and line and not line.startswith("@"):
                    implementation_lines.append(line)
            
            # Check for empty function bodies or "pass" statements
            has_implementation = bool(implementation_lines)
            empty_or_pass = all(line.strip() in ("pass", "") for line in implementation_lines)
            has_todo = "# TODO" in source or "# FIXME" in source or "# To be implemented" in source
            raises_not_implemented = "NotImplementedError" in source or "raise NotImplementedError" in source
            
            # Adjust safety assessment based on code analysis
            if (empty_or_pass or has_todo or raises_not_implemented) and safety["safe_to_describe"]:
                safety["safe_to_describe"] = False
                safety["reason"] = "Function appears to be incomplete (missing implementation, TODO comments, or raises NotImplementedError)"
        
        except (IOError, TypeError):
            # Can't access source code
            pass
    
    return safety


@intent("Summarize component implementation status")
def get_implementation_summary(module) -> Dict[str, Any]:
    """
    Get a summary of implementation status for all components in a module.
    
    This function helps prevent hallucination by providing a clear overview
    of what is and isn't implemented in a module.
    
    Args:
        module: The module to analyze
        
    Returns:
        Dictionary with implementation summary
        
    Example:
        summary = get_implementation_summary(my_module)
        print(f"Implemented: {summary['counts']['implemented']}")
        print(f"Not implemented: {summary['counts']['not_implemented']}")
    """
    summary = {
        "counts": {
            "implemented": 0,
            "partial": 0,
            "planned": 0,
            "not_implemented": 0,
            "in_progress": 0,
            "deprecated": 0,
            "total": 0
        },
        "implemented": [],
        "not_implemented": [],
        "partial": [],
        "planned": [],
        "in_progress": [],
        "deprecated": []
    }
    
    # Helper to process a component
    def process_component(name, obj, parent=None):
        if inspect.isfunction(obj) or inspect.ismethod(obj) or inspect.isclass(obj):
            status = getattr(obj, "__cop_implementation_status__", IMPLEMENTED)
            intent = getattr(obj, "__cop_intent__", None)
            
            full_name = f"{parent}.{name}" if parent else name
            component_info = {
                "name": full_name,
                "intent": intent
            }
            
            # Update counts
            summary["counts"]["total"] += 1
            summary["counts"][status] += 1
            
            # Add to appropriate list
            summary[status].append(component_info)
    
    # Process module contents
    for name, obj in inspect.getmembers(module):
        if not name.startswith("_"):  # Skip private members
            process_component(name, obj)
            
            # Also process class methods
            if inspect.isclass(obj):
                for method_name, method in inspect.getmembers(obj, inspect.isfunction):
                    if not method_name.startswith("_"):  # Skip private methods
                        process_component(method_name, method, parent=name)
    
    return summary


# Create an example implementation status summary function
@intent("Generate a human-readable implementation status report")
def generate_status_report(module) -> str:
    """
    Generate a human-readable report of what is and isn't implemented.
    
    This function helps prevent hallucination by explicitly listing
    which features are implemented vs. planned/not implemented.
    
    Args:
        module: The module to analyze
        
    Returns:
        Markdown-formatted status report
        
    Example:
        report = generate_status_report(my_module)
        print(report)
    """
    summary = get_implementation_summary(module)
    
    report = ["# Implementation Status Report", ""]
    
    # Add summary statistics
    report.append("## Summary")
    report.append("")
    report.append(f"- Total components: {summary['counts']['total']}")
    report.append(f"- Fully implemented: {summary['counts']['implemented']}")
    report.append(f"- Partially implemented: {summary['counts']['partial']}")
    report.append(f"- In progress: {summary['counts']['in_progress']}")
    report.append(f"- Planned (not implemented): {summary['counts']['planned']}")
    report.append(f"- Not implemented: {summary['counts']['not_implemented']}")
    report.append(f"- Deprecated: {summary['counts']['deprecated']}")
    report.append("")
    
    # Add implemented features
    if summary['implemented']:
        report.append("## Implemented Features")
        report.append("")
        for comp in summary['implemented']:
            report.append(f"- **{comp['name']}**: {comp['intent']}")
        report.append("")
    
    # Add partially implemented features
    if summary['partial']:
        report.append("## Partially Implemented Features")
        report.append("")
        for comp in summary['partial']:
            report.append(f"- **{comp['name']}**: {comp['intent']}")
        report.append("")
    
    # Add in-progress features
    if summary['in_progress']:
        report.append("## Features In Development")
        report.append("")
        for comp in summary['in_progress']:
            report.append(f"- **{comp['name']}**: {comp['intent']}")
        report.append("")
    
    # Add planned features
    if summary['planned']:
        report.append("## Planned Features (Not Yet Implemented)")
        report.append("")
        for comp in summary['planned']:
            report.append(f"- **{comp['name']}**: {comp['intent']}")
        report.append("")
    
    # Add not implemented features
    if summary['not_implemented']:
        report.append("## Not Implemented Features")
        report.append("")
        for comp in summary['not_implemented']:
            report.append(f"- **{comp['name']}**: {comp['intent']}")
        report.append("")
    
    # Add deprecated features
    if summary['deprecated']:
        report.append("## Deprecated Features")
        report.append("")
        for comp in summary['deprecated']:
            report.append(f"- **{comp['name']}**: {comp['intent']}")
        report.append("")
    
    # Add hallucination prevention reminder
    report.append("## ⚠️ Hallucination Prevention Reminder")
    report.append("")
    report.append("When describing this system to users:")
    report.append("- Only describe implemented and partially implemented features as existing functionality")
    report.append("- Clearly indicate limitations of partially implemented features")
    report.append("- Do not describe planned or not implemented features as if they exist")
    report.append("- Mention planned features only when discussing future capabilities")
    report.append("- Use implementation_safety_check() to verify before describing features")
    
    return "\n".join(report)


# Apply intent decorator to the module itself
intent("Provide extended functionality for Concept-Oriented Programming")(sys.modules[__name__])


# Example usage (uncomment to run)

# Create a simple example to demonstrate usage
if __name__ == "__main__":
    # Create an example module for testing
    import types
    example_module = types.ModuleType("example_module")
    
    # Add the PaymentSystem class to it
    example_module.PaymentSystem = PaymentSystem
    
    # Generate a status report
    report = generate_status_report(example_module)
    print(report)
    
    # Generate documentation for a method
    payment_system = PaymentSystem({"gateway_type": "mock"})
    docs = generate_documentation(payment_system.process_payment)
    print("\n" + docs)
