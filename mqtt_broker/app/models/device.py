from sqlalchemy import Column, Boolean, Integer, Sequence, String, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import Base


class Device(Base):
    __tablename__ = 'device'

    device_id = Column(Integer(), primary_key=True)
    manual_on = Column(Boolean(), nullable=False)  # includes out of power
    remote_on = Column(Boolean(), nullable=False)
    battery = Column(Integer(), nullable=False, default=100)

    count_thresh = Column(Integer(), nullable=False, default=8)
    min_thresh = Column(Integer(), nullable=False, default=19)
    max_thresh = Column(Integer(), nullable=False, default=35)
    color_thresh = Column(Integer(), nullable=False, default=90)

    reports = relationship("Report", back_populates="device")

    def __repr__(self):
        return "<Device(device_id='%d')>" % (self.device_id)