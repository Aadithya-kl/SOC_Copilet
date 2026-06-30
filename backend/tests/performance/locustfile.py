from locust import HttpUser, task, between

class SOCAnalystUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        # In a real scenario, this would authenticate and get a JWT token
        # self.client.post("/api/v1/auth/login", json={"username": "admin", "password": "password"})
        self.headers = {"Authorization": "Bearer mock_token"}

    @task(3)
    def view_dashboard(self):
        self.client.get("/api/v1/health", headers=self.headers)

    @task(1)
    def trigger_analysis(self):
        # Mock investigation ID
        inv_id = "00000000-0000-0000-0000-000000000000"
        self.client.post(f"/api/v1/ai/analyze?investigation_id={inv_id}", headers=self.headers)
