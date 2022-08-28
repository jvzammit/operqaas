from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from django.contrib.auth.models import User

from quizzes.models import Quiz, QuizQuestion, QuizSubmission, QuizUserAnswer
from quizzes.tests.factories import OwnerFactory, QuizFactory, QuizSubmissionFactory


@mock.patch("quizzes.views.send_mail")
class IntegrationTest(APITestCase):
    def test_flow(self, p_send_mail):
        superuser1 = User.objects.create_superuser(username="su")
        user1 = User.objects.create_user(username="owner1", email="owner1@quiz.com")
        owner1 = OwnerFactory(user=user1)
        user2 = User.objects.create_user(username="owner2", email="owner2@quiz.com")
        owner2 = OwnerFactory(user=user2)
        quiz2 = QuizFactory(name="Quiz 2", owner=owner2)

        # ===============================
        # login as owner
        self.client.force_login(user=user1)

        # no quizzes
        url = "/api/quizzes/"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 0)

        # create quiz
        data = {"name": "Test Quizzz"}
        response = self.client.post("/api/quizzes/", data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        quiz1 = Quiz.objects.get(id=response.data["id"])
        self.assertEqual(quiz1.owner.id, owner1.id)

        # add question 1
        data = {"text": "CH capital city?", "position": 1}
        url = f"/api/quizzes/{quiz1.id}/questions/"
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        question1 = QuizQuestion.objects.get(id=response.data["id"])
        self.assertEqual(question1.quiz.id, quiz1.id)

        # add question 2
        data = {"text": "Capital of canton Ticino?", "position": 2}
        url = f"/api/quizzes/{quiz1.id}/questions/"
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        question2 = QuizQuestion.objects.get(id=response.data["id"])
        self.assertEqual(question2.quiz.id, quiz1.id)

        # add question1 answers 1 & 2
        url = f"/api/quizzes/{quiz1.id}/questions/{question1.id}/answers"
        data = {"text": "Zurich", "position": 1, "is_correct": False}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question"], question1.id)
        q1a1_id = response.data["id"]
        data = {"text": "Bern", "position": 2, "is_correct": True}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question"], question1.id)
        q1a2_id = response.data["id"]

        # add question2 answers 1 & 2
        url = f"/api/quizzes/{quiz1.id}/questions/{question2.id}/answers"
        data = {"text": "Bellinzona", "position": 1, "is_correct": True}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question"], question2.id)
        q2a1_id = response.data["id"]
        data = {"text": "Lugano", "position": 2, "is_correct": False}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["question"], question2.id)
        q2a2_id = response.data["id"]  # noqa

        # retrieve quiz details for quiz owner
        url = f"/api/quizzes/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["questions"]), 2)
        self.assertEqual(len(response.data["questions"][0]["answers"]), 2)
        self.assertEqual(response.data["questions"][0]["answers"][0]["position"], 1)
        self.assertEqual(response.data["questions"][0]["answers"][1]["position"], 2)
        self.assertFalse(response.data["questions"][0]["answers"][0]["is_correct"])
        self.assertTrue(response.data["questions"][0]["answers"][1]["is_correct"])

        # try to update quiz as participant
        url = f"/api/quizzes/{quiz1.id}/"
        response = self.client.put(url, data={"name": "Test Quiz"}, json=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # try to retreive quiz details for quiz by another owner
        url = f"/api/quizzes/{quiz2.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # invite participant john.doe@test.com to quiz
        url = f"/api/quizzes/{quiz1.id}/invite/"
        data = {"first_name": "John", "last_name": "Doe", "email": "john.doe@test.com"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission1 = QuizSubmission.objects.get(id=response.data["submission_id"])
        self.assertEqual(submission1.participant.user.email, "john.doe@test.com")
        john_doe = submission1.participant

        # invite participant jane.doe@test.com to quiz
        url = f"/api/quizzes/{quiz1.id}/invite/"
        data = {"first_name": "Jane", "last_name": "Doe", "email": "jane.doe@test.com"}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        submission2 = QuizSubmission.objects.get(id=response.data["submission_id"])
        self.assertEqual(submission2.participant.user.email, "jane.doe@test.com")
        jane_doe = submission2.participant

        expected_calls = [
            mock.call(
                subject="Quiz Invite!",
                message="You've been invited to Test Quiz.",
                from_email="owner1@quiz.com",
                recipient_list=["john.doe@test.com"],
            ),
            mock.call(
                subject="Quiz Invite!",
                message="You've been invited to Test Quiz.",
                from_email="owner1@quiz.com",
                recipient_list=["jane.doe@test.com"],
            ),
        ]
        p_send_mail.assert_has_calls(expected_calls)

        # ===============================
        # sign in as participant john doe
        self.client.force_login(user=john_doe.user)

        # john.doe submit answer to quiz question 1
        url = f"/api/participant/{john_doe.id}/submissions/{quiz1.id}/answers/"
        data = {"question": question1.id, "answer": q1a1_id}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_answer1 = QuizUserAnswer.objects.get(id=response.data["id"])
        self.assertEqual(user_answer1.answer.question, question1)

        # check score for john.doe quiz
        url = f"/api/participant/{john_doe.id}/submissions/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], "0 / 1")
        self.assertEqual(response.data["progress"], "1 / 2")

        # john.doe submit answer to quiz question 2
        url = f"/api/participant/{john_doe.id}/submissions/{quiz1.id}/answers/"
        data = {"question": question2.id, "answer": q2a1_id}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_answer1 = QuizUserAnswer.objects.get(id=response.data["id"])
        self.assertEqual(user_answer1.answer.question, question2)

        # check score for john.doe quiz
        url = f"/api/participant/{john_doe.id}/submissions/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], "1 / 2")
        self.assertEqual(response.data["progress"], "2 / 2")

        # retrieve quiz details for quiz participant
        url = f"/api/quizzes/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["questions"]), 2)
        self.assertEqual(len(response.data["questions"][0]["answers"]), 2)
        self.assertEqual(response.data["questions"][0]["answers"][0]["position"], 1)
        self.assertEqual(response.data["questions"][0]["answers"][1]["position"], 2)
        self.assertNotIn("is_correct", response.data["questions"][0]["answers"][0])

        # try to retreive quiz details for quiz that john.doe was not invited to
        url = f"/api/quizzes/{quiz2.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # try to update quiz as participant
        url = f"/api/quizzes/{quiz1.id}/"
        response = self.client.patch(url, {"name": "lolz"})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # try to update quiz details for quiz that john.doe was not invited to
        url = f"/api/quizzes/{quiz2.id}/"
        response = self.client.patch(url, {"name": "lolz"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # ===============================
        # sign in as participant jane doe
        self.client.force_login(user=jane_doe.user)

        # jane.doe submit answer to quiz question 1
        url = f"/api/participant/{jane_doe.id}/submissions/{quiz1.id}/answers/"
        data = {"question": question1.id, "answer": q1a2_id}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_answer1 = QuizUserAnswer.objects.get(id=response.data["id"])
        self.assertEqual(user_answer1.answer.question, question1)

        # check score for jane.doe quiz
        url = f"/api/participant/{jane_doe.id}/submissions/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], "1 / 1")
        self.assertEqual(response.data["progress"], "1 / 2")

        # jane.doe submit answer to quiz question 2
        url = f"/api/participant/{jane_doe.id}/submissions/{quiz1.id}/answers/"
        data = {"question": question2.id, "answer": q2a1_id}
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user_answer1 = QuizUserAnswer.objects.get(id=response.data["id"])
        self.assertEqual(user_answer1.answer.question, question2)

        # check score for jane.doe quiz
        url = f"/api/participant/{jane_doe.id}/submissions/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["score"], "2 / 2")
        self.assertEqual(response.data["progress"], "2 / 2")
        self.assertEqual(len(response.data["answers"]), 2)

        # check that jane doe sees only her submissions
        url = f"/api/participant/{jane_doe.id}/submissions/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["id"], submission2.id)

        # Add submission for another quiz
        submission3 = QuizSubmissionFactory(
            quiz=quiz2, owner=owner2, participant=jane_doe
        )
        url = f"/api/participant/{jane_doe.id}/submissions/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)  # 2 submissions
        self.assertEqual(
            [sub["id"] for sub in response.data], [submission2.id, submission3.id]
        )

        # test filtering by quiz name
        url = f"/api/participant/{jane_doe.id}/submissions/?quiz_name=quiz+2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 submission
        self.assertEqual(response.data[0]["id"], submission3.id)

        # test filtering by quiz owner email
        url = f"/api/participant/{jane_doe.id}/submissions/?owner_email=owner1@quiz.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 submission
        self.assertEqual(response.data[0]["id"], submission2.id)
        url = f"/api/participant/{jane_doe.id}/submissions/?owner_email=owner2@quiz.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 submission
        self.assertEqual(response.data[0]["id"], submission3.id)

        # test search by quiz name and quiz owner email
        url = f"/api/participant/{jane_doe.id}/submissions/?search=quiz+2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 submission
        self.assertEqual(response.data[0]["id"], submission3.id)
        url = f"/api/participant/{jane_doe.id}/submissions/?search=owner2@quiz.com"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)  # 1 submission
        self.assertEqual(response.data[0]["id"], submission3.id)

        # ===============================
        # re-login as owner
        self.client.force_login(user=owner1.user)

        # fetch details about submissions for quiz
        url = "/api/quizzes/"
        response = self.client.get(url)
        self.assertEqual(len(response.data), 1)  # assert only one quiz returned
        quiz_data = response.data[0]
        self.assertEqual(
            [sub["id"] for sub in quiz_data["submissions"]],
            [submission1.id, submission2.id],
        )
        self.assertEqual(quiz_data["submissions"][0]["score"], "1 / 2")
        self.assertEqual(quiz_data["submissions"][0]["progress"], "2 / 2")
        self.assertEqual(quiz_data["submissions"][1]["score"], "2 / 2")
        self.assertEqual(quiz_data["submissions"][0]["progress"], "2 / 2")

        # add another quiz by "owner"
        QuizFactory(owner=owner1, name="Another Quiz")
        response = self.client.get(url)
        self.assertEqual(len(response.data), 2)  # only two quizzes returned

        # add another quiz by another owner
        another_owner = OwnerFactory()
        QuizFactory(owner=another_owner, name="Quiz by another owner")
        response = self.client.get(url)
        self.assertEqual(
            len(response.data), 2
        )  # still two quizzes returned for "owner"

        # filter quiz by name
        response = self.client.get(url + "?name=Test+Quiz")  # case sensitive
        self.assertEqual(len(response.data), 1)
        response = self.client.get(url + "?name=test+QUIZ")  # case insensitive
        self.assertEqual(len(response.data), 1)

        # seach quiz by name
        response = self.client.get(url + "?search=quiz")
        self.assertEqual(len(response.data), 2)  # both quizzes match "name"
        response = self.client.get(url + "?search=another")
        self.assertEqual(len(response.data), 1)  # one quiz matches "another"
        response = self.client.get(url + "?search=foobar")
        self.assertEqual(len(response.data), 0)  # no quiz matches "foobar"

        # login as superuser
        self.client.force_login(superuser1)
        url = "/api/quizzes/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 4)  # see all quizzes created!

        url = f"/api/quizzes/{quiz1.id}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
