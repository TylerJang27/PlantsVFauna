from sqlalchemy import Column, Integer, DateTime, Sequence, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base
from sqlalchemy import func


class Report(Base):
    __tablename__ = 'report'

    report_id_seq = Sequence('report_id_seq')
    uid = Column(Integer, report_id_seq, server_default=report_id_seq.next_value(), primary_key=True)
    device_id = Column(ForeignKey('device.device_id'), nullable=False)
    status = Column(String(50), nullable=True)
    description = Column(String(255), nullable=False)
    battery = Column(Integer, nullable=True)
    time = Column(DateTime(timezone=True), server_default=func.now())

    device = relationship("Device", back_populates="reports")


    def __init__(self, device_id, status, description, battery):
        self.device_id = device_id
        self.status = status
        self.description = description
        self.battery = battery

    def __repr__(self):
        return "<Report(report_id='%d', device_id='%d', report_status='%s', report_battery='%d')>" % (
                             self.uid, self.device_id, "N/A" if self.status is None else self.status, "N/A" if self.battery is None else self.battery)
