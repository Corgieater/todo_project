from django.utils import timezone
from datetime import datetime, time


def get_day_time_range(date):
    start_of_day = timezone.make_aware(datetime.combine(date, time.min))
    end_of_day = timezone.make_aware(datetime.combine(date, time.max))
    return start_of_day, end_of_day
