from sqlalchemy import Column, Integer, ForeignKey, DateTime, Float, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Bid(Base):
    __tablename__ = "bids"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float(precision=2))
    user_id = Column(Integer, ForeignKey("users.id"))
    plate_id = Column(Integer, ForeignKey("auto_plates.id"))
    created_at = Column(DateTime, default=datetime.now)

    user = relationship("User", back_populates="bids")
    plate = relationship("AutoPlate", back_populates="bids")

    __table_args__ = (UniqueConstraint("user_id", "plate_id", name="uq_user_plate"),)

    def __repr__(self):
        return f"<Bid {self.id}>"

    def __str__(self):
        return f"Bid {self.id}"

    def __eq__(self, other):
        if not isinstance(other, Bid):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __bool__(self):
        return True

    def to_dict(self):
        return {
            "id": self.id,
            "amount": self.amount,
            "user": self.user.username,
            "plate": self.plate.plate_number,
            "created_at": self.created_at,
        }
