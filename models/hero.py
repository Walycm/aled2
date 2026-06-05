from sqlmodel import SQLModel, Field, Relationship

class HeroBase(SQLModel):
    name: str
    age: int | None
    secret_name : str


class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: "Team" = Relationship(back_populates="heroes")

class HeroUpdate(SQLModel):
    name: str | None = None
    age : int | None = None
    secret_name: str | None = None
