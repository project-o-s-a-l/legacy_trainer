from sqlalchemy.orm import Session
from backend.app.db.enums import SubmissionStatus
from backend.app.models.submission import Submission
from backend.app.models.task import Task
from backend.app.repositories.user_progress import UserProgressRepository
from backend.app.schemas.user_progress import (
    DifficultyStatsResponse,
    UserProgressResponse,
)


class UserProgressService:
    def __init__(self, db: Session) -> None:
        self.progress = UserProgressRepository(db)

    def record_submission(
        self,
        *,
        user_id: int,
        task: Task,
        submission: Submission,
    ) -> None:
        is_solved = self._is_solved(task=task, submission=submission)
        progress = self.progress.get_user_task_progress(
            user_id=user_id,
            task_id=task.id,
        )

        if progress is None:
            self.progress.create_user_task_progress(
                user_id=user_id,
                task_id=task.id,
                best_submission_id=submission.id,
                submitted_at=submission.submitted_at,
                is_solved=is_solved,
            )
        else:
            progress.attempts_count += 1
            progress.last_submission_at = submission.submitted_at
            if self._is_better_submission(submission, progress.best_submission):
                progress.best_submission_id = submission.id
                progress.best_submission = submission
            if is_solved:
                progress.is_solved = True
            self.progress.flush()

        self.progress.recalculate_user_total_score(user_id)

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

            if (
                row.best_submission is not None
                and row.best_submission.score is not None
            ):
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

    def _is_solved(self, *, task: Task, submission: Submission) -> bool:
        threshold = task.max_score if 0 < task.max_score <= 100 else 100
        return self._score(submission) >= threshold

    def _score(self, submission: Submission | None) -> int:
        if submission is None:
            return 0
        return submission.score or 0

    def _is_better_submission(
        self,
        candidate: Submission,
        current: Submission | None,
    ) -> bool:
        if current is None:
            return True

        candidate_score = self._score(candidate)
        current_score = self._score(current)
        if candidate_score != current_score:
            return candidate_score > current_score

        return self._status_rank(candidate.status) > self._status_rank(current.status)

    def _status_rank(self, status: SubmissionStatus) -> int:
        if status == SubmissionStatus.PASSED:
            return 3
        if status == SubmissionStatus.FAILED:
            return 2
        if status == SubmissionStatus.ERROR:
            return 1
        return 0
