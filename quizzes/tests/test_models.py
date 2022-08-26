from django.test import TestCase

from quizzes.tests.factories import (
    QuizFactory,
    QuizQuestionAnswerFactory,
    QuizQuestionFactory,
)


class QuizTest(TestCase):
    def test_str(self):
        quiz = QuizFactory(name="Test")
        self.assertEqual(str(quiz), "Test")


class QuizQuestionTest(TestCase):
    def test_str(self):
        quiz = QuizFactory()
        quiz_question = QuizQuestionFactory(quiz=quiz, text="Test")
        self.assertEqual(str(quiz_question), "Test")


class QuizQuestionAnswerTest(TestCase):
    def test_str(self):
        quiz = QuizFactory()
        quiz_question = QuizQuestionFactory(quiz=quiz)
        quiz_question_answer = QuizQuestionAnswerFactory(
            question=quiz_question, text="Test", is_correct=False
        )
        self.assertEqual(str(quiz_question_answer), "Test")
