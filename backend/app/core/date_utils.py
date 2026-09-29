from datetime import date, timedelta


def get_current_and_previous_month_periods():
    """
    Return the current month-to-date and previous month
    date ranges in AWS Cost Explorer format.

    Returns:
        dict containing:
        - current_start
        - current_end
        - previous_start
        - previous_end
    """

    today = date.today()

    current_start = today.replace(day=1)

    current_end = today

    previous_month_end = current_start - timedelta(days=1)
    previous_start = previous_month_end.replace(day=1)

    return {
        "current_start": current_start.isoformat(),
        "current_end": current_end.isoformat(),
        "previous_start": previous_start.isoformat(),
        "previous_end": previous_month_end.isoformat(),
    }