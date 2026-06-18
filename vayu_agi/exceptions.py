"""Custom exception hierarchy for VAYU AGI 6."""
class VayuError(Exception): pass
class ModelUnavailableError(VayuError): pass
class BudgetExceededError(VayuError): pass
class RoutingError(VayuError): pass
class MemoryError(VayuError): pass
class ReasoningError(VayuError): pass
class ConsensusError(VayuError): pass
class MultimodalError(VayuError): pass
class SecurityError(VayuError): pass
class RateLimitError(VayuError): pass
