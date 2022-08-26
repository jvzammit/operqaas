import uuid

from django_extensions.db.models import TimeStampedModel

from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint

from quizzes.managers import QuizSubmissionManager

User = settings.AUTH_USER_MODEL


class Quiz(TimeStampedModel):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.name

    def get_progress(self):
        return self.submission_set.objects.filter()


class QuizQuestion(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    text = models.TextField()
    position = models.PositiveSmallIntegerField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["quiz", "position"],
                name="unique_position_per_quiz",
            )
        ]
        ordering = ["position"]

    def __str__(self):
        return self.text


class QuizQuestionAnswer(TimeStampedModel):
    question = models.ForeignKey(QuizQuestion, on_delete=models.CASCADE)
    text = models.TextField()
    position = models.PositiveSmallIntegerField()
    is_correct = models.BooleanField()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["question"],
                condition=Q(is_correct=True),
                name="unique_correct_answer_per_question",
            ),
            UniqueConstraint(
                fields=["question", "position"],
                name="unique_position_per_question",
            ),
        ]
        ordering = ["position"]

    def __str__(self):
        return f"{self.text}"


class QuizSubmission(TimeStampedModel):
    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invites_sent_set"
    )
    recipient = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="invites_received_set"
    )
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name="submission_set"
    )
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    invite_accepted_on = models.DateTimeField(blank=True, null=True)

    objects = QuizSubmissionManager()


class QuizUserAnswer(TimeStampedModel):
    submission = models.ForeignKey(
        QuizSubmission, on_delete=models.CASCADE, related_name="answer_set"
    )
    answer = models.ForeignKey(QuizQuestionAnswer, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["submission", "answer"],
                name="one_answer_per_question_per_submission",
            )
        ]
