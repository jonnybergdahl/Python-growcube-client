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

    :cvar HEADER: The header for a Growcube protocol message.
    :vartype HEADER: str
    :cvar DELIMITER: The delimiter used in the message.
    :vartype DELIMITER: str
    :cvar END_DELIMITER: The end delimiter used in the message.
    :vartype END_DELIMITER: str
    :cvar EMPTY_MESSAGE: An empty message used as a template.
    :vartype EMPTY_MESSAGE: str

    :ivar _command: The command value.
    :type _command: int
    :ivar _payload: The message payload.
    :type _payload: str
    :ivar _data: The complete message as bytes.
    :type _data: bytes
    """


    HEADER = 'elea'
    DELIMITER = '#'
    END_DELIMITER = '#'
    EMPTY_MESSAGE = HEADER + "00" + DELIMITER + DELIMITER + DELIMITER

    def __init__(self, command:int, payload:str, data:bytes):
        """
        GrowcubeMessage constructor

        :param command: Command value.
        :type command: int
        :param payload: Message payload.
        :type payload: str
        :param data: The complete message as bytes.
        :type data: bytes
        """
        self._command = command
        self._payload = payload
        self._data = data

    @property
    def command(self):
        """
        Command value

        :return: Command value.
        :rtype: int
        """
        return self._command

    @property
    def payload(self):
        """
        Message payload

        :return: Message payload.
        :rtype: str
        """
        return self._payload

    @property
    def data(self) -> bytes:
        """
        The complete message as bytes

        :return: The complete message as bytes.
        :rtype: bytes
        """
        return self._data

    @staticmethod
    def from_bytes(data: bytearray) -> (int, Self):
        """
        Tries to construct a complete GrowcubeMessage from the data and returns
        the index of the next non-consumed data in the buffer, together with the message.
        Converts a byte array to a GrowcubeMessage instance.

        :param data: The current data buffer.
        :type data: bytearray
        :return: The index of the next non-consumed data in the buffer, together with the message,
                 or the next found start index and None if the message is incomplete.
        :rtype: tuple[int, GrowcubeMessage] or tuple[int, None]
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
        Creates a bytearray representation of a message as used in the protocol.

        :param command: Command value.
        :type command: int
        :param data: Data to send.
        :type data: str
        :return: A bytearray representation of a message as used in the protocol.
        :rtype: bytes
        """
        result = f"{GrowcubeMessage.HEADER}{command:02d}{GrowcubeMessage.DELIMITER}{len(data)}" + \
                 f"{GrowcubeMessage.DELIMITER}{data}{GrowcubeMessage.DELIMITER}"
        return result.encode("ascii")
