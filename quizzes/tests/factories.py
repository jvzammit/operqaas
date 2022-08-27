import factory

from django.conf import settings

from quizzes import models

User = settings.AUTH_USER_MODEL


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: "user_%d" % n)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        # Default would use default manager create function instead of create_user
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class OwnerFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Owner


class ParticipantFactory(factory.django.DjangoModelFactory):
    user = factory.SubFactory(UserFactory)

    class Meta:
        model = models.Participant


class QuizFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: "Quiz %d" % n)
    owner = factory.SubFactory(OwnerFactory)

    class Meta:
        model = models.Quiz


class QuizQuestionFactory(factory.django.DjangoModelFactory):
    position = factory.Sequence(lambda n: n)

    class Meta:
        model = models.QuizQuestion


class QuizQuestionAnswerFactory(factory.django.DjangoModelFactory):
    position = factory.Sequence(lambda n: n)

    class Meta:
        model = models.QuizQuestionAnswer


class QuizSubmissionFactory(factory.django.DjangoModelFactory):
    owner = factory.SubFactory(OwnerFactory)
    participant = factory.SubFactory(ParticipantFactory)

    class Meta:
        model = models.QuizSubmission


class QuizUserAnswerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.QuizUserAnswer
