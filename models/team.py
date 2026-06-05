from sqlmodel import SQLModel, Field, Relationship

class TeamBase(SQLModel):
    name: str
    headquarters : str

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")

class TeamUpdate(SQLModel):
    name: str | None
    headquarters : str | None
    