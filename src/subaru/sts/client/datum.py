from enum import IntEnum


class DatumFormat(IntEnum):
    """Enumeration of STS datum formats."""

    INTEGER = 0
    FLOAT = 1
    TEXT = 2
    INTEGER_WITH_TEXT = 3
    FLOAT_WITH_TEXT = 4
    EXPONENT = 5  # Like FLOAT but may be presented differently on the STS web pages


class Datum:
    """A class to represent STS *datum*.

    Attributes
    ----------
        id: STS datum ID
        format: Data type/format (use DatumFormat enum values)
        timestamp: Timestamp in seconds since Unix epoch
        value: Data value (type depends on format)
    """

    # Data types (formats) - kept for backward compatibility
    INTEGER = DatumFormat.INTEGER
    FLOAT = DatumFormat.FLOAT
    TEXT = DatumFormat.TEXT
    INTEGER_WITH_TEXT = DatumFormat.INTEGER_WITH_TEXT
    FLOAT_WITH_TEXT = DatumFormat.FLOAT_WITH_TEXT
    EXPONENT = DatumFormat.EXPONENT

    def __init__(
        self,
        id: int | None = None,
        format: int = 0,
        timestamp: float = 0,
        value: int | float | str | tuple[int, str] | tuple[float, str] = 0,
    ):
        """Create a Datum object.

        Args:
            id: STS datum ID
            format: Data type (format) - use DatumFormat enum values
            timestamp: Timestamp in seconds since Unix epoch
            value: Data value (type depends on format)

        Raises
        ------
            ValueError: If format is invalid or value type doesn't match format
        """
        if format not in DatumFormat.__members__.values():
            valid_formats = ", ".join(
                f"{name} ({member.value})" for name, member in DatumFormat.__members__.items()
            )
            raise ValueError(f"Invalid format: {format}. Must be one of: {valid_formats}")

        self.id = id
        self.format = format
        self.timestamp = timestamp
        self.value = value

        # Validate value type matches format
        self._validate_value()

    def _validate_value(self) -> None:
        """Validate that the value type matches the format."""
        if self.format == DatumFormat.INTEGER:
            if not isinstance(self.value, (int, type(None))) or isinstance(self.value, bool):
                raise ValueError(
                    f"INTEGER format requires int value, got {type(self.value).__name__}"
                )
        elif self.format in (DatumFormat.FLOAT, DatumFormat.EXPONENT):
            if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
                raise ValueError(
                    f"FLOAT/EXPONENT format requires numeric value, got {type(self.value).__name__}"
                )
        elif self.format == DatumFormat.TEXT:
            if not isinstance(self.value, str):
                raise ValueError(f"TEXT format requires str value, got {type(self.value).__name__}")
        elif self.format == DatumFormat.INTEGER_WITH_TEXT:
            if not isinstance(self.value, tuple) or len(self.value) != 2:
                raise ValueError("INTEGER_WITH_TEXT format requires tuple of (int, str)")
            if not isinstance(self.value[0], int) or isinstance(self.value[0], bool):
                raise ValueError("INTEGER_WITH_TEXT format requires int as first element")
            if not isinstance(self.value[1], str):
                raise ValueError("INTEGER_WITH_TEXT format requires str as second element")
        elif self.format == DatumFormat.FLOAT_WITH_TEXT:
            if not isinstance(self.value, tuple) or len(self.value) != 2:
                raise ValueError("FLOAT_WITH_TEXT format requires tuple of (float, str)")
            if not isinstance(self.value[0], (int, float)) or isinstance(self.value[0], bool):
                raise ValueError("FLOAT_WITH_TEXT format requires numeric as first element")
            if not isinstance(self.value[1], str):
                raise ValueError("FLOAT_WITH_TEXT format requires str as second element")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.id!r}, format={self.format!r}, timestamp={self.timestamp!r}, value={self.value!r})"

    def __str__(self) -> str:
        """Human-readable string representation."""
        format_name = DatumFormat(self.format).name
        return f"Datum(id={self.id}, format={format_name}, timestamp={self.timestamp}, value={self.value})"

    def __eq__(self, other) -> bool:
        """Check equality based on id, format, timestamp, and value."""
        if not isinstance(other, Datum):
            return NotImplemented
        return (
            self.id == other.id
            and self.format == other.format
            and self.timestamp == other.timestamp
            and self.value == other.value
        )

    def __hash__(self) -> int:
        """Make Datum hashable for use in sets and as dict keys."""
        # Convert value to hashable type
        value_hash = self.value if not isinstance(self.value, tuple) else tuple(self.value)
        return hash((self.id, self.format, self.timestamp, value_hash))

    @classmethod
    def Integer(cls, id: int | None = None, timestamp: float = 0, value: int = 0) -> "Datum":
        """Factory method to create a Datum object with INTEGER data.

        Args:
            id: STS datum ID
            timestamp: Timestamp in seconds since Unix epoch
            value: Integer value

        Returns
        -------
            Datum object with INTEGER format
        """
        return cls(id=id, format=DatumFormat.INTEGER, timestamp=timestamp, value=value)

    @classmethod
    def Float(cls, id: int | None = None, timestamp: float = 0, value: float = 0.0) -> "Datum":
        """Factory method to create a Datum object with FLOAT data.

        Args:
            id: STS datum ID
            timestamp: Timestamp in seconds since Unix epoch
            value: Float value

        Returns
        -------
            Datum object with FLOAT format
        """
        return cls(id=id, format=DatumFormat.FLOAT, timestamp=timestamp, value=value)

    @classmethod
    def Text(cls, id: int | None = None, timestamp: float = 0, value: str = "") -> "Datum":
        """Factory method to create a Datum object with TEXT data.

        Args:
            id: STS datum ID
            timestamp: Timestamp in seconds since Unix epoch
            value: Text value

        Returns
        -------
            Datum object with TEXT format
        """
        return cls(id=id, format=DatumFormat.TEXT, timestamp=timestamp, value=value)

    @classmethod
    def IntegerWithText(
        cls, id: int | None = None, timestamp: float = 0, value: tuple[int, str] = (0, "")
    ) -> "Datum":
        """Factory method to create a Datum object with INTEGER and TEXT data.

        Args:
            id: STS datum ID
            timestamp: Timestamp in seconds since Unix epoch
            value: Tuple of (integer, text)

        Returns
        -------
            Datum object with INTEGER_WITH_TEXT format
        """
        return cls(id=id, format=DatumFormat.INTEGER_WITH_TEXT, timestamp=timestamp, value=value)

    @classmethod
    def FloatWithText(
        cls, id: int | None = None, timestamp: float = 0, value: tuple[float, str] = (0.0, "")
    ) -> "Datum":
        """Factory method to create a Datum object with FLOAT and TEXT data.

        Args:
            id: STS datum ID
            timestamp: Timestamp in seconds since Unix epoch
            value: Tuple of (float, text)

        Returns
        -------
            Datum object with FLOAT_WITH_TEXT format
        """
        return cls(id=id, format=DatumFormat.FLOAT_WITH_TEXT, timestamp=timestamp, value=value)

    @classmethod
    def Exponent(cls, id: int | None = None, timestamp: float = 0, value: float = 0.0) -> "Datum":
        """Factory method to create a Datum object with EXPONENT data.

        Args:
            id: STS datum ID
            timestamp: Timestamp in seconds since Unix epoch
            value: Float value (displayed in exponential notation)

        Returns
        -------
            Datum object with EXPONENT format
        """
        return cls(id=id, format=DatumFormat.EXPONENT, timestamp=timestamp, value=value)
