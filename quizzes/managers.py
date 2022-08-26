from django.db import models
from django.db.models import Count, Q


class QuizSubmissionManager(models.Manager):
    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .annotate(
                answers_all_count=Count("answer_set"),
                answers_correct_count=Count(
                    "answer_set",
                    filter=Q(answer_set__answer__is_correct=True),
                    distinct=True,
                ),
            )
        )
