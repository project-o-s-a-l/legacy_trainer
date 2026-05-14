from pydantic import BaseModel


class DifficultyStatsResponse(BaseModel):
    easy: int
    medium: int
    hard: int


class UserProgressResponse(BaseModel):
    tasksCompleted: DifficultyStatsResponse
    averageGrade: DifficultyStatsResponse
