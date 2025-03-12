from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_staff = Column(Boolean, default=False)

    plates_created = relationship("AutoPlate", back_populates="created_by")
    bids = relationship("Bid", back_populates="user", cascade="all, delete")

    def __repr__(self):
        return f"<User {self.username}>"

    def __str__(self):
        return self.username

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

    def __bool__(self):
        return True

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "is_staff": self.is_staff,
        }

    def get_active_bids(self):
        return [bid for bid in self.bids if bid.plate.is_bidding_active()]
