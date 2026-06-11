import random
from locust import HttpUser, task, between

class EventuraFullSystemTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxMjEzNDg1LCJpYXQiOjE3ODExOTE4ODUsImp0aSI6IjU2MTU1MzNiNDk3ODRhNjQ5ZTRhMWQ5OGJjZGZkMDk3IiwidXNlcl9pZCI6IjExIn0.kdBYiZeHQOTR-R64nsDvDG8MIZyFkCsDbZ_Ll-AV4VM"
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }

    @task(6)
    def browse_events_list(self):
        self.client.get("/api/events/", headers=self.headers)

    @task(4)
    def view_event_reviews(self):
        self.client.get("/api/reviews/event/14", headers=self.headers)