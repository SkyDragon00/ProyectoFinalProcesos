# reminder_scheduler.py
import datetime
from apscheduler.schedulers.blocking import BlockingScheduler
from sqlmodel import Session, select
from app.db.database import get_engine, Event, Registration, User, EventDate
from app.helpers.mail import send_event_reminder_email

def send_reminders():
    engine = get_engine()
    tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).date()
    with Session(engine) as session:
        # Get event dates for tomorrow instead of events with a date field
        event_dates = session.exec(
            select(EventDate).where(EventDate.day_date == tomorrow)
        ).all()
        
        # Group event dates by event
        events_dates_map = {}
        for event_date in event_dates:
            if event_date.event_id not in events_dates_map:
                events_dates_map[event_date.event_id] = []
            events_dates_map[event_date.event_id].append(event_date)
        
        for event_id, dates in events_dates_map.items():
            event = session.get(Event, event_id)
            if event and not event.is_cancelled:
                registrations = session.exec(
                    select(Registration).where(Registration.event_id == event.id)
                ).all()
                for reg in registrations:
                    user = session.get(User, reg.assistant_id)
                    if user:
                        try:
                            send_event_reminder_email(user, event, dates)
                        except Exception as e:
                            # Log the error but continue processing other reminders
                            print(f"Failed to send reminder email to {user.email}: {e}")
                            continue

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    scheduler.add_job(send_reminders, 'cron', hour=8)  # Every day at 8am
    scheduler.start()