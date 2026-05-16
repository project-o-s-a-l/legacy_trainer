from sqlalchemy.orm import Session

from backend.app.repositories.user_progress import UserProgressRepository
from backend.app.schemas.user_progress import (
    DifficultyStatsResponse,
    UserProgressResponse,
)


class UserProgressService:
    def __init__(self, db: Session) -> None:
        self.progress = UserProgressRepository(db)

    def get_progress(self, user_id: int) -> UserProgressResponse:
        rows = self.progress.get_user_progress_rows(user_id)

        completed = {
            "easy": 0,
            "medium": 0,
            "hard": 0,
        }
        score_sums = {
            "easy": 0,
            "medium": 0,
            "hard": 0,
        }
        score_counts = {
            "easy": 0,
            "medium": 0,
            "hard": 0,
        }

        for row in rows:
            difficulty = row.task.difficulty.value

            if row.is_solved:
                completed[difficulty] += 1

            if row.best_submission.score is not None:
                score_sums[difficulty] += row.best_submission.score
                score_counts[difficulty] += 1

        average_grade = {
            "easy": self._calculate_average(score_sums["easy"], score_counts["easy"]),
            "medium": self._calculate_average(
                score_sums["medium"],
                score_counts["medium"],
            ),
            "hard": self._calculate_average(score_sums["hard"], score_counts["hard"]),
        }

        return UserProgressResponse(
            tasksCompleted=DifficultyStatsResponse(**completed),
            averageGrade=DifficultyStatsResponse(**average_grade),
        )

    def _calculate_average(self, total: int, count: int) -> int:
        if count == 0:
            return 0
        return round(total / count)
