import pandas as pd
from src.validation.rules import ValidationEngine


def test_validation_engine_required_columns():
    rules = {
        "required_columns": {
            "customers": ["identifier", "name", "email"]
        }
    }
    engine = ValidationEngine(rules)

    df_valid = pd.DataFrame({
        "identifier": [1],
        "name": ["Ali"],
        "email": ["ali@example.com"],
    })
    errors = engine.validate(df_valid, "customers")
    assert errors.empty

    df_missing = pd.DataFrame({
        "identifier": [1],
        "name": ["Ali"],
    })
    errors = engine.validate(df_missing, "customers")
    assert len(errors) == 1
    assert errors.iloc[0]["error"] == "missing_required_column"
    assert errors.iloc[0]["column"] == "email"


def test_validation_engine_allowed_values():
    rules = {
        "allowed_values": {
            "orders.status": ["paid", "pending", "cancelled"]
        }
    }
    engine = ValidationEngine(rules)

    df = pd.DataFrame({
        "status": ["paid", "unknown_status", "pending"]
    })
    errors = engine.validate(df, "orders")
    assert len(errors) == 1
    assert errors.iloc[0]["error"] == "invalid_allowed_value"
    assert errors.iloc[0]["row"] == 1


def test_validation_engine_ranges():
    rules = {
        "ranges": {
            "students.age": {"min": 17, "max": 60},
            "students.gpa": {"min": 0.0, "max": 4.0}
        }
    }
    engine = ValidationEngine(rules)

    df = pd.DataFrame({
        "age": [20, -5, 25],
        "gpa": [3.5, 3.8, 4.5]
    })
    errors = engine.validate(df, "students")
    assert len(errors) == 2
    err_types = set(errors["error"])
    assert "below_minimum" in err_types
    assert "above_maximum" in err_types


def test_validation_engine_regex():
    rules = {
        "regex": {
            "customers.email": r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
        }
    }
    engine = ValidationEngine(rules)

    df = pd.DataFrame({
        "email": ["valid@example.com", "invalid-email-address"]
    })
    errors = engine.validate(df, "customers")
    assert len(errors) == 1
    assert errors.iloc[0]["error"] == "regex_validation_failed"
    assert errors.iloc[0]["row"] == 1
