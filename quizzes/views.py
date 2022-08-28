from django_filters import rest_framework as filters
from rest_framework import generics, status, views
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from quizzes.models import Participant, Quiz, QuizSubmission
from quizzes.permissions import (
    IsOwnerPermission,
    IsParticipantPermission,
    QuizPermission,
)
from quizzes.serializers import (
    QuizInviteSerializer,
    QuizQuestionAnswerSerializer,
    QuizQuestionSerializer,
    QuizSerializer,
    QuizSubmissionSerializer,
    QuizUserAnswerSerializer,
)


class QuizFilter(filters.FilterSet):
    name = filters.CharFilter(field_name="name", lookup_expr="iexact")

    class Meta:
        model = Quiz
        fields = ["name"]


class QuizListCreateAPIView(generics.ListCreateAPIView):
    queryset = Quiz.objects.all()
    serializer_class = QuizSerializer
    permission_classes = [IsAuthenticated, QuizPermission]
    filter_backends = [SearchFilter, filters.DjangoFilterBackend]
    filterset_class = QuizFilter
    search_fields = ["name"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if hasattr(self.request.user, "owner"):
            queryset = queryset.filter(owner=self.request.user.owner)
        return queryset


class QuizDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Quiz.objects.all()
    permission_classes = [IsAuthenticated, QuizPermission]
    serializer_class = QuizSerializer
    lookup_url_kwarg = "quiz_id"

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_superuser:
            return queryset
        if hasattr(self.request.user, "owner"):
            queryset = queryset.filter(owner=self.request.user.owner)
        if hasattr(self.request.user, "participant"):
            participant = self.request.user.participant
            quiz_id_list = participant.quizsubmission_set.values_list(
                "quiz_id", flat=True
            )
            queryset = queryset.filter(id__in=quiz_id_list)
        return queryset


class QuizQuestionCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerPermission]
    serializer_class = QuizQuestionSerializer


class QuizQuestionAnswerCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsOwnerPermission]
    serializer_class = QuizQuestionAnswerSerializer


class QuizInviteAPIView(views.APIView):
    permission_classes = [IsAuthenticated, IsOwnerPermission]

    def post(self, request, *args, **kwargs):
        quiz = get_object_or_404(Quiz, id=self.kwargs["quiz_id"])
        serializer = QuizInviteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.create_user(
            username=serializer.data["email"],
            email=serializer.data["email"],
            first_name=serializer.data["first_name"],
            last_name=serializer.data["last_name"],
        )
        participant = Participant.objects.create(user=user)
        submission = QuizSubmission.objects.create(
            quiz=quiz,
            owner=self.request.user.owner,
            participant=participant,
        )
        send_mail(
            subject="Quiz Invite!",
            message=f"You've been invited to {quiz.name}.",
            from_email=quiz.owner.user.email,
            recipient_list=[participant.user.email],
        )
        return Response(
            {"submission_id": submission.id}, status=status.HTTP_201_CREATED
        )


class QuizUserAnswerCreateAPIView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, IsParticipantPermission]
    serializer_class = QuizUserAnswerSerializer


class ParticipantSubmissionFilter(filters.FilterSet):
    quiz_name = filters.CharFilter(field_name="quiz__name", lookup_expr="iexact")
    owner_email = filters.CharFilter(
        field_name="owner__user__email", lookup_expr="iexact"
    )

    class Meta:
        model = QuizSubmission
        fields = ["quiz_name"]


class ParticipantSubmissionsListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated, IsParticipantPermission]
    serializer_class = QuizSubmissionSerializer
    filter_backends = [SearchFilter, filters.DjangoFilterBackend]
    filterset_class = ParticipantSubmissionFilter
    search_fields = ["quiz__name", "owner__user__email"]

    def get_queryset(self):
        return QuizSubmission.objects.filter(
            participant_id=self.kwargs["participant_id"],
        )


class ParticipantSubmissionsDetailAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsParticipantPermission]
    serializer_class = QuizSubmissionSerializer

    def get_object(self):
        return QuizSubmission.objects.get(
            participant_id=self.kwargs["participant_id"],
            quiz_id=self.kwargs["quiz_id"],
        )
