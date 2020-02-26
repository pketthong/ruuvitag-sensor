import os


def get_raw_hci(raw, data_format):
    return raw


def get_raw_bleson(raw, data_format):
    # Bleson drops FF from the raw data and it is required for DF 3 and 5
    # TODO: Move convert_data to adaptor specific code
    if data_format in (2, 4):
        return raw
    return 'FF' + raw


get_raw = get_raw_bleson if os.environ.get('RUUVI_BLE_ADAPTER') == 'Bleson' else get_raw_hci


class DataFormats(object):
    """
    RuuviTag broadcasted raw data handling for each data format
    """

    @staticmethod
    def convert_data(raw):
        """
        Validate that data is from RuuviTag and get correct data part.

        Returns:
            tuple (int, string): Data Format type and Sensor data
        """
        data = DataFormats._get_data_format_3(get_raw(raw, 3))

        if data is not None:
            return (3, data)

        data = DataFormats._get_data_format_5(get_raw(raw, 5))

        if data is not None:
            return (5, data)

        # TODO: Check from raw data correct data format
        # Now this returns 2 also for Data Format 4
        data = DataFormats._get_data_format_2and4(get_raw(raw, 2))

        if data is not None:
            return (2, data)

        return (None, None)

    @staticmethod
    def _get_data_format_2and4(raw):
        """
        Validate that data is from RuuviTag and is Data Format 2 or 4.
        Convert hexadcimal data to string.
        Encoded data part is after ruu.vi/#

        Returns:
            string: Encoded sensor data
        """
        try:
            base16_split = [raw[i:i + 2] for i in range(0, len(raw), 2)]
            selected_hexs = filter(lambda x: int(x, 16) < 128, base16_split)
            characters = [chr(int(c, 16)) for c in selected_hexs]
            data = ''.join(characters)

            # take only part after ruu.vi/#
            index = data.find('ruu.vi/#')
            if index > -1:
                return data[(index + 8):]

            return None
        except:
            return None

    @staticmethod
    def _get_data_format_3(raw):
        """
        Validate that data is from RuuviTag and is Data Format 3

        Returns:
            string: Sensor data
        """
        # Search of FF990403 (Manufacturer Specific Data (FF) /
        # Ruuvi Innovations ltd (9904) / Format 3 (03))
        try:
            if 'FF990403' not in raw:
                return None

            payload_start = raw.index('FF990403') + 6
            return raw[payload_start:]
        except:
            return None

    @staticmethod
    def _get_data_format_5(raw):
        """
        Validate that data is from RuuviTag and is Data Format 5

        Returns:
            string: Sensor data
        """
        # Search of FF990405 (Manufacturer Specific Data (FF) /
        # Ruuvi Innovations ltd (9904) / Format 5 (05))
        try:
            if 'FF990405' not in raw:
                return None

            payload_start = raw.index('FF990405') + 6
            return raw[payload_start:]
        except:
            return None
