from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase

from quizzes.permissions import IsOwnerPermission, IsParticipantPermission
from quizzes.tests.factories import OwnerFactory, ParticipantFactory


class IsOwnerPermissionTest(TestCase):
    def test_has_permission_no(self):
        request = RequestFactory()
        request.user = User.objects.create_user("test")
        self.assertFalse(IsOwnerPermission().has_permission(request, None))

    def test_has_permission_yes(self):
        request = RequestFactory()
        request.user = User.objects.create_user("test")
        OwnerFactory(user=request.user)
        self.assertTrue(IsOwnerPermission().has_permission(request, None))

    def test_has_permission_is_superuser(self):
        request = RequestFactory()
        request.user = User.objects.create_superuser("test")
        self.assertTrue(IsOwnerPermission().has_permission(request, None))


class IsParticipantPermissionTest(TestCase):
    def test_has_permission_no(self):
        request = RequestFactory()
        request.user = User.objects.create_user("test")
        self.assertFalse(IsParticipantPermission().has_permission(request, None))

    def test_has_permission_yes(self):
        request = RequestFactory()
        request.user = User.objects.create_user("test")
        ParticipantFactory(user=request.user)
        self.assertTrue(IsParticipantPermission().has_permission(request, None))

    def test_has_permission_is_superuser(self):
        request = RequestFactory()
        request.user = User.objects.create_superuser("test")
        self.assertTrue(IsParticipantPermission().has_permission(request, None))
