"""Parameter validation for ActionTable API.

Based on:
- Specs/ParameterTypes.idr (Idris2 formal specification)
- Schema/parameter_table.json (132 actions, 1154 parameters)
- HwpBooks/ParameterSetTable_2504.pdf
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ParameterDef:
    """Idris ParameterDef implementation.

    Corresponds to Specs/ParameterTypes.idr:
    record ParameterDef where
      paramName : String
      paramType : PITType
      subType : String
      description : String
    """
    param_name: str
    param_type: str  # "PIT_BSTR", "PIT_UI1", etc.
    subtype: str
    description: str


@dataclass
class ActionSchema:
    """Idris ActionSchema implementation.

    Corresponds to Specs/ParameterTypes.idr:
    record ActionSchema where
      actionName : String
      paramDefs : List ParameterDef
    """
    action_name: str
    param_defs: List[ParameterDef]


@dataclass
class ValidationError:
    """Idris ValidationError implementation.

    Corresponds to Specs/ParameterTypes.idr:
    data ValidationError =
      TypeMismatch PITType PITType |
      ValueOutOfRange PITType Int Int Int |
      InvalidStringValue String |
      MissingRequiredParameter String |
      UnknownParameter String
    """
    error_type: str  # "TypeMismatch", "ValueOutOfRange", etc.
    message: str
    param_name: Optional[str] = None


@dataclass
class ValidationResult:
    """Validation result with errors and warnings."""
    success: bool
    errors: List[ValidationError]
    warnings: List[str]

    @staticmethod
    def ok(warnings: Optional[List[str]] = None) -> 'ValidationResult':
        """Create successful validation result."""
        return ValidationResult(True, [], warnings or [])

    @staticmethod
    def fail(errors: List[ValidationError]) -> 'ValidationResult':
        """Create failed validation result."""
        return ValidationResult(False, errors, [])


class ParameterValidator:
    """Parameter validator based on Idris2 Specs/ParameterTypes.idr.

    Implements:
    - validateType : PITType -> ParamValue -> Either ValidationError ()
    - validateParameter : ParameterDef -> ParamValue -> Either ValidationError ()
    - validateParameters : ActionSchema -> List (String, ParamValue) -> Either ValidationError ()
    """

    def __init__(self):
        """Initialize validator and load parameter_table.json."""
        self.schemas: Dict[str, ActionSchema] = {}
        self._load_parameter_table()

    def _load_parameter_table(self) -> None:
        """Load Schema/parameter_table.json and convert to ActionSchema objects."""
        json_path = Path(__file__).parent.parent.parent / "Schema" / "parameter_table.json"

        if not json_path.exists():
            raise FileNotFoundError(f"parameter_table.json not found: {json_path}")

        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        actions = data.get('actions', {})

        for action_name, params in actions.items():
            param_defs = [
                ParameterDef(
                    param_name=p['param_name'],
                    param_type=p['param_type'],
                    subtype=p.get('subtype', ''),
                    description=p.get('description', '')
                )
                for p in params
            ]

            self.schemas[action_name] = ActionSchema(
                action_name=action_name,
                param_defs=param_defs
            )

    def validate_type(self, pit_type: str, value: Any) -> Optional[ValidationError]:
        """Validate value against PIT type.

        Implements Idris: validateType : PITType -> ParamValue -> Either ValidationError ()

        Args:
            pit_type: PIT type string (e.g., "PIT_BSTR", "PIT_UI1")
            value: Python value to validate

        Returns:
            ValidationError if invalid, None if valid
        """
        # PIT_BSTR: String
        if pit_type == "PIT_BSTR":
            if not isinstance(value, str):
                return ValidationError(
                    "TypeMismatch",
                    f"Expected string for PIT_BSTR, got {type(value).__name__}",
                    None
                )
            return None

        # Integer types - check type first
        if not isinstance(value, int):
            return ValidationError(
                "TypeMismatch",
                f"Expected integer for {pit_type}, got {type(value).__name__}",
                None
            )

        # PIT_UI1: 0-255 (1-byte unsigned)
        if pit_type == "PIT_UI1":
            if not (0 <= value <= 255):
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} out of range for PIT_UI1 (valid: 0-255)",
                    None
                )
            return None

        # PIT_UI2: 0-65535 (2-byte unsigned)
        if pit_type == "PIT_UI2":
            if not (0 <= value <= 65535):
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} out of range for PIT_UI2 (valid: 0-65535)",
                    None
                )
            return None

        # PIT_UI4: 0-4294967295 (4-byte unsigned)
        if pit_type == "PIT_UI4":
            if not (0 <= value <= 4294967295):
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} out of range for PIT_UI4 (valid: 0-4294967295)",
                    None
                )
            return None

        # PIT_UI: unsigned integer (same as UI4)
        if pit_type == "PIT_UI":
            if value < 0:
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} must be non-negative for PIT_UI",
                    None
                )
            return None

        # PIT_I1: -128 to 127 (1-byte signed)
        if pit_type == "PIT_I1":
            if not (-128 <= value <= 127):
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} out of range for PIT_I1 (valid: -128-127)",
                    None
                )
            return None

        # PIT_I2: -32768 to 32767 (2-byte signed)
        if pit_type == "PIT_I2":
            if not (-32768 <= value <= 32767):
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} out of range for PIT_I2 (valid: -32768-32767)",
                    None
                )
            return None

        # PIT_I4: -2147483648 to 2147483647 (4-byte signed)
        if pit_type == "PIT_I4":
            if not (-2147483648 <= value <= 2147483647):
                return ValidationError(
                    "ValueOutOfRange",
                    f"Value {value} out of range for PIT_I4 (valid: -2147483648-2147483647)",
                    None
                )
            return None

        # PIT_I: signed integer (same as I4)
        if pit_type == "PIT_I":
            return None  # Any integer is valid

        # PIT_SET: nested ParameterSet (dict expected)
        if pit_type == "PIT_SET":
            if not isinstance(value, dict):
                return ValidationError(
                    "TypeMismatch",
                    f"Expected dict for PIT_SET, got {type(value).__name__}",
                    None
                )
            return None

        # PIT_ARRAY: array (list expected)
        if pit_type == "PIT_ARRAY":
            if not isinstance(value, list):
                return ValidationError(
                    "TypeMismatch",
                    f"Expected list for PIT_ARRAY, got {type(value).__name__}",
                    None
                )
            return None

        # Unknown type - allow it (for future compatibility)
        return None

    def validate_parameter(
        self,
        action_id: str,
        param_name: str,
        value: Any
    ) -> Optional[ValidationError]:
        """Validate single parameter.

        Implements Idris: validateParameter : ParameterDef -> ParamValue -> Either ValidationError ()

        Args:
            action_id: Action name (e.g., "InsertText")
            param_name: Parameter name (e.g., "Text")
            value: Parameter value

        Returns:
            ValidationError if invalid, None if valid
        """
        # Get action schema
        schema = self.schemas.get(action_id)
        if not schema:
            # Unknown action - allow it (for future compatibility)
            return None

        # Find parameter definition
        param_def = None
        for pd in schema.param_defs:
            if pd.param_name == param_name:
                param_def = pd
                break

        if not param_def:
            # Unknown parameter - return warning instead of error
            return None

        # Validate type
        error = self.validate_type(param_def.param_type, value)
        if error:
            error.param_name = param_name
        return error

    def validate_all_parameters(
        self,
        action_id: str,
        params: Dict[str, Any]
    ) -> ValidationResult:
        """Validate all parameters for an action.

        Implements Idris: validateParameters : ActionSchema -> List (String, ParamValue) -> Either ValidationError ()

        Args:
            action_id: Action name
            params: Parameter dictionary

        Returns:
            ValidationResult with errors and warnings
        """
        errors = []
        warnings = []

        # Get action schema
        schema = self.schemas.get(action_id)
        if not schema:
            # Unknown action - warn but allow
            warnings.append(f"Unknown action '{action_id}' - no validation performed")
            return ValidationResult(True, [], warnings)

        # Get known parameter names
        known_params = {pd.param_name for pd in schema.param_defs}

        # Validate each provided parameter
        for param_name, value in params.items():
            # Check if parameter is known
            if param_name not in known_params:
                warnings.append(f"Unknown parameter '{param_name}' for action '{action_id}'")
                continue

            # Validate parameter
            error = self.validate_parameter(action_id, param_name, value)
            if error:
                errors.append(error)

        if errors:
            return ValidationResult.fail(errors)
        else:
            return ValidationResult.ok(warnings)

    def convert_to_pit_type(
        self,
        action_id: str,
        param_name: str,
        value: Any
    ) -> Any:
        """Convert Python value to appropriate PIT type.

        Args:
            action_id: Action name
            param_name: Parameter name
            value: Python value

        Returns:
            Converted value (may be same as input)
        """
        # Get parameter definition
        schema = self.schemas.get(action_id)
        if not schema:
            return value

        param_def = None
        for pd in schema.param_defs:
            if pd.param_name == param_name:
                param_def = pd
                break

        if not param_def:
            return value

        pit_type = param_def.param_type

        # Boolean to integer conversion for PIT_UI1
        if pit_type == "PIT_UI1" and isinstance(value, bool):
            return 1 if value else 0

        # String conversion for PIT_BSTR
        if pit_type == "PIT_BSTR" and not isinstance(value, str):
            return str(value)

        # Integer conversion
        if pit_type.startswith("PIT_UI") or pit_type.startswith("PIT_I"):
            if isinstance(value, str) and value.isdigit():
                return int(value)

        return value

    def get_schema(self, action_id: str) -> Optional[ActionSchema]:
        """Get ActionSchema for an action.

        Args:
            action_id: Action name

        Returns:
            ActionSchema or None if not found
        """
        return self.schemas.get(action_id)

    def get_all_actions(self) -> List[str]:
        """Get list of all known action names.

        Returns:
            List of action names
        """
        return list(self.schemas.keys())
