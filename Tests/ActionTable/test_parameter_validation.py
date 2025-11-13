"""Unit tests for parameter validation.

Tests Specs/ParameterTypes.idr implementation in param_validator.py
"""

import sys
from pathlib import Path

# Windows console UTF-8 setup
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

# Add src to path
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))

# Import param_validator directly (avoid importing client which needs pywin32)
import importlib.util
param_validator_path = src_path / "action_table" / "param_validator.py"
spec = importlib.util.spec_from_file_location("param_validator", param_validator_path)
param_validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(param_validator)

ParameterValidator = param_validator.ParameterValidator
ValidationError = param_validator.ValidationError


def test_pit_type_validation_bstr():
    """Test PIT_BSTR validation."""
    validator = ParameterValidator()

    # Valid: string
    error = validator.validate_type("PIT_BSTR", "Hello")
    assert error is None, "String should be valid for PIT_BSTR"

    # Invalid: integer
    error = validator.validate_type("PIT_BSTR", 123)
    assert error is not None, "Integer should be invalid for PIT_BSTR"
    assert error.error_type == "TypeMismatch"


def test_pit_type_validation_ui1():
    """Test PIT_UI1 validation (0-255)."""
    validator = ParameterValidator()

    # Valid cases
    assert validator.validate_type("PIT_UI1", 0) is None
    assert validator.validate_type("PIT_UI1", 1) is None
    assert validator.validate_type("PIT_UI1", 255) is None

    # Invalid: out of range
    error = validator.validate_type("PIT_UI1", 256)
    assert error is not None
    assert error.error_type == "ValueOutOfRange"

    error = validator.validate_type("PIT_UI1", -1)
    assert error is not None
    assert error.error_type == "ValueOutOfRange"

    # Invalid: wrong type
    error = validator.validate_type("PIT_UI1", "not a number")
    assert error is not None
    assert error.error_type == "TypeMismatch"


def test_pit_type_validation_i4():
    """Test PIT_I4 validation (signed 32-bit)."""
    validator = ParameterValidator()

    # Valid cases
    assert validator.validate_type("PIT_I4", 0) is None
    assert validator.validate_type("PIT_I4", 1000) is None
    assert validator.validate_type("PIT_I4", -1000) is None
    assert validator.validate_type("PIT_I4", 2147483647) is None
    assert validator.validate_type("PIT_I4", -2147483648) is None


def test_action_schema_lookup():
    """Test ActionSchema lookup from parameter_table.json."""
    validator = ParameterValidator()

    # Test InsertText schema
    schema = validator.get_schema("InsertText")
    assert schema is not None, "InsertText schema should exist"
    assert schema.action_name == "InsertText"
    assert len(schema.param_defs) == 1
    assert schema.param_defs[0].param_name == "Text"
    assert schema.param_defs[0].param_type == "PIT_BSTR"

    # Test CharShape schema
    schema = validator.get_schema("CharShape")
    assert schema is not None, "CharShape schema should exist"
    assert schema.action_name == "CharShape"
    assert len(schema.param_defs) == 65, "CharShape should have 65 parameters"

    # Check some CharShape parameters
    param_names = {p.param_name for p in schema.param_defs}
    assert "FaceNameHangul" in param_names
    assert "Bold" in param_names
    assert "Height" in param_names


def test_validate_parameter():
    """Test single parameter validation."""
    validator = ParameterValidator()

    # Valid: InsertText with string
    error = validator.validate_parameter("InsertText", "Text", "Hello")
    assert error is None

    # Invalid: InsertText with integer
    error = validator.validate_parameter("InsertText", "Text", 123)
    assert error is not None
    assert error.param_name == "Text"

    # Valid: CharShape Bold (PIT_UI1)
    error = validator.validate_parameter("CharShape", "Bold", 1)
    assert error is None

    # Invalid: CharShape Bold out of range
    error = validator.validate_parameter("CharShape", "Bold", 256)
    assert error is not None
    assert error.param_name == "Bold"


def test_validate_all_parameters():
    """Test validation of all parameters for an action."""
    validator = ParameterValidator()

    # Valid: InsertText
    result = validator.validate_all_parameters("InsertText", {"Text": "Hello"})
    assert result.success, "InsertText with valid params should succeed"

    # Invalid: InsertText with wrong type
    result = validator.validate_all_parameters("InsertText", {"Text": 123})
    assert not result.success, "InsertText with integer should fail"
    assert len(result.errors) == 1

    # Valid: CharShape with multiple parameters
    result = validator.validate_all_parameters("CharShape", {
        "FaceNameHangul": "맑은 고딕",
        "Height": 1000,
        "Bold": 1,
        "Italic": 0
    })
    assert result.success, "CharShape with valid params should succeed"

    # Invalid: CharShape with out-of-range value
    result = validator.validate_all_parameters("CharShape", {
        "Bold": 300  # Out of range for PIT_UI1
    })
    assert not result.success, "CharShape with invalid Bold should fail"

    # Warning: Unknown parameter
    result = validator.validate_all_parameters("InsertText", {
        "Text": "Hello",
        "UnknownParam": 123
    })
    assert result.success, "Unknown params should not block execution"
    assert len(result.warnings) > 0, "Should have warning for unknown param"


def test_convert_to_pit_type():
    """Test Python value to PIT type conversion."""
    validator = ParameterValidator()

    # Boolean to integer for PIT_UI1
    converted = validator.convert_to_pit_type("CharShape", "Bold", True)
    assert converted == 1, "True should convert to 1"

    converted = validator.convert_to_pit_type("CharShape", "Bold", False)
    assert converted == 0, "False should convert to 0"

    # String stays as string for PIT_BSTR
    converted = validator.convert_to_pit_type("InsertText", "Text", "Hello")
    assert converted == "Hello"


def test_get_all_actions():
    """Test getting all action names."""
    validator = ParameterValidator()

    actions = validator.get_all_actions()
    # Note: parameter_table.json has 132 actions currently
    # Just verify we have a reasonable number and key actions exist
    assert len(actions) > 100, f"Should have many actions, got {len(actions)}"
    assert "InsertText" in actions
    assert "CharShape" in actions
    assert "BorderFill" in actions


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Running Parameter Validation Tests")
    print("=" * 60)

    tests = [
        ("PIT_BSTR validation", test_pit_type_validation_bstr),
        ("PIT_UI1 validation", test_pit_type_validation_ui1),
        ("PIT_I4 validation", test_pit_type_validation_i4),
        ("Action schema lookup", test_action_schema_lookup),
        ("Single parameter validation", test_validate_parameter),
        ("All parameters validation", test_validate_all_parameters),
        ("Type conversion", test_convert_to_pit_type),
        ("Get all actions", test_get_all_actions),
    ]

    passed = 0
    failed = 0

    for test_name, test_func in tests:
        try:
            test_func()
            print(f"✅ {test_name}")
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"💥 {test_name}: {e}")
            failed += 1

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
