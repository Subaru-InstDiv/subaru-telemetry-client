import socket
import struct
import time
from unittest.mock import MagicMock, call, patch

import pytest

from subaru.sts.client import Datum, Radio


@pytest.fixture
def sample_data():
    """Create a list of STS data that can be written to STS for testing."""
    # Long text data (62*3 bytes)
    text = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz" * 3
    timestamp = int(time.time())
    return [
        Datum.Integer(id=1090, timestamp=timestamp, value=1),
        Datum.Float(id=1091, timestamp=timestamp, value=1.0),
        Datum.Text(id=1092, timestamp=timestamp, value=text),
        Datum.IntegerWithText(id=1093, timestamp=timestamp, value=(1, text)),
        Datum.FloatWithText(id=1094, timestamp=timestamp, value=(1.0, text)),
        Datum.Exponent(id=1095, timestamp=timestamp, value=1.0),
    ]


@pytest.fixture
def sample_ids():
    """Create a list of IDs for testing receive functionality."""
    return [1090, 1091, 1092, 1093, 1094, 1095]


class TestRadioInit:
    """Tests for Radio initialization."""

    def test_default_constructor(self):
        """Test the default constructor of the Radio class."""
        radio = Radio()
        assert radio.host == "sts"
        assert radio.port == 9001
        assert radio.timeout == 5.0

    def test_constructor_with_custom_host(self):
        """Test constructor with custom host."""
        radio = Radio(host="localhost")
        assert radio.host == "localhost"
        assert radio.port == 9001
        assert radio.timeout == 5.0

    def test_constructor_with_custom_port(self):
        """Test constructor with custom port."""
        radio = Radio(port=8080)
        assert radio.host == "sts"
        assert radio.port == 8080
        assert radio.timeout == 5.0

    def test_constructor_with_custom_timeout(self):
        """Test constructor with custom timeout."""
        radio = Radio(timeout=10.0)
        assert radio.host == "sts"
        assert radio.port == 9001
        assert radio.timeout == 10.0

    def test_constructor_with_all_params(self):
        """Test constructor with all custom parameters."""
        radio = Radio(host="192.168.1.1", port=8080, timeout=10.0)
        assert radio.host == "192.168.1.1"
        assert radio.port == 8080
        assert radio.timeout == 10.0

    def test_repr(self):
        """Test __repr__ method."""
        radio = Radio(host="testhost", port=1234, timeout=2.5)
        expected = "Radio(host='testhost', port=1234, timeout=2.5)"
        assert repr(radio) == expected

    def test_repr_default(self):
        """Test __repr__ with default values."""
        radio = Radio()
        expected = "Radio(host='sts', port=9001, timeout=5.0)"
        assert repr(radio) == expected


class TestRadioPack:
    """Tests for Radio.pack() static method."""

    def test_pack_integer(self):
        """Test packing INTEGER format datum."""
        datum = Datum.Integer(id=100, timestamp=1234567890, value=42)
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header size (10 bytes) + integer size (4 bytes) = 14 bytes
        assert len(packet) == 14

    def test_pack_float(self):
        """Test packing FLOAT format datum."""
        datum = Datum.Float(id=200, timestamp=1234567890, value=3.14)
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header size (10 bytes) + float size (8 bytes) = 18 bytes
        assert len(packet) == 18

    def test_pack_exponent(self):
        """Test packing EXPONENT format datum."""
        datum = Datum.Exponent(id=300, timestamp=1234567890, value=1.23e-10)
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header size (10 bytes) + float size (8 bytes) = 18 bytes
        assert len(packet) == 18

    def test_pack_text(self):
        """Test packing TEXT format datum."""
        datum = Datum.Text(id=400, timestamp=1234567890, value="Hello World")
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header size (10 bytes) + text length (11 bytes) = 21 bytes
        assert len(packet) == 21

    def test_pack_text_empty(self):
        """Test packing TEXT format with empty string."""
        datum = Datum.Text(id=500, timestamp=1234567890, value="")
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header size only (10 bytes)
        assert len(packet) == 10

    def test_pack_text_maximum_size(self):
        """Test packing TEXT format with text exceeding maximum size."""
        # Maximum packet size is 127 bytes
        long_text = "A" * 200  # Exceeds maximum
        datum = Datum.Text(id=600, timestamp=1234567890, value=long_text)
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Should be capped at maximum packet size (127 bytes)
        assert len(packet) == 127

    def test_pack_integer_with_text(self):
        """Test packing INTEGER_WITH_TEXT format datum."""
        datum = Datum.IntegerWithText(id=700, timestamp=1234567890, value=(42, "units"))
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header (10) + integer (4) + text (5) = 19 bytes
        assert len(packet) == 19

    def test_pack_integer_with_text_empty_string(self):
        """Test packing INTEGER_WITH_TEXT with empty string."""
        datum = Datum.IntegerWithText(id=800, timestamp=1234567890, value=(99, ""))
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header (10) + integer (4) = 14 bytes
        assert len(packet) == 14

    def test_pack_integer_with_text_maximum_size(self):
        """Test packing INTEGER_WITH_TEXT with text exceeding maximum size."""
        long_text = "B" * 200
        datum = Datum.IntegerWithText(id=900, timestamp=1234567890, value=(123, long_text))
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Should be capped at maximum packet size
        assert len(packet) == 127

    def test_pack_float_with_text(self):
        """Test packing FLOAT_WITH_TEXT format datum."""
        datum = Datum.FloatWithText(id=1000, timestamp=1234567890, value=(3.14, "meters"))
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header (10) + float (8) + text (6) = 24 bytes
        assert len(packet) == 24

    def test_pack_float_with_text_empty_string(self):
        """Test packing FLOAT_WITH_TEXT with empty string."""
        datum = Datum.FloatWithText(id=1100, timestamp=1234567890, value=(2.71, ""))
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Header (10) + float (8) = 18 bytes
        assert len(packet) == 18

    def test_pack_float_with_text_maximum_size(self):
        """Test packing FLOAT_WITH_TEXT with text exceeding maximum size."""
        long_text = "C" * 200
        datum = Datum.FloatWithText(id=1200, timestamp=1234567890, value=(9.81, long_text))
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        # Should be capped at maximum packet size
        assert len(packet) == 127

    def test_pack_with_invalid_format(self):
        """Test packing with invalid data type raises RuntimeError."""
        # Create datum with invalid format by bypassing validation
        datum = Datum.__new__(Datum)
        datum.id = 0
        datum.format = 6
        datum.timestamp = 0
        datum.value = 0
        with pytest.raises(RuntimeError, match="Invalid data type"):
            Radio.pack(datum)

    def test_pack_header_has_flag_set(self):
        """Test that packed header has the high bit (0x80) set in size byte."""
        datum = Datum.Integer(id=1, timestamp=1000, value=1)
        packet = Radio.pack(datum)

        # First byte should have 0x80 flag set
        assert packet[0] & 0x80 == 0x80

    def test_pack_negative_integer(self):
        """Test packing negative integer value."""
        datum = Datum.Integer(id=1300, timestamp=1234567890, value=-999)
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        assert len(packet) == 14

    def test_pack_negative_float(self):
        """Test packing negative float value."""
        datum = Datum.Float(id=1400, timestamp=1234567890, value=-3.14)
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        assert len(packet) == 18

    def test_pack_unicode_text(self):
        """Test packing text with special characters."""
        # Note: latin-1 encoding is used, so only characters in that range work
        datum = Datum.Text(id=1500, timestamp=1234567890, value="café")
        packet = Radio.pack(datum)

        assert isinstance(packet, bytearray)
        assert len(packet) == 10 + 4  # header + 4 characters


class TestRadioUnpack:
    """Tests for Radio.unpack() static method."""

    def test_unpack_integer(self):
        """Test unpacking INTEGER format packet."""
        original = Datum.Integer(id=100, timestamp=1234567890, value=42)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == original.id
        assert unpacked.format == original.format
        assert unpacked.timestamp == original.timestamp
        assert unpacked.value == original.value

    def test_unpack_float(self):
        """Test unpacking FLOAT format packet."""
        original = Datum.Float(id=200, timestamp=1234567890, value=3.14159)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == original.id
        assert unpacked.format == original.format
        assert unpacked.timestamp == original.timestamp
        assert unpacked.value == pytest.approx(original.value)

    def test_unpack_exponent(self):
        """Test unpacking EXPONENT format packet."""
        original = Datum.Exponent(id=300, timestamp=1234567890, value=1.23e-10)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == original.id
        assert unpacked.format == original.format
        assert unpacked.timestamp == original.timestamp
        assert unpacked.value == pytest.approx(original.value)

    def test_unpack_text(self):
        """Test unpacking TEXT format packet."""
        original = Datum.Text(id=400, timestamp=1234567890, value="Test String")
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == original.id
        assert unpacked.format == original.format
        assert unpacked.timestamp == original.timestamp
        assert unpacked.value == original.value

    def test_unpack_text_empty(self):
        """Test unpacking TEXT format with empty string."""
        original = Datum.Text(id=500, timestamp=1234567890, value="")
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == ""

    def test_unpack_integer_with_text(self):
        """Test unpacking INTEGER_WITH_TEXT format packet."""
        original = Datum.IntegerWithText(id=600, timestamp=1234567890, value=(42, "units"))
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == original.id
        assert unpacked.format == original.format
        assert unpacked.timestamp == original.timestamp
        assert unpacked.value == original.value

    def test_unpack_float_with_text(self):
        """Test unpacking FLOAT_WITH_TEXT format packet."""
        original = Datum.FloatWithText(id=700, timestamp=1234567890, value=(3.14, "meters"))
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == original.id
        assert unpacked.format == original.format
        assert unpacked.timestamp == original.timestamp
        assert unpacked.value[0] == pytest.approx(original.value[0])
        assert unpacked.value[1] == original.value[1]

    def test_unpack_invalid_packet_size(self):
        """Test unpacking with invalid packet size raises RuntimeError."""
        packet = Radio.pack(Datum.Integer(id=0, timestamp=0, value=0))
        # Modify the size byte to create an invalid packet
        packet[0:1] = bytes([18 | 0x80])

        with pytest.raises(RuntimeError, match="Invalid packet size"):
            Radio.unpack(packet)

    def test_unpack_invalid_data_type(self):
        """Test unpacking with invalid data type raises RuntimeError."""
        packet = Radio.pack(Datum.Integer(id=0, timestamp=0, value=0))
        # Modify the format byte to an invalid value
        packet[5:6] = bytes([6])

        with pytest.raises(RuntimeError, match="Invalid data type"):
            Radio.unpack(packet)

    def test_unpack_invalid_header_flag(self):
        """Test unpacking packet without 0x80 flag raises RuntimeError."""
        packet = Radio.pack(Datum.Integer(id=0, timestamp=0, value=0))
        # Clear the 0x80 flag
        packet[0] = packet[0] & 0x7F

        with pytest.raises(RuntimeError, match="Invalid packet header"):
            Radio.unpack(packet)

    def test_unpack_negative_integer(self):
        """Test unpacking negative integer."""
        original = Datum.Integer(id=800, timestamp=1234567890, value=-999)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == -999

    def test_unpack_negative_float(self):
        """Test unpacking negative float."""
        original = Datum.Float(id=900, timestamp=1234567890, value=-2.718)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == pytest.approx(-2.718)


class TestRadioRoundTrip:
    """Tests for pack/unpack round-trip consistency."""

    def test_round_trip_all_formats(self, sample_data):
        """Test if data round-trips through pack and unpack methods."""
        for datum in sample_data:
            packet = Radio.pack(datum)
            unpacked = Radio.unpack(packet)

            assert unpacked.id == datum.id
            assert unpacked.format == datum.format
            assert unpacked.timestamp == datum.timestamp

            # Handle float comparisons with approximate equality
            if datum.format in (Datum.FLOAT, Datum.EXPONENT):
                assert unpacked.value == pytest.approx(datum.value)
            elif datum.format == Datum.FLOAT_WITH_TEXT:
                # FLOAT_WITH_TEXT may have truncated text
                # Header (10) + float (8) = 18 bytes, so max text is 109 bytes
                max_text_len = Radio._MAXIMUM_PACKET_SIZE - Radio._HEADER_SIZE - Radio._FLOAT_SIZE
                expected_value = (datum.value[0], datum.value[1][:max_text_len])
                assert unpacked.value[0] == pytest.approx(expected_value[0])
                assert unpacked.value[1] == expected_value[1]
            elif datum.format == Datum.TEXT:
                # TEXT may be truncated due to maximum packet size (127 bytes)
                # Header is 10 bytes, so max text is 117 bytes
                expected_value = datum.value[: Radio._MAXIMUM_PACKET_SIZE - Radio._HEADER_SIZE]
                assert unpacked.value == expected_value
            elif datum.format == Datum.INTEGER_WITH_TEXT:
                # INTEGER_WITH_TEXT may have truncated text
                # Header (10) + int (4) = 14 bytes, so max text is 113 bytes
                max_text_len = Radio._MAXIMUM_PACKET_SIZE - Radio._HEADER_SIZE - Radio._INTEGER_SIZE
                expected_value = (datum.value[0], datum.value[1][:max_text_len])
                assert unpacked.value == expected_value
            else:
                assert unpacked.value == datum.value

    def test_round_trip_large_integer(self):
        """Test round-trip with large integer values."""
        original = Datum.Integer(id=1000, timestamp=2000000000, value=2147483647)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == original.value

    def test_round_trip_very_small_exponent(self):
        """Test round-trip with very small exponent values."""
        original = Datum.Exponent(id=1100, timestamp=1500000000, value=1e-100)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == pytest.approx(original.value)

    def test_round_trip_very_large_exponent(self):
        """Test round-trip with very large exponent values."""
        original = Datum.Exponent(id=1200, timestamp=1600000000, value=1e100)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == pytest.approx(original.value)


class TestRadioTransmit:
    """Tests for Radio.transmit() method."""

    @patch("socket.socket")
    def test_transmit_success(self, mock_socket_class, sample_data):
        """Test successful transmit operation."""
        # Setup mock socket
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.side_effect = ["OK: Write On\n", "OK: Write Off\n"]
        mock_socket.makefile.return_value = mock_file

        # Perform transmit
        radio = Radio()
        radio.transmit(sample_data)

        # Verify socket operations
        mock_socket_class.assert_called_once_with(socket.AF_INET, socket.SOCK_STREAM)
        mock_socket.settimeout.assert_called_once_with(5.0)
        mock_socket.connect.assert_called_once_with(("sts", 9001))

        # Verify commands sent
        calls = mock_socket.sendall.call_args_list
        assert calls[0] == call(b"W\n")  # Enter write mode
        # Then 6 data packets
        assert (
            len([c for c in calls if c != call(b"W\n") and c != call(b"\n") and c != call(b"Q\n")])
            == 6
        )
        assert call(b"\n") in calls  # Exit write mode
        assert call(b"Q\n") in calls  # Quit command

        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_transmit_with_custom_timeout(self, mock_socket_class):
        """Test transmit with custom timeout."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.side_effect = ["OK: Write On\n", "OK: Write Off\n"]
        mock_socket.makefile.return_value = mock_file

        radio = Radio(timeout=10.0)
        radio.transmit([Datum.Integer(id=1, timestamp=1000, value=1)])

        mock_socket.settimeout.assert_called_once_with(10.0)

    @patch("socket.socket")
    def test_transmit_invalid_response(self, mock_socket_class):
        """Test transmit with invalid server response."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.return_value = "ERROR: Invalid\n"
        mock_socket.makefile.return_value = mock_file

        radio = Radio()
        with pytest.raises(RuntimeError, match="Invalid response"):
            radio.transmit([Datum.Integer(id=1, timestamp=1000, value=1)])

        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_transmit_connection_error(self, mock_socket_class):
        """Test transmit handles connection errors."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = OSError("Connection refused")

        radio = Radio()
        with pytest.raises(socket.error):
            radio.transmit([Datum.Integer(id=1, timestamp=1000, value=1)])

        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_transmit_empty_list(self, mock_socket_class):
        """Test transmit with empty data list."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.side_effect = ["OK: Write On\n", "OK: Write Off\n"]
        mock_socket.makefile.return_value = mock_file

        radio = Radio()
        radio.transmit([])

        # Should still go through write mode cycle
        calls = mock_socket.sendall.call_args_list
        assert call(b"W\n") in calls
        assert call(b"\n") in calls
        assert call(b"Q\n") in calls


class TestRadioReceive:
    """Tests for Radio.receive() method."""

    @patch("socket.socket")
    def test_receive_success(self, mock_socket_class, sample_ids):
        """Test successful receive operation."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        # Setup readline mock
        mock_file = MagicMock()
        mock_file.readline.return_value = "OK: Read On\n"
        mock_socket.makefile.return_value = mock_file

        # Create sample packets to return
        sample_packets = [
            Radio.pack(Datum.Integer(id=1090, timestamp=1000, value=1)),
            Radio.pack(Datum.Float(id=1091, timestamp=1001, value=2.0)),
            Radio.pack(Datum.Text(id=1092, timestamp=1002, value="test")),
            Radio.pack(Datum.IntegerWithText(id=1093, timestamp=1003, value=(3, "m"))),
            Radio.pack(Datum.FloatWithText(id=1094, timestamp=1004, value=(4.0, "s"))),
            Radio.pack(Datum.Exponent(id=1095, timestamp=1005, value=5e-5)),
        ]

        # Mock _recv_packet to return our sample packets
        with patch.object(Radio, "_recv_packet", side_effect=sample_packets):
            radio = Radio()
            data = radio.receive(sample_ids)

        # Verify results
        assert len(data) == 6
        assert data[0].id == 1090
        assert data[1].id == 1091
        assert data[2].id == 1092

        # Verify socket operations
        mock_socket.settimeout.assert_called_once_with(5.0)
        mock_socket.connect.assert_called_once_with(("sts", 9001))

        # Verify read mode entered
        calls = mock_socket.sendall.call_args_list
        assert calls[0] == call(b"R\n")

        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_receive_invalid_response(self, mock_socket_class):
        """Test receive with invalid server response."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.return_value = "ERROR: Invalid\n"
        mock_socket.makefile.return_value = mock_file

        radio = Radio()
        with pytest.raises(RuntimeError, match="Invalid response"):
            radio.receive([1, 2, 3])

        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_receive_empty_id_list(self, mock_socket_class):
        """Test receive with empty ID list."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.return_value = "OK: Read On\n"
        mock_socket.makefile.return_value = mock_file

        radio = Radio()
        data = radio.receive([])

        assert data == []
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_receive_with_custom_host_port(self, mock_socket_class):
        """Test receive with custom host and port."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.return_value = "OK: Read On\n"
        mock_socket.makefile.return_value = mock_file

        radio = Radio(host="192.168.1.100", port=8080)
        with patch.object(
            Radio,
            "_recv_packet",
            return_value=Radio.pack(Datum.Integer(id=1, timestamp=1, value=1)),
        ):
            radio.receive([1])

        mock_socket.connect.assert_called_once_with(("192.168.1.100", 8080))

    @patch("socket.socket")
    def test_receive_sends_terminator(self, mock_socket_class):
        """Test that receive sends -1 as terminator."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_file = MagicMock()
        mock_file.readline.return_value = "OK: Read On\n"
        mock_socket.makefile.return_value = mock_file

        sample_packet = Radio.pack(Datum.Integer(id=1, timestamp=1000, value=42))

        with patch.object(Radio, "_recv_packet", return_value=sample_packet):
            radio = Radio()
            radio.receive([1])

        # Find the call with -1 terminator
        calls = mock_socket.sendall.call_args_list
        terminator_call = [c for c in calls if c[0][0] == struct.pack("!i", -1)]
        assert len(terminator_call) == 1


class TestRadioRecvPacket:
    """Tests for Radio._recv_packet() static method."""

    def test_recv_packet_reads_correct_size(self):
        """Test that _recv_packet reads the correct packet size."""
        # Create a sample packet
        original = Datum.Integer(id=123, timestamp=1000, value=999)
        expected_packet = Radio.pack(original)

        # Mock socket that returns our packet
        mock_socket = MagicMock()

        # Mock recv to return data based on MSG_PEEK flag
        def mock_recv(size, flags=0):
            if flags == socket.MSG_PEEK:
                return expected_packet[:size]
            return expected_packet[:size]

        mock_socket.recv.side_effect = mock_recv

        # Mock _recvn to return the full packet
        with patch.object(Radio, "_recvn") as mock_recvn:
            mock_recvn.side_effect = [expected_packet[:1], expected_packet]

            result = Radio._recv_packet(mock_socket)

            # Verify _recvn was called correctly
            assert mock_recvn.call_count == 2
            # First call peeks at header
            assert mock_recvn.call_args_list[0] == call(mock_socket, 1, socket.MSG_PEEK)


class TestRadioRecvn:
    """Tests for Radio._recvn() static method."""

    def test_recvn_single_chunk(self):
        """Test _recvn when data arrives in a single chunk."""
        mock_socket = MagicMock()
        data = b"Hello World"
        mock_socket.recv.return_value = data

        result = Radio._recvn(mock_socket, len(data))

        assert result == bytearray(data)
        mock_socket.recv.assert_called_once_with(len(data), 0)

    def test_recvn_multiple_chunks(self):
        """Test _recvn when data arrives in multiple chunks."""
        mock_socket = MagicMock()
        data = b"Hello World"
        # Return data in 3 chunks
        mock_socket.recv.side_effect = [b"Hello", b" Wor", b"ld"]

        result = Radio._recvn(mock_socket, len(data))

        assert result == bytearray(data)
        assert mock_socket.recv.call_count == 3

    def test_recvn_connection_closed(self):
        """Test _recvn raises error when connection is closed."""
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b""  # Empty bytes indicates closed connection

        with pytest.raises(RuntimeError, match="Connection closed by peer"):
            Radio._recvn(mock_socket, 100)

    def test_recvn_with_msg_peek_flag(self):
        """Test _recvn with MSG_PEEK flag."""
        mock_socket = MagicMock()
        data = b"Test"
        mock_socket.recv.return_value = data

        result = Radio._recvn(mock_socket, len(data), socket.MSG_PEEK)

        assert result == bytearray(data)
        mock_socket.recv.assert_called_once_with(len(data), socket.MSG_PEEK)

    def test_recvn_partial_then_complete(self):
        """Test _recvn with partial data followed by complete data."""
        mock_socket = MagicMock()
        # First recv gets partial data, second completes it
        mock_socket.recv.side_effect = [b"Par", b"tial"]

        result = Radio._recvn(mock_socket, 7)

        assert result == bytearray(b"Partial")
        assert mock_socket.recv.call_count == 2


class TestRadioConstants:
    """Tests for Radio class constants."""

    def test_default_constants(self):
        """Test that class constants have expected values."""
        assert Radio.HOST == "sts"
        assert Radio.PORT == 9001
        assert Radio.TIMEOUT == 5.0

    def test_format_sizes(self):
        """Test that format sizes are correct."""
        assert Radio._HEADER_SIZE == 10
        assert Radio._INTEGER_SIZE == 4
        assert Radio._FLOAT_SIZE == 8

    def test_maximum_packet_size(self):
        """Test maximum packet size constant."""
        assert Radio._MAXIMUM_PACKET_SIZE == 127


class TestRadioEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_pack_unpack_zero_timestamp(self):
        """Test pack/unpack with zero timestamp."""
        original = Datum.Integer(id=1, timestamp=0, value=42)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.timestamp == 0

    def test_pack_unpack_large_timestamp(self):
        """Test pack/unpack with large timestamp."""
        original = Datum.Integer(id=1, timestamp=2147483647, value=42)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.timestamp == 2147483647

    def test_pack_unpack_zero_id(self):
        """Test pack/unpack with zero ID."""
        original = Datum.Integer(id=0, timestamp=1000, value=42)
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.id == 0

    def test_pack_special_float_infinity(self):
        """Test packing positive infinity."""
        original = Datum.Float(id=1, timestamp=1000, value=float("inf"))
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == float("inf")

    def test_pack_special_float_negative_infinity(self):
        """Test packing negative infinity."""
        original = Datum.Float(id=1, timestamp=1000, value=float("-inf"))
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        assert unpacked.value == float("-inf")

    def test_pack_special_float_nan(self):
        """Test packing NaN."""
        original = Datum.Float(id=1, timestamp=1000, value=float("nan"))
        packet = Radio.pack(original)
        unpacked = Radio.unpack(packet)

        # NaN is not equal to itself
        assert unpacked.value != unpacked.value

    @patch("socket.socket")
    def test_transmit_socket_closed_on_exception(self, mock_socket_class):
        """Test that socket is closed even when exception occurs."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = Exception("Test error")

        radio = Radio()
        with pytest.raises(Exception):
            radio.transmit([Datum.Integer(id=1, timestamp=1000, value=1)])

        # Socket should still be closed
        mock_socket.close.assert_called_once()

    @patch("socket.socket")
    def test_receive_socket_closed_on_exception(self, mock_socket_class):
        """Test that socket is closed even when exception occurs in receive."""
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket
        mock_socket.connect.side_effect = Exception("Test error")

        radio = Radio()
        with pytest.raises(Exception):
            radio.receive([1, 2, 3])

        # Socket should still be closed
        mock_socket.close.assert_called_once()
