import pytest
from fastapi.testclient import TestClient
from fastapi import status

from app.schemas.task import TaskStatus, TaskPriority

class TestTaskEndpoints:
    """Integration tests for the task API endpoints."""
    
    def test_create_task(self, client: TestClient):
        """Test creating a task via the API."""
        # Setup
        task_data = {
            "title": "API Test Task",
            "description": "Created via API test",
            "status": "pending",
            "priority": 3
        }
        
        # Test
        response = client.post("/api/v1/tasks", json=task_data)
        
        # Verify
        assert response.status_code == status.HTTP_201_CREATED
        
        data = response.json()
        assert data["message"] == "Success"
        assert data["status"] == 201
        
        task_result = data["data"]
        assert task_result["title"] == task_data["title"]
        assert task_result["description"] == task_data["description"]
        assert task_result["status"] == task_data["status"]
        assert task_result["priority"] == task_data["priority"]
    
    def test_create_task_duplicate(self, client: TestClient, sample_task):
        """Test creating a task with a duplicate title."""
        # Setup
        task_data = {
            "title": sample_task.title,  # Same title as sample_task
            "description": "This should fail",
            "status": "pending",
            "priority": 1
        }
        
        # Test
        response = client.post("/api/v1/tasks", json=task_data)
        
        # Verify
        assert response.status_code == status.HTTP_409_CONFLICT
        
        data = response.json()
        assert data["message"] == "Error"
        assert "already exists" in data["data"]["detail"]
        assert data["data"]["error_code"] == "DUPLICATE_TASK"
    
    def test_get_all_tasks(self, client: TestClient, sample_task):
        """Test retrieving all tasks."""
        # Test
        response = client.get("/api/v1/tasks")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "Success"
        
        pagination = data["data"]
        assert pagination["total"] >= 1  # At least our sample task
        assert pagination["skip"] == 0
        assert pagination["limit"] == 10  # Default limit
        
        # Check that our sample task is in the results
        task_titles = [task["title"] for task in pagination["items"]]
        assert sample_task.title in task_titles
    
    def test_get_tasks_with_filters(self, client: TestClient, sample_task):
        """Test retrieving tasks with filtering."""
        # Create a second task with different status
        completed_task_data = {
            "title": "Completed Task",
            "description": "This task is completed",
            "status": "completed",
            "priority": 4
        }
        client.post("/api/v1/tasks", json=completed_task_data)
        
        # Test filtering by status
        response = client.get("/api/v1/tasks?status=completed")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        pagination = data["data"]
        
        # All returned tasks should have completed status
        for task in pagination["items"]:
            assert task["status"] == "completed"
        
        # Sample task (pending) should not be in results
        task_titles = [task["title"] for task in pagination["items"]]
        assert sample_task.title not in task_titles
        assert "Completed Task" in task_titles
    
    def test_get_tasks_with_search(self, client: TestClient):
        """Test searching tasks."""
        # Create tasks with specific terms to search for
        search_task_data = {
            "title": "SearchableTask",
            "description": "Contains searchable keyword",
            "status": "pending",
            "priority": 2
        }
        client.post("/api/v1/tasks", json=search_task_data)
        
        # Test searching
        response = client.get("/api/v1/tasks?search=searchable")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        pagination = data["data"]
        
        # Results should contain our searchable task
        task_titles = [task["title"] for task in pagination["items"]]
        assert "SearchableTask" in task_titles
    
    def test_get_tasks_with_pagination(self, client: TestClient):
        """Test pagination of tasks."""
        # Create multiple tasks
        for i in range(5):
            task_data = {
                "title": f"Pagination Task {i}",
                "description": f"Task for testing pagination {i}",
                "status": "pending",
                "priority": 1
            }
            client.post("/api/v1/tasks", json=task_data)
        
        # Test pagination - first page
        response = client.get("/api/v1/tasks?skip=0&limit=3")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        pagination = data["data"]
        
        assert len(pagination["items"]) <= 3  # Should return at most 3 items
        
        # Get second page
        response = client.get("/api/v1/tasks?skip=3&limit=3")
        
        # Verify second page
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        pagination = data["data"]
        
        assert len(pagination["items"]) > 0  # Should return more items on second page
    
    def test_get_task_by_title(self, client: TestClient, sample_task):
        """Test retrieving a specific task by title."""
        # Test
        response = client.get(f"/api/v1/tasks/{sample_task.title}")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "Success"
        
        task_data = data["data"]
        assert task_data["title"] == sample_task.title
        assert task_data["description"] == sample_task.description
        assert task_data["status"] == sample_task.status
        assert task_data["priority"] == sample_task.priority
    
    def test_get_task_not_found(self, client: TestClient):
        """Test retrieving a non-existent task."""
        # Test
        response = client.get("/api/v1/tasks/Non-existent-Task")
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["message"] == "Error"
        assert data["data"]["error_code"] == "TASK_NOT_FOUND"
    
    def test_update_task(self, client: TestClient, sample_task):
        """Test updating a task."""
        # Setup
        update_data = {
            "title": sample_task.title,  # Same title
            "description": "Updated via API test",
            "status": "in-progress",
            "priority": 4
        }
        
        # Test
        response = client.put(f"/api/v1/tasks/{sample_task.title}", json=update_data)
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "Success"
        
        # Verify the task was updated by fetching it
        get_response = client.get(f"/api/v1/tasks/{sample_task.title}")
        assert get_response.status_code == status.HTTP_200_OK
        
        updated_task = get_response.json()["data"]
        assert updated_task["description"] == "Updated via API test"
        assert updated_task["status"] == "in-progress"
        assert updated_task["priority"] == 4
    
    def test_update_task_title_mismatch(self, client: TestClient, sample_task):
        """Test updating a task with mismatched titles."""
        # Setup
        update_data = {
            "title": "Different Title",  # Different title
            "description": "This should fail",
            "status": "in-progress",
            "priority": 4
        }
        
        # Test
        response = client.put(f"/api/v1/tasks/{sample_task.title}", json=update_data)
        
        # Verify
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        
        data = response.json()
        assert data["message"] == "Error"
        assert "Cannot update a task name" in data["data"]["detail"]
        assert data["data"]["error_code"] == "TITLE_MISMATCH"
    
    def test_update_task_not_found(self, client: TestClient):
        """Test updating a non-existent task."""
        # Setup
        update_data = {
            "title": "Non-existent Task",
            "description": "This should fail",
            "status": "in-progress",
            "priority": 4
        }
        
        # Test
        response = client.put("/api/v1/tasks/Non-existent-Task", json=update_data)
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["message"] == "Error"
        assert data["data"]["error_code"] == "TASK_NOT_FOUND"
    
    def test_delete_task(self, client: TestClient, sample_task):
        """Test deleting a task."""
        # Test
        response = client.delete(f"/api/v1/tasks/{sample_task.title}")
        
        # Verify
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["message"] == "Success"
        
        # Verify the task was deleted by trying to fetch it
        get_response = client.get(f"/api/v1/tasks/{sample_task.title}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_delete_task_not_found(self, client: TestClient):
        """Test deleting a non-existent task."""
        # Test
        response = client.delete("/api/v1/tasks/Non-existent-Task")
        
        # Verify
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        data = response.json()
        assert data["message"] == "Error"
        assert data["data"]["error_code"] == "TASK_NOT_FOUND"
    
    def test_create_task_with_invalid_data(self, client: TestClient):
        """Test validation errors when creating a task with invalid data."""
        # Setup - a task with invalid data (empty title)
        invalid_task = {
            "title": "",  # Empty title - should fail validation
            "description": "This should fail validation",
            "status": "pending",
            "priority": 3
        }
        
        # Test
        response = client.post("/api/v1/tasks", json=invalid_task)
        
        # Verify
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        data = response.json()
        assert data["message"] == "Error"
        assert "VALIDATION_ERROR" in data["data"]["error_code"]
        assert "title" in data["data"]["detail"]  # Error message should mention the title field
    
    def test_response_format_structure(self, client: TestClient, sample_task):
        """Test that API responses follow the expected format structure."""
        # Test
        response = client.get(f"/api/v1/tasks/{sample_task.title}")
        
        # Verify response has the correct structure
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        # Check message response structure
        assert "message" in data
        assert "data" in data
        assert "status" in data
        
        # Check actual values
        assert data["message"] == "Success"
        assert data["status"] == 200
        
        # Check task data structure
        task_data = data["data"]
        assert "title" in task_data
        assert "description" in task_data
        assert "status" in task_data
        assert "priority" in task_data
    
    @pytest.mark.parametrize(
        "task_data,expected_status",
        [
            ({"title": "Valid Task", "description": "This is valid", "status": "pending", "priority": 3}, status.HTTP_201_CREATED),
            ({"title": "Missing Description", "status": "pending", "priority": 3}, status.HTTP_422_UNPROCESSABLE_ENTITY),
            ({"title": "Invalid Status", "description": "Invalid status", "status": "not-a-real-status", "priority": 3}, status.HTTP_422_UNPROCESSABLE_ENTITY),
            ({"title": "Invalid Priority", "description": "Invalid priority", "status": "pending", "priority": 10}, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ]
    )
    def test_create_task_validation_cases(self, client: TestClient, task_data, expected_status):
        """Test various validation scenarios when creating tasks."""
        # Test
        response = client.post("/api/v1/tasks", json=task_data)
        
        # Verify
        assert response.status_code == expected_status
