from rest_framework import serializers

from django.contrib.auth.models import User

from quizzes import models


class QuizSerializer(serializers.ModelSerializer):
    submissions = serializers.SerializerMethodField()  # aka invites
    questions = serializers.SerializerMethodField()

    class Meta:
        model = models.Quiz
        fields = "__all__"
        read_only_fields = ["owner"]

    def create(self, validated_data):
        validated_data["owner_id"] = self.context["request"].user.owner.id
        return super().create(validated_data)

    def get_field_names(self, declared_fields, info):
        request = self.context["request"]
        field_names = super().get_field_names(declared_fields, info)
        if request.user.is_superuser or hasattr(request.user, "owner"):
            return field_names
        # non superuser/owner
        field_names.remove("submissions")
        return field_names

    def get_submissions(self, obj):
        return [
            QuizSubmissionSerializer(submission, context=self.context).data
            for submission in obj.quizsubmission_set.all()
        ]

    def get_questions(self, obj):
        return [
            QuizQuestionSerializer(question, context=self.context).data
            for question in obj.quizquestion_set.all()
        ]


class QuizQuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()

    class Meta:
        model = models.QuizQuestion
        fields = "__all__"
        read_only_fields = ["quiz"]

    def create(self, validated_data):
        validated_data["quiz_id"] = self.context["view"].kwargs["quiz_id"]
        return super().create(validated_data)

    def get_answers(self, obj):
        return [
            QuizQuestionAnswerSerializer(answer, context=self.context).data
            for answer in obj.quizquestionanswer_set.all()
        ]


class QuizQuestionAnswerSerializer(serializers.ModelSerializer):
    def get_field_names(self, declared_fields, info):
        field_names = super().get_field_names(declared_fields, info)
        request = self.context["request"]
        if request.user.is_superuser or hasattr(request.user, "owner"):
            return field_names
        field_names.remove("is_correct")  # otherwise exclude is_correct field
        return field_names

    class Meta:
        model = models.QuizQuestionAnswer
        fields = "__all__"
        read_only_fields = ["question"]

    def create(self, validated_data):
        validated_data["question_id"] = self.context["view"].kwargs["question_id"]
        return super().create(validated_data)


class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField()

    class Meta:
        model = User
        fields = ["id", "email", "first_name", "last_name"]


class ParticipantSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())

    class Meta:
        model = models.Participant
        fields = "__all__"


class QuizUserAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.QuizUserAnswer
        fields = "__all__"
        read_only_fields = ["submission"]

    def create(self, validated_data):
        validated_data["submission"] = models.QuizSubmission.objects.get(
            participant_id=self.context["view"].kwargs["participant_id"],
            quiz_id=self.context["view"].kwargs["quiz_id"],
        )
        return super().create(validated_data)


class QuizSubmissionSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = models.QuizSubmission
        fields = "__all__"

    def get_answers(self, obj):
        return [
            QuizUserAnswerSerializer(answer, context=self.context).data
            for answer in obj.answer_set.all()
        ]

    def get_score(self, obj):
        return f"{obj.answers_correct_count} / {obj.answers_all_count}"

    def get_progress(self, obj):
        return f"{obj.answers_all_count} / {obj.quiz.quizquestion_set.count()}"


# serializers used only for vaildation:


class QuizInviteSerializer(serializers.Serializer):
    first_name = serializers.CharField(max_length=64)
    last_name = serializers.CharField(max_length=64)
    email = serializers.EmailField()
