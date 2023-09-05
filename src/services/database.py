from database_exception import DatabaseExceptions
from dotenv import load_dotenv
from envs import env
from modules.report.report_dto import STATUS
from services.models import Process, Status
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

load_dotenv()

SQLALCHEMY_DATABASE_URL = env("DATABASE_URL", var_type="string", allow_none=False)

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Database:
    def __init__(self) -> None:
        self.db = SessionLocal()

    def create_process(self, payload, configuration_version):
        try:

            process_status_id = (
                select(Status.id)
                .where(Status.value == STATUS.IN_PROGRESS.value)
                .scalar_subquery()
            )
            process = Process(
                configurationId=payload.configurationId,
                params=payload.params,
                status=process_status_id,
                configurationVersion=configuration_version,
            )
            self.db.add(process)
            self.db.commit()
            self.db.refresh(process)
            self.db.close()
            subquery = select(Status.value).where(Status.id == process.status)
            process_status = self.db.execute(subquery).scalar()
            process.status = process_status
            return process
        except:
            raise DatabaseExceptions(
                {
                    "status_code": 400,
                    "detail": f"Failed to create a process {payload.configurationId}",
                }
            )

    def update_process(self, uuid, process_time, status, data):
        try:
            record = self.db.query(Process).filter_by(uuid=uuid).first()
            record.processTime = process_time * 1000

            process_status_id = (
                select(Status.id).where(Status.value == status).scalar_subquery()
            )

            record.status = process_status_id
            if status == STATUS.COMPLETE.value:
                record.data = data
            elif status == STATUS.FAILED.value:
                record.error = data

            self.db.commit()
            self.db.close()
        except:
            raise DatabaseExceptions(
                {
                    "status_code": 404,
                    "detail": f"Process not found, processId {uuid}, failed to update the process",
                }
            )

    def get_process(self, uuid, cid):
        try:
            record = self.db.query(Process).filter_by(uuid=uuid).first()
            subquery = select(Status.value).where(Status.id == record.status)
            process_status = self.db.execute(subquery).scalar()
            result = {
                "cid": cid,
                "uuid": record.uuid,
                "status": process_status,
                "configurationId": record.configurationId,
                "params": record.params,
                "data": record.data,
                "error": record.error,
                "createdAt": record.createdAt,
                "createdBy": record.createdBy,
                "updatedAt": record.updatedAt,
                "updatedBy": record.updatedBy,
            }

            return result

        except:
            raise DatabaseExceptions(
                {
                    "status_code": 404,
                    "detail": f"Process not found, processId {uuid}",
                }
            )
