from django.test import TestCase

from quizzes.models import QuizSubmission
from quizzes.tests.factories import (
    QuizFactory,
    QuizQuestionAnswerFactory,
    QuizQuestionFactory,
    QuizSubmissionFactory,
    QuizUserAnswerFactory,
)


class QuizSubmissionManagerTest(TestCase):
    def test_get_queryset(self):
        quiz1 = QuizFactory(name="Geography")
        q1 = QuizQuestionFactory(quiz=quiz1, text="CH capital city?")
        _ = QuizQuestionAnswerFactory(question=q1, text="Zurich", is_correct=False)
        _ = QuizQuestionAnswerFactory(question=q1, text="Geneva", is_correct=False)
        q1a3 = QuizQuestionAnswerFactory(question=q1, text="Bern", is_correct=True)
        _ = QuizQuestionAnswerFactory(question=q1, text="Lugano", is_correct=False)
        q2 = QuizQuestionFactory(quiz=quiz1, text="Capital of canton Ticino?")
        _ = QuizQuestionAnswerFactory(question=q2, text="Lugano", is_correct=False)
        q2a2 = QuizQuestionAnswerFactory(
            question=q2, text="Bellinzona", is_correct=True
        )
        q2a3 = QuizQuestionAnswerFactory(question=q2, text="Como", is_correct=False)
        _ = QuizQuestionAnswerFactory(question=q2, text="Milan", is_correct=False)
        q3 = QuizQuestionFactory(quiz=quiz1, text="Main language of canton Vaud?")
        _ = QuizQuestionAnswerFactory(question=q3, text="EN", is_correct=False)
        _ = QuizQuestionAnswerFactory(question=q3, text="IT", is_correct=False)
        _ = QuizQuestionAnswerFactory(question=q3, text="DE", is_correct=False)
        q3a4 = QuizQuestionAnswerFactory(question=q3, text="FR", is_correct=True)

        quiz1sub1 = QuizSubmissionFactory(quiz=quiz1)
        QuizUserAnswerFactory(submission=quiz1sub1, answer=q1a3)
        QuizUserAnswerFactory(submission=quiz1sub1, answer=q2a3)
        QuizUserAnswerFactory(submission=quiz1sub1, answer=q3a4)

        quiz1sub1 = QuizSubmission.objects.get(id=quiz1sub1.id)  # from queryset
        self.assertEqual(quiz1sub1.answers_all_count, 3)
        self.assertEqual(quiz1sub1.answers_correct_count, 2)

        quiz1sub2 = QuizSubmissionFactory(quiz=quiz1)
        quiz1sub2 = QuizSubmission.objects.get(id=quiz1sub2.id)  # from queryset
        self.assertEqual(quiz1sub2.answers_all_count, 0)
        self.assertEqual(quiz1sub2.answers_correct_count, 0)

        quiz1sub3 = QuizSubmissionFactory(quiz=quiz1)
        QuizUserAnswerFactory(submission=quiz1sub3, answer=q1a3)
        QuizUserAnswerFactory(submission=quiz1sub3, answer=q2a2)
        QuizUserAnswerFactory(submission=quiz1sub3, answer=q3a4)

        quiz1sub3 = QuizSubmission.objects.get(id=quiz1sub3.id)  # from queryset
        self.assertEqual(quiz1sub3.answers_all_count, 3)
        self.assertEqual(quiz1sub3.answers_correct_count, 3)
