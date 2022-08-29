from django.urls import path

from quizzes.views import (
    ParticipantSubmissionsDetailAPIView,
    ParticipantSubmissionsListAPIView,
    QuizDetailAPIView,
    QuizInviteAPIView,
    QuizListCreateAPIView,
    QuizQuestionAnswerCreateAPIView,
    QuizQuestionCreateAPIView,
    QuizUserAnswerCreateAPIView,
)

urlpatterns = [
    path("quizzes/", QuizListCreateAPIView.as_view(), name="quiz-list-create"),
    path("quizzes/<int:quiz_id>/", QuizDetailAPIView.as_view(), name="quiz-detail"),
    path(
        "quizzes/<int:quiz_id>/questions/",
        QuizQuestionCreateAPIView.as_view(),
        name="quiz-question-list-create",
    ),
    path(
        "quizzes/<int:quiz_id>/questions/<int:question_id>/answers",
        QuizQuestionAnswerCreateAPIView.as_view(),
        name="quiz-question-answer-list-create",
    ),
    path(
        "quizzes/<int:quiz_id>/invite/",
        QuizInviteAPIView.as_view(),
        name="quiz-submissions-list-create",
    ),
    path(
        "participant/<int:participant_id>/submissions/",
        ParticipantSubmissionsListAPIView.as_view(),
        name="participant-submission-list",
    ),
    path(
        "participant/<int:participant_id>/submissions/<int:quiz_id>/",
        ParticipantSubmissionsDetailAPIView.as_view(),
        name="participant-submission-detail",
    ),
    path(
        "participant/<int:participant_id>/submissions/<int:quiz_id>/answers/",
        QuizUserAnswerCreateAPIView.as_view(),
        name="participant-answers-list-create",
    ),
]
