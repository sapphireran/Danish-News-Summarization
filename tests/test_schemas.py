from fjordpress.schemas import (
    SCHEMA_CATALOG,
    SchemaError,
    script_io_notes,
    validate_columns,
    validate_row,
)


def test_catalog_has_the_2023_shapes():
    assert SCHEMA_CATALOG["raw_input"] == ("id", "article text")
    assert SCHEMA_CATALOG["labeled"] == ("id", "body", "summary")
    assert "input_text" in SCHEMA_CATALOG["public_eval"]


def test_validate_columns_missing_and_extra():
    try:
        validate_columns(["id"], "labeled")
    except SchemaError as exc:
        assert "summary" in exc.missing
    else:
        raise AssertionError("expected SchemaError")
    try:
        validate_columns(["id", "body", "summary", "bonus"], "labeled")
    except SchemaError as exc:
        assert "bonus" in exc.extra
    else:
        raise AssertionError("expected SchemaError")
    validate_columns(["id", "body", "summary"], "labeled")


def test_validate_row_rejects_empty():
    try:
        validate_row({"id": "x", "body": "tekst", "summary": "  "}, "labeled")
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
    validate_row({"id": "x", "body": "tekst", "summary": "kort", "extra": 1}, "labeled")


def test_script_notes_mention_known_scars():
    blob = " ".join(script_io_notes())
    assert "[:10]" in blob
    assert "dan_Latn" in blob
    assert "article text" in blob
