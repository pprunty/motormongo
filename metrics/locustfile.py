from locust import HttpUser, task, between, SequentialTaskSet
import json
import uuid


class UserBehavior(SequentialTaskSet):
    host = "http://127.0.0.1:8000 "

    def on_start(self):
        """Generate unique user data for each simulated user."""
        self.username = f"user_{uuid.uuid4()}"
        self.email = f"{self.username}@example.com"
        self.password = "password123"

    @task
    def create_user(self):
        """Create a new user."""
        response = self.client.post("/users/", json={
            "username": self.username,
            "email": self.email,
            "password": self.password
        })
        if response.ok:
            print(f"Created user {self.username}")
        else:
            print(f"Failed to create user {self.username}")

    @task
    def authenticate_user(self):
        """Authenticate the created user."""
        response = self.client.post("/user/auth", json={
            "username": self.username,
            "password": self.password
        })
        if response.ok:
            print(f"Authenticated user {self.username}")
        else:
            print(f"Failed to authenticate user {self.username}")

    @task
    def get_users(self):
        """Fetch list of users."""
        self.client.get("/users")

    @task
    def get_user(self):
        """Fetch the created user by username."""
        self.client.get(f"/users/{self.username}")

    @task
    def update_user(self):
        """Update the created user's email."""
        new_email = f"new_{self.email}"
        new_username = f"new_{self.username}"

        response = self.client.put(f"/users/{self.username}", json={"email": new_email,
                                                                    "username": new_username})
        if response.ok:
            print(f"Updated user {self.username} email to {new_email}")
            self.email = new_email
            self.username = new_username
        else:
            print(f"Failed to update user {self.username}")

    @task
    def delete_user(self):
        """Delete the created user."""
        response = self.client.delete(f"/users/{self.username}")
        if response.ok:
            print(f"Deleted user {self.username}")
        else:
            print(f"Failed to delete user {self.username}")


class WebsiteUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)
