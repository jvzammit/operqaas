import uuid

from django_extensions.db.models import TimeStampedModel

from django.conf import settings
from django.db import models
from django.db.models import Q, UniqueConstraint

from quizzes.managers import QuizSubmissionManager

User = settings.AUTH_USER_MODEL


class Owner(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Participant(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Quiz(TimeStampedModel):
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    name = models.CharField(max_length=32)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Quizzes"

    def __str__(self):
        return self.name


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
    owner = models.ForeignKey(Owner, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    accepted_on = models.DateTimeField(blank=True, null=True)

    objects = QuizSubmissionManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["participant", "quiz"],
                name="one_submission_per_participant_per_quiz",
            )
        ]


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
