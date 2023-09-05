from services.database import SessionLocal
from services.models import Process, Status


def seed_analytics_db():

    db = SessionLocal()
    existing_processes = db.query(Process).all()
    if not existing_processes:
        process_data = {
            "configurationId": "9987ea1f-ff53-48f5-8a7f-af8f1d4bf768",
            "params": "{}",
        }
        print("seeding process")
        db_process = Process(**process_data)
        db.merge(db_process)
        db.commit()

    existing_status = db.query(Status).all()
    if not existing_status:
        status_data = [
            {"value": "PENDING", "description": "Waiting for process to start"},
            {"value": "IN_PROGRESS", "description": "Process is in progress"},
            {"value": "COMPLETE", "description": "Process is complete"},
            {"value": "FAILED", "description": "Process failed"},
        ]

        print("seeding status")
        for s in status_data:
            db_status = Status(**s)
            db.merge(db_status)
        db.commit()


seed_analytics_db()
