import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, time
from uuid import uuid4
from email.message import EmailMessage

from app.helpers.mail import (
    connect_to_smtp_server,
    _send_email,
    send_new_assistant_email,
    send_event_rating_email,
    send_event_registration_email,
    send_event_reminder_email,
    send_registration_canceled_email
)
from app.db.database import User, Event, EventDate
from app.models.Role import Role
from app.models.TypeCapacity import TypeCapacity


class TestMailFunctions:
    """Test suite for mail helper functions."""

    @pytest.fixture
    def mock_user(self, faker):
        """Create a mock user for testing."""
        return User(
            id=1,
            email=faker.email(domain="udla.edu.ec"),
            first_name=faker.first_name(),
            last_name=faker.last_name(),
            hashed_password=b"hashed_password",
            role=Role.ASSISTANT
        )

    @pytest.fixture
    def mock_event(self, faker):
        """Create a mock event for testing."""
        return Event(
            id=1,
            name=faker.sentence(nb_words=3),
            description=faker.text(),
            location=faker.address(),
            maps_link="https://maps.app.goo.gl/example",
            capacity=50,
            capacity_type=TypeCapacity.LIMIT_OF_SPACES,
            image_uuid=uuid4(),
            organizer_id=1
        )

    @pytest.fixture
    def mock_event_dates(self, faker):
        """Create mock event dates for testing."""
        return [
            EventDate(
                id=1,
                day_date=date(2025, 8, 15),
                start_time=time(10, 0),
                end_time=time(12, 0),
                event_id=1
            ),
            EventDate(
                id=2,
                day_date=date(2025, 8, 16),
                start_time=time(14, 0),
                end_time=time(16, 0),
                event_id=1
            )
        ]

    @patch('app.helpers.mail.smtplib.SMTP_SSL')
    @patch('app.helpers.mail.ssl.create_default_context')
    def test_connect_to_smtp_server(self, mock_ssl_context, mock_smtp):
        """Test SMTP server connection."""
        mock_server = Mock()
        mock_smtp.return_value = mock_server
        
        result = connect_to_smtp_server()
        
        mock_ssl_context.assert_called_once()
        mock_smtp.assert_called_once_with('smtp.gmail.com', 465, context=mock_ssl_context.return_value)
        mock_server.login.assert_called_once()
        assert result == mock_server

    @patch('app.helpers.mail.connect_to_smtp_server')
    @patch('app.helpers.mail.templates.get_template')
    def test_send_email_success(self, mock_get_template, mock_connect, mock_user):
        """Test successful email sending."""
        # Mock template
        mock_template = Mock()
        mock_template.render.return_value = "<html><body>Test email</body></html>"
        mock_get_template.return_value = mock_template
        
        # Mock SMTP server
        mock_server = Mock()
        mock_connect.return_value.__enter__.return_value = mock_server
        
        # Test data
        subject = "Test Subject"
        template_name = "test_template.html"
        template_vars = {"name": "Test User"}
        
        # Call function
        _send_email(mock_user, subject, template_name, template_vars)
        
        # Verify template rendering
        mock_get_template.assert_called_once_with(template_name)
        mock_template.render.assert_called_once_with(**template_vars)
        
        # Verify SMTP server usage
        mock_connect.assert_called_once()
        mock_server.sendmail.assert_called_once()

    @patch('app.helpers.mail._send_email')
    def test_send_new_assistant_email(self, mock_send_email, mock_user):
        """Test sending new assistant welcome email."""
        send_new_assistant_email(mock_user)
        
        expected_subject = f"Bienvenido {mock_user.first_name} {mock_user.last_name}!"
        expected_template_vars = {"first_name": mock_user.first_name}
        
        mock_send_email.assert_called_once_with(
            mock_user,
            expected_subject,
            "account_creation.html",
            expected_template_vars
        )

    @patch('app.helpers.mail._send_email')
    def test_send_event_rating_email(self, mock_send_email, mock_user):
        """Test sending event rating email."""
        send_event_rating_email(mock_user)
        
        expected_subject = f"¿Qué te pareció el evento {mock_user.first_name} {mock_user.last_name}?"
        expected_template_vars = {"first_name": mock_user.first_name}
        
        mock_send_email.assert_called_once_with(
            mock_user,
            expected_subject,
            "event_rating.html",
            expected_template_vars
        )

    @patch('app.helpers.mail._send_email')
    def test_send_event_registration_email_with_dates(self, mock_send_email, mock_user, mock_event, mock_event_dates):
        """Test sending event registration email when dates are available."""
        send_event_registration_email(mock_user, mock_event, mock_event_dates)
        
        expected_subject = f"Hola {mock_user.first_name} {mock_user.last_name}, estás oficialmente registrado/a!"
        # Should use the earliest date (sorted by day_date)
        earliest_date = sorted(mock_event_dates, key=lambda d: d.day_date)[0]
        expected_template_vars = {
            "event_name": mock_event.name,
            "day_date": earliest_date.day_date.strftime("%d/%m/%Y"),
            "start_time": earliest_date.start_time,
            "end_time": earliest_date.end_time,
            "event_location": mock_event.location,
        }
        
        mock_send_email.assert_called_once_with(
            mock_user,
            expected_subject,
            "event_registration.html",
            expected_template_vars
        )

    @patch('app.helpers.mail._send_email')
    def test_send_event_registration_email_no_dates(self, mock_send_email, mock_user, mock_event):
        """Test sending event registration email when no dates are available."""
        send_event_registration_email(mock_user, mock_event, [])
        
        expected_subject = f"Hola {mock_user.first_name} {mock_user.last_name}, estás oficialmente registrado/a!"
        expected_template_vars = {
            "event_name": mock_event.name,
            "day_date": "Fechas por confirmar",
            "start_time": "Por confirmar",
            "end_time": "Por confirmar",
            "event_location": mock_event.location,
        }
        
        mock_send_email.assert_called_once_with(
            mock_user,
            expected_subject,
            "event_registration.html",
            expected_template_vars
        )

    @patch('app.helpers.mail._send_email')
    def test_send_event_reminder_email(self, mock_send_email, mock_user, mock_event, mock_event_dates):
        """Test sending event reminder email."""
        send_event_reminder_email(mock_user, mock_event, mock_event_dates)
        
        expected_subject = f"Hola {mock_user.first_name} {mock_user.last_name}, te recordamos que del evento '{mock_event.name}' en UDLA ya es mañana"
        # Should use the earliest date (sorted by day_date)
        earliest_date = sorted(mock_event_dates, key=lambda d: d.day_date)[0]
        expected_template_vars = {
            "first_name": mock_user.first_name,
            "event_name": mock_event.name,
            "day_date": earliest_date.day_date.strftime("%d/%m/%Y"),
            "start_time": earliest_date.start_time,
            "end_time": earliest_date.end_time,
            "event_location": mock_event.location,
        }
        
        mock_send_email.assert_called_once_with(
            mock_user,
            expected_subject,
            "event_reminder.html",
            expected_template_vars
        )

    @patch('app.helpers.mail._send_email')
    def test_send_registration_canceled_email(self, mock_send_email, mock_user, mock_event):
        """Test sending registration canceled email."""
        send_registration_canceled_email(mock_user, mock_event)
        
        expected_subject = f"Cancelaste el evento '{mock_event.name}' en la UDLA"
        expected_template_vars = {
            "first_name": mock_user.first_name,
            "event_name": mock_event.name,
        }
        
        mock_send_email.assert_called_once_with(
            mock_user,
            expected_subject,
            "registration_canceled.html",
            expected_template_vars
        )

    @patch('app.helpers.mail.connect_to_smtp_server')
    @patch('app.helpers.mail.templates.get_template')
    def test_send_email_with_email_message_creation(self, mock_get_template, mock_connect, mock_user):
        """Test that EmailMessage is created correctly."""
        # Mock template
        mock_template = Mock()
        mock_template.render.return_value = "<html><body>Test email</body></html>"
        mock_get_template.return_value = mock_template
        
        # Mock SMTP server
        mock_server = Mock()
        mock_connect.return_value.__enter__.return_value = mock_server
        
        # Test data
        subject = "Test Subject"
        template_name = "test_template.html"
        template_vars = {"name": "Test User"}
        
        with patch('app.helpers.mail.EmailMessage') as mock_email_message:
            mock_em = Mock()
            # Make the mock support item assignment like a real EmailMessage
            mock_em.__setitem__ = Mock()
            mock_email_message.return_value = mock_em
            
            # Call function
            _send_email(mock_user, subject, template_name, template_vars)
            
            # Verify EmailMessage creation and configuration
            mock_email_message.assert_called_once()
            assert mock_em.__setitem__.call_count >= 3  # From, To, Subject
            mock_em.set_content.assert_called_once_with(
                "<html><body>Test email</body></html>", 
                subtype='html'
            )
            mock_server.sendmail.assert_called_once()

    def test_event_dates_sorting(self, mock_user, mock_event):
        """Test that event dates are sorted correctly by day_date."""
        # Create dates in non-chronological order
        dates = [
            EventDate(
                id=1,
                day_date=date(2025, 8, 20),
                start_time=time(10, 0),
                end_time=time(12, 0),
                event_id=1
            ),
            EventDate(
                id=2,
                day_date=date(2025, 8, 15),  # This should be first
                start_time=time(14, 0),
                end_time=time(16, 0),
                event_id=1
            ),
            EventDate(
                id=3,
                day_date=date(2025, 8, 18),
                start_time=time(16, 0),
                end_time=time(18, 0),
                event_id=1
            )
        ]
        
        with patch('app.helpers.mail._send_email') as mock_send_email:
            send_event_registration_email(mock_user, mock_event, dates)
            
            # Verify that the earliest date (2025-08-15) was used
            call_args = mock_send_email.call_args[0]
            template_vars = call_args[3]
            assert template_vars["day_date"] == "15/08/2025"

    @patch('app.helpers.mail.connect_to_smtp_server')
    def test_smtp_connection_error_handling(self, mock_connect, mock_user):
        """Test SMTP connection error handling."""
        mock_connect.side_effect = Exception("SMTP connection failed")
        
        with patch('app.helpers.mail.templates.get_template') as mock_get_template:
            mock_template = Mock()
            mock_template.render.return_value = "<html><body>Test</body></html>"
            mock_get_template.return_value = mock_template
            
            with pytest.raises(Exception, match="SMTP connection failed"):
                _send_email(mock_user, "Test", "test.html", {})

    def test_template_rendering_with_correct_variables(self, mock_user, mock_event, mock_event_dates):
        """Test that template variables are passed correctly for each email type."""
        
        with patch('app.helpers.mail._send_email') as mock_send_email:
            # Test new assistant email
            send_new_assistant_email(mock_user)
            args = mock_send_email.call_args[0]
            assert args[3] == {"first_name": mock_user.first_name}
            
            mock_send_email.reset_mock()
            
            # Test event rating email
            send_event_rating_email(mock_user)
            args = mock_send_email.call_args[0]
            assert args[3] == {"first_name": mock_user.first_name}
            
            mock_send_email.reset_mock()
            
            # Test registration canceled email
            send_registration_canceled_email(mock_user, mock_event)
            args = mock_send_email.call_args[0]
            expected_vars = {
                "first_name": mock_user.first_name,
                "event_name": mock_event.name,
            }
            assert args[3] == expected_vars