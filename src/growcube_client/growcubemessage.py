from typing_extensions import Self
"""
Growcube client library
https://github.com/jonnybergdahl/Python-growcube-client

Author: Jonny Bergdahl
Date: 2023-09-05
"""


class GrowcubeMessage:
    """
    Growcube protocol message base class
    """
    HEADER = 'elea'
    DELIMITER = '#'
    END_DELIMITER = '#'
    EMPTY_MESSAGE = HEADER + "00" + DELIMITER + DELIMITER + DELIMITER

    def __init__(self, command:int, payload:str, data:bytes):
        """
        GrowcubeMessage constructor
        Args:
            command: Command value
            payload: Message payload
            data: The complete message as bytes
        """
        self._command = command
        self._payload = payload
        self._data = data

    @property
    def command(self):
        """
        Command value
        Returns:
            Command value
        """
        return self._command

    @property
    def payload(self):
        """
        Message payload
        Returns:
            Message payload
        """
        return self._payload

    @property
    def data(self) -> bytes:
        """
        The complete message as bytes
        Returns:
            The complete message as bytes
        """
        return self._data

    @staticmethod
    def from_bytes(data: bytearray) -> (int, Self):
        """
        Tries to construct a complete GrowcubeMessage from the data, and returns
        the index of the next non consumed data in the buffer, together with the message
        Converts a byte array to a GrowcubeMessage instance
        Args:
            data: the current data buffer

        Returns:
            The index of the next non consumed data in the buffer, together with the message,
            or the next found start index and None if the message is incomplete
        """
        message_str = data.decode('ascii')

        start_index = message_str.find(GrowcubeMessage.HEADER)
        if start_index == -1:
            # Header not found, return
            return 0, None

        # Move to start of message
        message_str = message_str[start_index:]

        parts = message_str[len(GrowcubeMessage.HEADER):].split(GrowcubeMessage.DELIMITER)
        if len(parts) < 3:
            # Still don't have the complete message
            return start_index, None

        try:
            payload_len = int(parts[1])
        except ValueError:
            raise ValueError('Invalid payload length')

        payload = parts[2]
        payload_length = len(GrowcubeMessage.EMPTY_MESSAGE) + len(str(payload_len)) + len(payload)
        consumed_index = start_index + payload_length
        if len(data) < consumed_index:
            # Still incomplete
            return start_index, None

        if not message_str[payload_length - 1] == GrowcubeMessage.DELIMITER:
            raise ValueError('Invalid message end delimiter')

        try:
            # Parse command value
            command = int(parts[0])
        except ValueError:
            raise ValueError('Invalid command')

        return consumed_index, GrowcubeMessage(command, payload, data[start_index:consumed_index])

    @staticmethod
    def to_bytes(command: int, data: str) -> bytes:
        """
        Creates a bytearray representation of a message as used in the protocol
        Args:
            command: Command value
            data: Data to send

        Returns:
            A bytearray representation of a message as used in the protocol
        """
        result = f"{GrowcubeMessage.HEADER}{command:02d}{GrowcubeMessage.DELIMITER}{len(data)}" + \
                 f"{GrowcubeMessage.DELIMITER}{data}{GrowcubeMessage.DELIMITER}"
        return result.encode("ascii")
