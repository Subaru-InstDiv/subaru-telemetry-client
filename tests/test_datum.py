import pytest

from subaru.sts.client.datum import Datum, DatumFormat


class TestDatumFormat:
    """Tests for DatumFormat enum."""

    def test_datum_format_values(self):
        """Test that DatumFormat has expected values."""
        assert DatumFormat.INTEGER == 0
        assert DatumFormat.FLOAT == 1
        assert DatumFormat.TEXT == 2
        assert DatumFormat.INTEGER_WITH_TEXT == 3
        assert DatumFormat.FLOAT_WITH_TEXT == 4
        assert DatumFormat.EXPONENT == 5

    def test_datum_format_names(self):
        """Test that DatumFormat members have correct names."""
        assert DatumFormat(0).name == "INTEGER"
        assert DatumFormat(1).name == "FLOAT"
        assert DatumFormat(2).name == "TEXT"
        assert DatumFormat(3).name == "INTEGER_WITH_TEXT"
        assert DatumFormat(4).name == "FLOAT_WITH_TEXT"
        assert DatumFormat(5).name == "EXPONENT"


class TestDatumBackwardCompatibility:
    """Tests for backward compatibility class constants."""

    def test_class_constants_exist(self):
        """Test that class constants match DatumFormat values."""
        assert Datum.INTEGER == DatumFormat.INTEGER
        assert Datum.FLOAT == DatumFormat.FLOAT
        assert Datum.TEXT == DatumFormat.TEXT
        assert Datum.INTEGER_WITH_TEXT == DatumFormat.INTEGER_WITH_TEXT
        assert Datum.FLOAT_WITH_TEXT == DatumFormat.FLOAT_WITH_TEXT
        assert Datum.EXPONENT == DatumFormat.EXPONENT


class TestDatumInit:
    """Tests for Datum initialization."""

    def test_default_initialization(self):
        """Test creating Datum with default values."""
        d = Datum()
        assert d.id is None
        assert d.format == 0
        assert d.timestamp == 0
        assert d.value == 0

    def test_initialization_with_all_params(self):
        """Test creating Datum with all parameters."""
        d = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1234567890.5, value=42)
        assert d.id == 123
        assert d.format == DatumFormat.INTEGER
        assert d.timestamp == 1234567890.5
        assert d.value == 42

    def test_invalid_format_raises_error(self):
        """Test that invalid format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid format: 99"):
            Datum(format=99)

    def test_invalid_format_negative_raises_error(self):
        """Test that negative format raises ValueError."""
        with pytest.raises(ValueError, match="Invalid format: -1"):
            Datum(format=-1)


class TestDatumValidation:
    """Tests for value validation."""

    # INTEGER format validation
    def test_integer_format_with_int_value(self):
        """Test INTEGER format accepts int values."""
        d = Datum(format=DatumFormat.INTEGER, value=42)
        assert d.value == 42

    def test_integer_format_with_none_value(self):
        """Test INTEGER format accepts None values."""
        d = Datum(format=DatumFormat.INTEGER, value=None)
        assert d.value is None

    def test_integer_format_rejects_float(self):
        """Test INTEGER format rejects float values."""
        with pytest.raises(ValueError, match="INTEGER format requires int value"):
            Datum(format=DatumFormat.INTEGER, value=42.5)

    def test_integer_format_rejects_string(self):
        """Test INTEGER format rejects string values."""
        with pytest.raises(ValueError, match="INTEGER format requires int value"):
            Datum(format=DatumFormat.INTEGER, value="42")

    def test_integer_format_rejects_bool(self):
        """Test INTEGER format rejects bool values."""
        with pytest.raises(ValueError, match="INTEGER format requires int value"):
            Datum(format=DatumFormat.INTEGER, value=True)

    # FLOAT format validation
    def test_float_format_with_float_value(self):
        """Test FLOAT format accepts float values."""
        d = Datum(format=DatumFormat.FLOAT, value=3.14)
        assert d.value == 3.14

    def test_float_format_with_int_value(self):
        """Test FLOAT format accepts int values."""
        d = Datum(format=DatumFormat.FLOAT, value=42)
        assert d.value == 42

    def test_float_format_rejects_string(self):
        """Test FLOAT format rejects string values."""
        with pytest.raises(ValueError, match="FLOAT/EXPONENT format requires numeric value"):
            Datum(format=DatumFormat.FLOAT, value="3.14")

    def test_float_format_rejects_bool(self):
        """Test FLOAT format rejects bool values."""
        with pytest.raises(ValueError, match="FLOAT/EXPONENT format requires numeric value"):
            Datum(format=DatumFormat.FLOAT, value=False)

    # EXPONENT format validation
    def test_exponent_format_with_float_value(self):
        """Test EXPONENT format accepts float values."""
        d = Datum(format=DatumFormat.EXPONENT, value=1.23e-10)
        assert d.value == 1.23e-10

    def test_exponent_format_with_int_value(self):
        """Test EXPONENT format accepts int values."""
        d = Datum(format=DatumFormat.EXPONENT, value=1000)
        assert d.value == 1000

    def test_exponent_format_rejects_string(self):
        """Test EXPONENT format rejects string values."""
        with pytest.raises(ValueError, match="FLOAT/EXPONENT format requires numeric value"):
            Datum(format=DatumFormat.EXPONENT, value="1e-10")

    # TEXT format validation
    def test_text_format_with_string_value(self):
        """Test TEXT format accepts string values."""
        d = Datum(format=DatumFormat.TEXT, value="Hello World")
        assert d.value == "Hello World"

    def test_text_format_with_empty_string(self):
        """Test TEXT format accepts empty strings."""
        d = Datum(format=DatumFormat.TEXT, value="")
        assert d.value == ""

    def test_text_format_rejects_int(self):
        """Test TEXT format rejects int values."""
        with pytest.raises(ValueError, match="TEXT format requires str value"):
            Datum(format=DatumFormat.TEXT, value=42)

    def test_text_format_rejects_float(self):
        """Test TEXT format rejects float values."""
        with pytest.raises(ValueError, match="TEXT format requires str value"):
            Datum(format=DatumFormat.TEXT, value=3.14)

    # INTEGER_WITH_TEXT format validation
    def test_integer_with_text_format_valid(self):
        """Test INTEGER_WITH_TEXT format accepts valid tuples."""
        d = Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=(42, "units"))
        assert d.value == (42, "units")

    def test_integer_with_text_format_rejects_wrong_tuple_length(self):
        """Test INTEGER_WITH_TEXT format rejects tuples of wrong length."""
        with pytest.raises(
            ValueError, match="INTEGER_WITH_TEXT format requires tuple of \\(int, str\\)"
        ):
            Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=(42,))

    def test_integer_with_text_format_rejects_non_tuple(self):
        """Test INTEGER_WITH_TEXT format rejects non-tuple values."""
        with pytest.raises(
            ValueError, match="INTEGER_WITH_TEXT format requires tuple of \\(int, str\\)"
        ):
            Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=42)

    def test_integer_with_text_format_rejects_float_first_element(self):
        """Test INTEGER_WITH_TEXT format rejects float as first element."""
        with pytest.raises(
            ValueError, match="INTEGER_WITH_TEXT format requires int as first element"
        ):
            Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=(3.14, "text"))

    def test_integer_with_text_format_rejects_bool_first_element(self):
        """Test INTEGER_WITH_TEXT format rejects bool as first element."""
        with pytest.raises(
            ValueError, match="INTEGER_WITH_TEXT format requires int as first element"
        ):
            Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=(True, "text"))

    def test_integer_with_text_format_rejects_int_second_element(self):
        """Test INTEGER_WITH_TEXT format rejects int as second element."""
        with pytest.raises(
            ValueError, match="INTEGER_WITH_TEXT format requires str as second element"
        ):
            Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=(42, 100))

    # FLOAT_WITH_TEXT format validation
    def test_float_with_text_format_valid_float(self):
        """Test FLOAT_WITH_TEXT format accepts valid float tuples."""
        d = Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=(3.14, "meters"))
        assert d.value == (3.14, "meters")

    def test_float_with_text_format_valid_int(self):
        """Test FLOAT_WITH_TEXT format accepts int as first element."""
        d = Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=(42, "meters"))
        assert d.value == (42, "meters")

    def test_float_with_text_format_rejects_wrong_tuple_length(self):
        """Test FLOAT_WITH_TEXT format rejects tuples of wrong length."""
        with pytest.raises(
            ValueError, match="FLOAT_WITH_TEXT format requires tuple of \\(float, str\\)"
        ):
            Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=(3.14, "text", "extra"))

    def test_float_with_text_format_rejects_non_tuple(self):
        """Test FLOAT_WITH_TEXT format rejects non-tuple values."""
        with pytest.raises(
            ValueError, match="FLOAT_WITH_TEXT format requires tuple of \\(float, str\\)"
        ):
            Datum(format=DatumFormat.FLOAT_WITH_TEXT, value="text")

    def test_float_with_text_format_rejects_string_first_element(self):
        """Test FLOAT_WITH_TEXT format rejects string as first element."""
        with pytest.raises(
            ValueError, match="FLOAT_WITH_TEXT format requires numeric as first element"
        ):
            Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=("3.14", "text"))

    def test_float_with_text_format_rejects_bool_first_element(self):
        """Test FLOAT_WITH_TEXT format rejects bool as first element."""
        with pytest.raises(
            ValueError, match="FLOAT_WITH_TEXT format requires numeric as first element"
        ):
            Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=(False, "text"))

    def test_float_with_text_format_rejects_int_second_element(self):
        """Test FLOAT_WITH_TEXT format rejects int as second element."""
        with pytest.raises(
            ValueError, match="FLOAT_WITH_TEXT format requires str as second element"
        ):
            Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=(3.14, 42))


class TestDatumStringRepresentations:
    """Tests for string representations."""

    def test_repr_basic(self):
        """Test __repr__ method."""
        d = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1234567890.5, value=42)
        assert (
            repr(d)
            == "Datum(id=123, format=<DatumFormat.INTEGER: 0>, timestamp=1234567890.5, value=42)"
        )

    def test_repr_with_none_id(self):
        """Test __repr__ with None id."""
        d = Datum(id=None, format=DatumFormat.FLOAT, timestamp=0, value=3.14)
        assert repr(d) == "Datum(id=None, format=<DatumFormat.FLOAT: 1>, timestamp=0, value=3.14)"

    def test_repr_with_text(self):
        """Test __repr__ with text value."""
        d = Datum(id=456, format=DatumFormat.TEXT, timestamp=100.5, value="test")
        assert (
            repr(d) == "Datum(id=456, format=<DatumFormat.TEXT: 2>, timestamp=100.5, value='test')"
        )

    def test_str_integer(self):
        """Test __str__ method with INTEGER format."""
        d = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1234567890.5, value=42)
        assert str(d) == "Datum(id=123, format=INTEGER, timestamp=1234567890.5, value=42)"

    def test_str_float(self):
        """Test __str__ method with FLOAT format."""
        d = Datum(id=456, format=DatumFormat.FLOAT, timestamp=100.0, value=3.14)
        assert str(d) == "Datum(id=456, format=FLOAT, timestamp=100.0, value=3.14)"

    def test_str_text(self):
        """Test __str__ method with TEXT format."""
        d = Datum(id=789, format=DatumFormat.TEXT, timestamp=200.0, value="hello")
        assert str(d) == "Datum(id=789, format=TEXT, timestamp=200.0, value=hello)"

    def test_str_integer_with_text(self):
        """Test __str__ method with INTEGER_WITH_TEXT format."""
        d = Datum(
            id=111, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=300.0, value=(42, "units")
        )
        assert (
            str(d)
            == "Datum(id=111, format=INTEGER_WITH_TEXT, timestamp=300.0, value=(42, 'units'))"
        )

    def test_str_float_with_text(self):
        """Test __str__ method with FLOAT_WITH_TEXT format."""
        d = Datum(
            id=222, format=DatumFormat.FLOAT_WITH_TEXT, timestamp=400.0, value=(3.14, "meters")
        )
        assert (
            str(d)
            == "Datum(id=222, format=FLOAT_WITH_TEXT, timestamp=400.0, value=(3.14, 'meters'))"
        )

    def test_str_exponent(self):
        """Test __str__ method with EXPONENT format."""
        d = Datum(id=333, format=DatumFormat.EXPONENT, timestamp=500.0, value=1.23e-10)
        assert str(d) == "Datum(id=333, format=EXPONENT, timestamp=500.0, value=1.23e-10)"


class TestDatumEquality:
    """Tests for equality comparison."""

    def test_equal_datums(self):
        """Test that identical datums are equal."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        assert d1 == d2

    def test_equal_datums_with_none_id(self):
        """Test equality with None id."""
        d1 = Datum(id=None, format=DatumFormat.FLOAT, timestamp=2000.0, value=3.14)
        d2 = Datum(id=None, format=DatumFormat.FLOAT, timestamp=2000.0, value=3.14)
        assert d1 == d2

    def test_unequal_ids(self):
        """Test that datums with different ids are not equal."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=456, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        assert d1 != d2

    def test_unequal_formats(self):
        """Test that datums with different formats are not equal."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=123, format=DatumFormat.FLOAT, timestamp=1000.0, value=42)
        assert d1 != d2

    def test_unequal_timestamps(self):
        """Test that datums with different timestamps are not equal."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=2000.0, value=42)
        assert d1 != d2

    def test_unequal_values(self):
        """Test that datums with different values are not equal."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=99)
        assert d1 != d2

    def test_equality_with_tuple_values(self):
        """Test equality with tuple values."""
        d1 = Datum(
            id=123, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=1000.0, value=(42, "units")
        )
        d2 = Datum(
            id=123, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=1000.0, value=(42, "units")
        )
        assert d1 == d2

    def test_inequality_with_different_tuple_values(self):
        """Test inequality with different tuple values."""
        d1 = Datum(
            id=123, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=1000.0, value=(42, "units")
        )
        d2 = Datum(
            id=123, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=1000.0, value=(42, "meters")
        )
        assert d1 != d2

    def test_equality_with_non_datum(self):
        """Test equality comparison with non-Datum objects."""
        d = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        assert d != "not a datum"
        assert d != 42
        assert d != None


class TestDatumHash:
    """Tests for hash functionality."""

    def test_hashable(self):
        """Test that Datum objects are hashable."""
        d = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        assert isinstance(hash(d), int)

    def test_equal_datums_have_same_hash(self):
        """Test that equal datums have the same hash."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        assert hash(d1) == hash(d2)

    def test_datum_in_set(self):
        """Test that Datum can be used in sets."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=456, format=DatumFormat.FLOAT, timestamp=2000.0, value=3.14)
        d3 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)

        datum_set = {d1, d2, d3}
        assert len(datum_set) == 2  # d1 and d3 are equal

    def test_datum_as_dict_key(self):
        """Test that Datum can be used as dict keys."""
        d1 = Datum(id=123, format=DatumFormat.INTEGER, timestamp=1000.0, value=42)
        d2 = Datum(id=456, format=DatumFormat.FLOAT, timestamp=2000.0, value=3.14)

        datum_dict = {d1: "first", d2: "second"}
        assert datum_dict[d1] == "first"
        assert datum_dict[d2] == "second"

    def test_hash_with_tuple_value(self):
        """Test hashing with tuple values."""
        d = Datum(
            id=123, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=1000.0, value=(42, "units")
        )
        assert isinstance(hash(d), int)


class TestDatumFactoryMethods:
    """Tests for factory methods."""

    def test_integer_factory(self):
        """Test Integer factory method."""
        d = Datum.Integer(id=123, timestamp=1000.0, value=42)
        assert d.id == 123
        assert d.format == DatumFormat.INTEGER
        assert d.timestamp == 1000.0
        assert d.value == 42

    def test_integer_factory_defaults(self):
        """Test Integer factory method with defaults."""
        d = Datum.Integer()
        assert d.id is None
        assert d.format == DatumFormat.INTEGER
        assert d.timestamp == 0
        assert d.value == 0

    def test_float_factory(self):
        """Test Float factory method."""
        d = Datum.Float(id=456, timestamp=2000.0, value=3.14)
        assert d.id == 456
        assert d.format == DatumFormat.FLOAT
        assert d.timestamp == 2000.0
        assert d.value == 3.14

    def test_float_factory_defaults(self):
        """Test Float factory method with defaults."""
        d = Datum.Float()
        assert d.id is None
        assert d.format == DatumFormat.FLOAT
        assert d.timestamp == 0
        assert d.value == 0.0

    def test_text_factory(self):
        """Test Text factory method."""
        d = Datum.Text(id=789, timestamp=3000.0, value="hello")
        assert d.id == 789
        assert d.format == DatumFormat.TEXT
        assert d.timestamp == 3000.0
        assert d.value == "hello"

    def test_text_factory_defaults(self):
        """Test Text factory method with defaults."""
        d = Datum.Text()
        assert d.id is None
        assert d.format == DatumFormat.TEXT
        assert d.timestamp == 0
        assert d.value == ""

    def test_integer_with_text_factory(self):
        """Test IntegerWithText factory method."""
        d = Datum.IntegerWithText(id=111, timestamp=4000.0, value=(42, "units"))
        assert d.id == 111
        assert d.format == DatumFormat.INTEGER_WITH_TEXT
        assert d.timestamp == 4000.0
        assert d.value == (42, "units")

    def test_integer_with_text_factory_defaults(self):
        """Test IntegerWithText factory method with defaults."""
        d = Datum.IntegerWithText()
        assert d.id is None
        assert d.format == DatumFormat.INTEGER_WITH_TEXT
        assert d.timestamp == 0
        assert d.value == (0, "")

    def test_float_with_text_factory(self):
        """Test FloatWithText factory method."""
        d = Datum.FloatWithText(id=222, timestamp=5000.0, value=(3.14, "meters"))
        assert d.id == 222
        assert d.format == DatumFormat.FLOAT_WITH_TEXT
        assert d.timestamp == 5000.0
        assert d.value == (3.14, "meters")

    def test_float_with_text_factory_defaults(self):
        """Test FloatWithText factory method with defaults."""
        d = Datum.FloatWithText()
        assert d.id is None
        assert d.format == DatumFormat.FLOAT_WITH_TEXT
        assert d.timestamp == 0
        assert d.value == (0.0, "")

    def test_exponent_factory(self):
        """Test Exponent factory method."""
        d = Datum.Exponent(id=333, timestamp=6000.0, value=1.23e-10)
        assert d.id == 333
        assert d.format == DatumFormat.EXPONENT
        assert d.timestamp == 6000.0
        assert d.value == 1.23e-10

    def test_exponent_factory_defaults(self):
        """Test Exponent factory method with defaults."""
        d = Datum.Exponent()
        assert d.id is None
        assert d.format == DatumFormat.EXPONENT
        assert d.timestamp == 0
        assert d.value == 0.0


class TestEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_negative_id(self):
        """Test datum with negative id."""
        d = Datum(id=-1, format=DatumFormat.INTEGER, value=42)
        assert d.id == -1

    def test_zero_id(self):
        """Test datum with zero id."""
        d = Datum(id=0, format=DatumFormat.INTEGER, value=42)
        assert d.id == 0

    def test_very_large_integer(self):
        """Test datum with very large integer value."""
        large_value = 10**20
        d = Datum(format=DatumFormat.INTEGER, value=large_value)
        assert d.value == large_value

    def test_negative_integer(self):
        """Test datum with negative integer value."""
        d = Datum(format=DatumFormat.INTEGER, value=-999)
        assert d.value == -999

    def test_negative_float(self):
        """Test datum with negative float value."""
        d = Datum(format=DatumFormat.FLOAT, value=-3.14)
        assert d.value == -3.14

    def test_very_small_float(self):
        """Test datum with very small float value."""
        d = Datum(format=DatumFormat.EXPONENT, value=1e-100)
        assert d.value == 1e-100

    def test_very_large_float(self):
        """Test datum with very large float value."""
        d = Datum(format=DatumFormat.EXPONENT, value=1e100)
        assert d.value == 1e100

    def test_negative_timestamp(self):
        """Test datum with negative timestamp (before Unix epoch)."""
        d = Datum(timestamp=-1000.0, format=DatumFormat.INTEGER, value=42)
        assert d.timestamp == -1000.0

    def test_unicode_text(self):
        """Test datum with unicode text."""
        d = Datum(format=DatumFormat.TEXT, value="Hello 世界 🌍")
        assert d.value == "Hello 世界 🌍"

    def test_empty_tuple_text(self):
        """Test datum with empty string in tuple."""
        d = Datum(format=DatumFormat.INTEGER_WITH_TEXT, value=(42, ""))
        assert d.value == (42, "")

    def test_unicode_in_tuple(self):
        """Test datum with unicode in tuple text."""
        d = Datum(format=DatumFormat.FLOAT_WITH_TEXT, value=(3.14, "μm"))
        assert d.value == (3.14, "μm")

    def test_special_float_values(self):
        """Test datum with special float values."""
        d_inf = Datum(format=DatumFormat.FLOAT, value=float("inf"))
        assert d_inf.value == float("inf")

        d_ninf = Datum(format=DatumFormat.FLOAT, value=float("-inf"))
        assert d_ninf.value == float("-inf")

        # NaN is special - it's not equal to itself
        d_nan = Datum(format=DatumFormat.FLOAT, value=float("nan"))
        assert d_nan.value != d_nan.value  # NaN != NaN
