from datetime import datetime, time, timedelta

# Datetime helper functions
to_date = lambda (str): datetime.strptime(str, '%Y-%m-%d').date() if str else None
to_time = lambda (str): datetime.strptime(str, '%H:%M').time() if str else None
to_ts = lambda (str): datetime.strptime(str, '%Y-%m-%d %H:%M') if str else None

# Define bit statuses
UPHOLDER = 0x1;
QUESTIONER = 0x2;
OBLIGER = 0x4;
REBEL = 0x8;

def weekday_to_bits(int):
    """
    Converts a weekday integer to its associated bit value.

    :param int: The integer corresponding to a datetime.weekday().

    :return: A bit value.
    """
    return {
        0: 0b1,
        1: 0b10,
        2: 0b100,
        3: 0b1000,
        4: 0b10000,
        5: 0b100000,
        6: 0b1000000
    }[int]

def get_status_bits(startTS, endTS, records):
    """
    Determines whether, for a given datetime interval of startTS to endTS, a given status applies to a dataset.

    :param startTS: The start of the datetime interval (inclusive)
    :param endTS: The end of the datetime interval (exclusive)
    :param records: An array of dicts with status data

    :return: An int with zero or more bit statuses set.
    """
    result = 0

    # If there are no records, return 0
    if not records:
        return result

    # Get the list of dates in the interval
    dates = [(startTS + timedelta(days=d)).date() for d in range(0, (endTS - startTS).days + 2)]

    # Iterate over records in the dataset
    for record in records:
        # Get the status from the record
        status = record.get('status')

        # If status is missing, the record is invalid
        if not status:
            continue

        # Get the start and end dates from the record
        startDate = record.get('startDate')
        endDate = record.get('endDate')

        # Get the start and end times, defaulting to min and max, respectively
        startTime = record.get('startTime') if record.get('startTime') is not None else time.min
        endTime = record.get('endTime') if record.get('endTime') is not None else time.max

        # Assemble the start and end datetimes
        startDateTime = datetime.combine(startDate, startTime) if startDate else None
        endDateTime = datetime.combine(endDate, endTime) if endDate else None

        # Get the applicable weekdays, defaulting to all days available
        dayOfWeekBits = record.get('dayOfWeekBits') if record.get('dayOfWeekBits') is not None else 0b1111111

        # If either datetime is out of range, skip the record
        if (startDateTime and startDateTime >= endTS) or (endDateTime and endDateTime <= startTS):
            continue

        # Check each day in the interval to determine if the record is applicable
        for day in dates:
            # If this day of the week is not applicable, skip it
            if not weekday_to_bits(day.weekday()) & dayOfWeekBits:
                continue

            # Get the beginning and end of this day
            dayStart = datetime.combine(day, time.min)
            dayEnd = datetime.combine(day, time.max)

            # If the record is unbounded (missing datetimes), set datetimes based on this day
            if not startDateTime and not endDateTime:
                boundStart = datetime.combine(day, startTime)
                boundEnd = datetime.combine(day, endTime)
            # Otherwise, use the bounded datetimes
            else:
                boundStart = startDateTime or startTS
                boundEnd = endDateTime or endTS

            # If the bounds are invalid, skip it
            if boundStart > boundEnd:
                continue

            # The range starts with the start of the day or the start of the interval, whichever is later
            rangeStart = max([startTS, dayStart])

            # The range ends with the end of the day or the end of the interval, whichever is earlier
            rangeEnd = min([endTS, dayEnd])

            # If the day's bounds overlap with the range, apply the record's status to the result
            if boundEnd > rangeStart and boundStart <= rangeEnd:
                result |= status
    return result

def to_record(status=UPHOLDER, startDate=None, endDate=None, startTime=None, endTime=None, dayOfWeekBits=None):
    """
    Provides a record with status data.

    :param status: The bit status of the record; this is the only required property
    :param startDate: Starting date range of status (inclusive); when missing or None, means unbounded
    :param endDate: Ending date range of status (inclusive); when missing or None, means unbounded
    :param startTime: Starting time of status (inclusive); when missing or None, means midnight morning
    :param endTime: Ending time of status (exclusive); when missing or None, means midnight evening
    :param dayOfWeekBits: Days of the week that apply; when missing or None, means all days of the week

    :return: A dictionary.
    """
    return {
        'status': status,
        'startDate': to_date(startDate),
        'endDate': to_date(endDate),
        'startTime': to_time(startTime),
        'endTime': to_time(endTime),
        'dayOfWeekBits': dayOfWeekBits
    }

# Define a start and end timestamp with which to test
startTS = to_ts('2017-01-01 03:00')
endTS = to_ts('2017-01-03 02:00')

# Define tests
tests = [
    # Test no records
    ([], 0),

    # Test partial record
    ([{'status': OBLIGER}], OBLIGER),

    # Test out of range
    ([to_record(startDate='2017-01-04')], 0),
    ([to_record(endDate='2016-12-31')], 0),
    ([to_record(startDate='2017-01-01', endDate='2017-01-01', endTime='03:00')], 0),
    ([to_record(startDate='2017-01-03', endDate='2017-01-03', startTime='02:00')], 0),
    ([to_record(startDate='2017-01-01', endDate='2017-01-01', dayOfWeekBits=0b0111111)], 0),
    ([{'status': UPHOLDER, 'endTime': time.min}], 0),

    # Test inside range
    ([to_record()], UPHOLDER),
    ([to_record(startDate='2017-01-01', endDate='2017-01-01')], UPHOLDER),
    ([to_record(startDate='2017-01-03', endDate='2017-01-03')], UPHOLDER),
    ([to_record(startDate='2017-01-01', endDate='2017-01-01', startTime='02:30', endTime='04:00')], UPHOLDER),
    ([to_record(startDate='2017-01-01', endDate='2017-01-01', dayOfWeekBits=0b1000000)], UPHOLDER),
    ([{'status': UPHOLDER, 'startTime': time.max}], UPHOLDER),

    # Test invalid range
    ([to_record(startDate='2017-01-02', endDate='2017-01-01')], 0),
    ([to_record(startTime='2:00', endTime='1:00')], 0),
    ([to_record(dayOfWeekBits=0)], 0),

    # Test recurring times applicable only on certain days
    ([to_record(startTime='01:00', endTime='02:00', dayOfWeekBits=0b1000000)], 0),
    ([to_record(startTime='01:00', endTime='02:00', dayOfWeekBits=0b0000010)], UPHOLDER),

    # Test multiple matches
    ([to_record(status=QUESTIONER), to_record(startDate='2017-01-01', endDate='2017-01-01', startTime='02:30', endTime='04:00')], UPHOLDER | QUESTIONER),

    # Test invalid record
    ([to_record(status=None)], 0)
]

pass_count = 0

# Iterate over tests
for idx, (records, expected) in enumerate(tests):
    # Execute the function and get the result
    actual = get_status_bits(startTS, endTS, records)

    # If the result does not match the expectation, log it
    if actual != expected:
        print 'Test #%s %s failed: Expected %s, got %s' % (idx, records, expected, actual)
        print
    else:
        pass_count += 1

# Print out overall test results
print '%s/%s passed (%s%%)' % (pass_count, len(tests), int(pass_count / float(len(tests)) * 100))