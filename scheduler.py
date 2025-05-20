from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from datetime import datetime, timedelta
import json
import uuid
import logging

# --- Constants --- #
EVENTS_FILE = 'events.json'


# --- Utility Functions --- #
def load_events():
    """Load events from the events file."""
    try:
        with open(EVENTS_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def reminder_callback(event_id, when):
    """Callback function to execute when a reminder is triggered."""
    events = load_events()
    event = events.get(event_id)
    if not event:
        return
    # Here you could send an email, push notification, etc.
    # For demo we'll just print.
    print(f"[REMINDER] {when} reminder for event '{event['name']}' on {event['date']}")


# --- Scheduler Functions --- #
def schedule_reminders(scheduler, event_id, event_date_str):
    """Schedule reminders for an event."""
    # Parse the event date
    event_date = datetime.fromisoformat(event_date_str)

    # 24-hour-before reminder
    reminder_1 = event_date - timedelta(days=1)
    if reminder_1 > datetime.now():
        scheduler.add_job(
            reminder_callback,
            trigger=DateTrigger(run_date=reminder_1),
            args=[event_id, "24-hour"],
            id=f"{event_id}_reminder1"
        )

    # 1-hour-before reminder
    reminder_2 = event_date - timedelta(hours=1)
    if reminder_2 > datetime.now():
        scheduler.add_job(
            reminder_callback,
            trigger=DateTrigger(run_date=reminder_2),
            args=[event_id, "1-hour"],
            id=f"{event_id}_reminder2"
        )


def init_scheduler():
    """Initialize the background scheduler and reschedule existing reminders."""
    scheduler = BackgroundScheduler()
    scheduler.start()

    # On startup, reschedule reminders for all future events
    events = load_events()
    for event_id, ev in events.items():
        schedule_reminders(scheduler, event_id, ev['date'])

    return scheduler


# --- Event Handling --- #
# expose a function to call when you create a new event
scheduler = init_scheduler()


def on_event_created(event_id, date):
    """Handle scheduling of event reminders."""
    try:
        logging.info(f"Scheduling reminder for event {event_id} on {date}")
        schedule_reminders(scheduler, event_id, date)
        return True
    except Exception as e:
        logging.error(f"Failed to schedule reminder: {str(e)}")
        return False
