from django.test import TestCase, Client
from django.core import mail
from posts.models import User


class ProfileTest(TestCase):
    """User registration and email confirmation test. """
    def setUp(self):
        """User creation and email sending."""
        self.client = Client()
        self.user = User.objects.create_user(
            username="someuser", email="someuser@somemail.com",
            password="somepassword"
        )
        mail.send_mail(
            'Registration confirmation', 'Your registration was a success',
            'admin@yatube.com', [self.user.email]
        )

    def test_email_confirmation(self):
        """Tests of email confirmation."""
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Registration confirmation')
