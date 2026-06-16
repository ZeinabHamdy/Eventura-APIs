import random
from locust import HttpUser, task, between

class EventuraFullSystemTest(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzgxNTU1NDkzLCJpYXQiOjE3ODE1MzM4OTMsImp0aSI6IjYxMzFlYzZiMjQwYjQyOTRiYjU3NTAzYTA5Mjc0YzQyIiwidXNlcl9pZCI6IjExIn0.BxdZ0jRIeb5ms9a0tZmgW31t6VHI8LVk67WCIHgwnyc"
        self.headers = {
            "Authorization": f"Bearer {access_token}"
        }

    @task(6)
    def browse_events_list(self):
        self.client.get("/api/events/", headers=self.headers)

    @task(4)
    def view_event_reviews(self):
        self.client.get("/api/reviews/event/14", headers=self.headers)