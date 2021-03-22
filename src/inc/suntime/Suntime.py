import math
try:
 from utime import localtime
except:
 from inc.faketime import localtime


class SunTimeException(Exception):

    def __init__(self, message):
        super(SunTimeException, self).__init__(message)


class Sun:
    """
    Original: https://github.com/SatAgro/suntime/blob/master/suntime/suntime.py

    Ported to Micropython 20.02.2021: Divergentti / Jari Hiltunen
    Replaced: date utils. Method call use hour difference to UTC as timezone! This will be added to return.
    """

    def __init__(self, lat, lon, tzone):
        self._lat = lat
        self._lon = lon
        self._tzone = tzone

    def get_sunrise_time(self, date=None):
        """
        Calculate the sunrise time for given date.
        :param date: Reference date. Today if not provided.
        :return: UTC sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """

        date = localtime() if date is None else date
        sr = self._calc_sun_time(date, True)
        if sr is None:
            raise SunTimeException('The sun never rises on this location (on the specified date)')
        else:
            return sr

    def get_sunset_time(self, date=None):
        """
        Calculate the sunset time for given date.
        :param date: Reference date. Today if not provided.
        :return: UTC sunset datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date.
        """
        date = localtime() if date is None else date
        ss = self._calc_sun_time(date, False)
        if ss is None:
            raise SunTimeException('The sun never sets on this location (on the specified date)')
        else:
            return ss

    def _calc_sun_time(self, date, isrisetime=True, zenith=90.8):
        """
        Calculate sunrise or sunset date.
        :param date: Reference date (localtime())
        :param isRiseTime: True if you want to calculate sunrise time.
        :param zenith: Sun reference zenith
        :return: UTC sunset or sunrise datetime
        :raises: SunTimeException when there is no sunrise and sunset on given location and date
        """
        # isRiseTime == False, returns sunsetTime
        day = date[2]
        month = date[1]
        year = date[0]
        to_rad = math.pi / 180.0

        # 1. first calculate the day of the year
        n1 = math.floor(275 * month / 9)
        n2 = math.floor((month + 9) / 12)
        n3 = (1 + math.floor((year - 4 * math.floor(year / 4) + 2) / 3))
        n = n1 - (n2 * n3) + day - 30

        # 2. convert the longitude to hour value and calculate an approximate time
        lnghour = self._lon / 15

        if isrisetime:
            t = n + ((6 - lnghour) / 24)
        else:  # sunset
            t = n + ((18 - lnghour) / 24)

        # 3. calculate the Sun's mean anomaly
        m = (0.9856 * t) - 3.289

        # 4. calculate the Sun's true longitude
        ll = m + (1.916 * math.sin(to_rad * m)) + (0.020 * math.sin(to_rad * 2 * m)) + 282.634
        ll = self._force_range(ll, 360)  # NOTE: L adjusted into the range [0,360)

        # 5a. calculate the Sun's right ascension

        ra = (1 / to_rad) * math.atan(0.91764 * math.tan(to_rad * ll))
        ra = self._force_range(ra, 360)  # NOTE: RA adjusted into the range [0,360)

        # 5b. right ascension value needs to be in the same quadrant as L
        lquadrant = (math.floor(ll / 90)) * 90
        raquadrant = (math.floor(ra / 90)) * 90
        ra = ra + (lquadrant - raquadrant)

        # 5c. right ascension value needs to be converted into hours
        ra = ra / 15

        # 6. calculate the Sun's declination
        sindec = 0.39782 * math.sin(to_rad * ll)
        cosdec = math.cos(math.asin(sindec))

        # 7a. calculate the Sun's local hour angle
        cosh = (math.cos(to_rad * zenith) - (sindec * math.sin(to_rad * self._lat))) / (
                    cosdec * math.cos(to_rad * self._lat))

        if cosh > 1:
            return None  # The sun never rises on this location (on the specified date)
        if cosh < -1:
            return None  # The sun never sets on this location (on the specified date)

        # 7b. finish calculating H and convert into hours

        if isrisetime:
            h = 360 - (1 / to_rad) * math.acos(cosh)
        else:  # setting
            h = (1 / to_rad) * math.acos(cosh)

        h = h / 15

        # 8. calculate local mean time of rising/setting
        t = h + ra - (0.06571 * t) - 6.622

        # 9. adjust back to UTC
        ut = t - lnghour
        ut = self._force_range(ut, 24)  # UTC time in decimal format (e.g. 23.23)

        # 10. Return
        hr = self._force_range(int(ut), 24)
        minutes = round((ut - int(ut)) * 60, 0)
        if minutes == 60:
            hr += 1
            minutes = 0
        return year, month, day, hr + self._tzone, int(minutes)

    @staticmethod
    def _force_range(v, maximum):
        # force v to be >= 0 and < max
        if v < 0:
            return v + maximum
        elif v >= maximum:
            return v - maximum
        return v
