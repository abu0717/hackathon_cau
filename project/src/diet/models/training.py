from sqlalchemy import UniqueConstraint, ForeignKey
from src.auth.models import AccountModel
from src.database.models import BaseModel
from src.database.types import str_32, str_256
from sqlalchemy.orm import Mapped, mapped_column, relationship
from enum import Enum


class TrainingLevels(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4


class TrainingModel(BaseModel):
    __tablename__ = 'trainings'

    name: Mapped[str_32]
    video: Mapped[str_256] = mapped_column(unique=True)
    level: Mapped[TrainingLevels]
    conducted_trainings: Mapped[list["ConductedTrainingModel"]] = relationship(back_populates="training")

    __table_args__ = (
        UniqueConstraint('name', 'level', name='uix_name_level'),
    )

    def __str__(self):
        return f"<TrainingModel(name: {self.name}, video: {self.video})>"


class ConductedTrainingModel(BaseModel):
    __tablename__ = 'conducted_trainings'

    training_id: Mapped[int] = mapped_column(ForeignKey('trainings.id', ondelete='CASCADE'))
    training: Mapped[TrainingModel] = relationship(back_populates='conducted_trainings')
    user_id: Mapped[int] = mapped_column(ForeignKey('accounts.id', ondelete='CASCADE'))
    user: Mapped["AccountModel"] = relationship(backref='conducted_trainings')

    __table_args__ = (
        UniqueConstraint('training_id', 'user_id', name='uix_training_user'),
    )

    def __str__(self):
        return f"<ConductedTrainings(training_id: {self.training_id}, user_id: {self.user})>"
