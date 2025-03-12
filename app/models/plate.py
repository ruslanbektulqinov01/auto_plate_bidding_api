from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class AutoPlate(Base):
    __tablename__ = "auto_plates"

    id = Column(Integer, primary_key=True, index=True)
    plate_number = Column(String(10), unique=True, index=True)
    description = Column(Text)
    deadline = Column(DateTime)
    created_by_id = Column(Integer, ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    created_by = relationship("User", back_populates="plates_created")
    bids = relationship("Bid", back_populates="plate", cascade="all, delete")

    def __repr__(self):
        return f"<AutoPlate {self.plate_number}>"

    def __str__(self):
        return self.plate_number

    def get_highest_bid(self):
        if not self.bids:
            return None
        return max(self.bids, key=lambda bid: bid.amount)

    def is_bidding_active(self):
        return self.is_active and self.deadline > datetime.now()
