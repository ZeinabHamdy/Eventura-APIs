from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from events.validators.event_validators import (
    validate_end_date_after_start,
    validate_start_date_in_future,
    validate_start_date_on_publish,
    validate_status_flow,
)

class EventValidatorsTestCase(TestCase):
    def test_end_date_before_or_equal_start_date_raises_error(self):
        now = timezone.now()
        with self.assertRaises(ValidationError):
            validate_end_date_after_start(start_date=now + timedelta(days=2), end_date=now + timedelta(days=1))
        with self.assertRaises(ValidationError):
            validate_end_date_after_start(start_date=now, end_date=now)

    def test_end_date_after_start_date_passes(self):
        now = timezone.now()
        try:
            validate_end_date_after_start(start_date=now, end_date=now + timedelta(hours=2))
        except ValidationError:
            self.fail("validate_end_date_after_start raised ValidationError unexpectedly!")

    def test_start_date_in_past_raises_error(self):
        past_date = timezone.now() - timedelta(minutes=5)
        with self.assertRaises(ValidationError):
            validate_start_date_in_future(past_date)

    def test_start_date_in_future_passes(self):
        future_date = timezone.now() + timedelta(days=1)
        try:
            validate_start_date_in_future(future_date)
        except ValidationError:
            self.fail("validate_start_date_in_future raised ValidationError unexpectedly!")

    def test_publish_event_with_past_start_date_raises_error(self):
        past_date = timezone.now() - timedelta(days=1)
        with self.assertRaises(ValidationError):
            validate_start_date_on_publish(status='drafted', new_status='published', start_date=past_date)

    def test_publish_event_with_future_start_date_passes(self):
        future_date = timezone.now() + timedelta(days=1)
        try:
            validate_start_date_on_publish(status='drafted', new_status='published', start_date=future_date)
        except ValidationError:
            self.fail("validate_start_date_on_publish raised ValidationError unexpectedly!")


    """ status flow---- """
    def test_status_flow_same_status_passes(self):
        try:
            validate_status_flow(current_status='published', new_status='published', start_date=timezone.now())
        except ValidationError:
            self.fail("validate_status_flow raised ValidationError when status hasn't changed.")

    def test_status_flow_allowed_transitions_pass(self):
        future_date = timezone.now() + timedelta(days=1)
        try:
            validate_status_flow('drafted', 'published', future_date)
            validate_status_flow('drafted', 'cancelled', future_date)
            validate_status_flow('published', 'cancelled', future_date)
        except ValidationError:
            self.fail("Allowed status transition raised ValidationError unexpectedly!")

    def test_status_flow_forbidden_transitions_raise_error(self):
        with self.assertRaises(ValidationError):
            validate_status_flow('published', 'drafted', timezone.now())
        with self.assertRaises(ValidationError):
            validate_status_flow('cancelled', 'drafted', timezone.now())
        with self.assertRaises(ValidationError):
            validate_status_flow('cancelled', 'published', timezone.now())

    def test_cancel_published_event_in_past_raises_error(self):
        past_date = timezone.now() - timedelta(hours=1)
        with self.assertRaises(ValidationError):
            validate_status_flow(current_status='published', new_status='cancelled', start_date=past_date)