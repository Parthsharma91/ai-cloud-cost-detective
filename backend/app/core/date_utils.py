from datetime import date, timedelta


def get_current_and_previous_month_periods():
    """
    Return the current month-to-date and previous month
    date ranges in AWS Cost Explorer format.

    AWS Cost Explorer treats the End date as exclusive.

    Returns:
        dict containing:
        - current_start
        - current_end
        - previous_start
        - previous_end
    """

    today = date.today()

    current_start = today.replace(day=1)

    # AWS Cost Explorer End date is exclusive.
    # Use tomorrow so today's costs are included.
    current_end = today + timedelta(days=1)

    previous_month_end = current_start - timedelta(days=1)
    previous_start = previous_month_end.replace(day=1)

    # Previous month End is also exclusive.
    previous_end = current_start

    return {
        "current_start": current_start.isoformat(),
        "current_end": current_end.isoformat(),
        "previous_start": previous_start.isoformat(),
        "previous_end": previous_end.isoformat(),
    }