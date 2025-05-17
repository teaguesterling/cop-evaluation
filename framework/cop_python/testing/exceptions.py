# Exception classes for assertions

class COPAnnotationViolation(AssertionError):
    pass

class InvariantViolation(COPAnnotationViolation): 
    pass
    
class SecurityRiskViolation(COPAnnotationViolation): 
    pass
    
class ImplementationStatusMismatch(COPAnnotationViolation): 
    pass
    
class DecisionViolation(COPAnnotationViolation): 
    pass
    
class IntentViolation(COPAnnotationViolation): 
    pass
