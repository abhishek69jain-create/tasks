#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for QuickAssign Task Management System
Tests all authentication, user management, task CRUD, comment, and attachment APIs
"""

import requests
import json
import os
import tempfile
from datetime import datetime, timedelta
import time

class QuickAssignAPITester:
    def __init__(self):
        # Use the production backend URL from frontend .env
        self.base_url = "https://quick-assign-1.preview.emergentagent.com/api"
        self.admin_token = None
        self.team_token = None
        self.admin_user_id = None
        self.team_user_id = None
        self.created_task_ids = []
        self.created_attachment_ids = []
        
        print(f"Testing backend at: {self.base_url}")
        
    def headers(self, token=None):
        """Get headers with optional auth token"""
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers
    
    def test_health_check(self):
        """Test basic health check endpoints"""
        print("\n=== TESTING HEALTH CHECKS ===")
        
        # Test root endpoint
        try:
            response = requests.get(f"{self.base_url}/")
            assert response.status_code == 200, f"Root endpoint failed: {response.status_code}"
            data = response.json()
            assert "message" in data, "Root endpoint missing message"
            print("✅ Root endpoint working")
        except Exception as e:
            print(f"❌ Root endpoint failed: {e}")
            return False
            
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/health")
            assert response.status_code == 200, f"Health check failed: {response.status_code}"
            data = response.json()
            assert data.get("status") == "healthy", "Health check not healthy"
            print("✅ Health check working")
        except Exception as e:
            print(f"❌ Health check failed: {e}")
            return False
            
        return True
    
    def test_user_registration(self):
        """Test user registration - first user becomes admin"""
        print("\n=== TESTING USER REGISTRATION ===")
        
        # Test admin registration (first user)
        admin_data = {
            "email": "admin@quickassign.com",
            "password": "AdminPass123!",
            "name": "Admin User"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                headers=self.headers(),
                json=admin_data
            )
            
            if response.status_code == 400 and "Email already registered" in response.text:
                print("⚠️ Admin user already exists - trying login instead")
                return self.test_user_login()
                
            assert response.status_code == 200, f"Admin registration failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "access_token" in data, "Missing access token in admin registration"
            assert data.get("token_type") == "bearer", "Invalid token type"
            assert "user" in data, "Missing user data in registration"
            assert data["user"]["role"] == "admin", "First user should be admin"
            
            self.admin_token = data["access_token"]
            self.admin_user_id = data["user"]["id"]
            print("✅ Admin registration successful")
            
        except Exception as e:
            print(f"❌ Admin registration failed: {e}")
            return False
        
        # Test team member registration (second user)
        team_data = {
            "email": "team@quickassign.com",
            "password": "TeamPass123!",
            "name": "Team Member"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/register",
                headers=self.headers(),
                json=team_data
            )
            
            if response.status_code == 400 and "Email already registered" in response.text:
                print("⚠️ Team user already exists - trying login instead")
                # Try to login as team member
                login_response = requests.post(
                    f"{self.base_url}/auth/login",
                    headers=self.headers(),
                    json={"email": team_data["email"], "password": team_data["password"]}
                )
                if login_response.status_code == 200:
                    login_data = login_response.json()
                    self.team_token = login_data["access_token"]
                    self.team_user_id = login_data["user"]["id"]
                    print("✅ Team member login successful")
                    return True
                else:
                    print(f"❌ Team member login failed: {login_response.status_code}")
                    return False
            
            assert response.status_code == 200, f"Team registration failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "access_token" in data, "Missing access token in team registration"
            assert data["user"]["role"] == "team_member", "Second user should be team_member"
            
            self.team_token = data["access_token"]
            self.team_user_id = data["user"]["id"]
            print("✅ Team member registration successful")
            
        except Exception as e:
            print(f"❌ Team member registration failed: {e}")
            return False
            
        return True
    
    def test_user_login(self):
        """Test user login functionality"""
        print("\n=== TESTING USER LOGIN ===")
        
        # Test admin login
        admin_login = {
            "email": "admin@quickassign.com",
            "password": "AdminPass123!"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers=self.headers(),
                json=admin_login
            )
            assert response.status_code == 200, f"Admin login failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "access_token" in data, "Missing access token in admin login"
            assert data["user"]["role"] == "admin", "Admin login should return admin role"
            
            self.admin_token = data["access_token"]
            self.admin_user_id = data["user"]["id"]
            print("✅ Admin login successful")
            
        except Exception as e:
            print(f"❌ Admin login failed: {e}")
            return False
        
        # Test team member login
        team_login = {
            "email": "team@quickassign.com",
            "password": "TeamPass123!"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers=self.headers(),
                json=team_login
            )
            
            if response.status_code == 401:
                print("⚠️ Team member doesn't exist - will create during registration test")
                return True
                
            assert response.status_code == 200, f"Team login failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "access_token" in data, "Missing access token in team login"
            assert data["user"]["role"] == "team_member", "Team login should return team_member role"
            
            self.team_token = data["access_token"]
            self.team_user_id = data["user"]["id"]
            print("✅ Team member login successful")
            
        except Exception as e:
            print(f"❌ Team member login failed: {e}")
            return False
            
        # Test invalid credentials
        try:
            invalid_login = {
                "email": "invalid@example.com",
                "password": "wrongpassword"
            }
            response = requests.post(
                f"{self.base_url}/auth/login",
                headers=self.headers(),
                json=invalid_login
            )
            assert response.status_code == 401, "Invalid credentials should return 401"
            print("✅ Invalid credentials properly rejected")
            
        except Exception as e:
            print(f"❌ Invalid credentials test failed: {e}")
            return False
            
        return True
    
    def test_auth_me(self):
        """Test get current user endpoint"""
        print("\n=== TESTING AUTH/ME ENDPOINT ===")
        
        if not self.admin_token:
            print("❌ No admin token available for testing")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"Auth/me failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert "id" in data, "Missing user id in auth/me response"
            assert "email" in data, "Missing email in auth/me response"
            assert "role" in data, "Missing role in auth/me response"
            assert data["role"] == "admin", "Admin token should return admin role"
            print("✅ Auth/me endpoint working")
            
        except Exception as e:
            print(f"❌ Auth/me test failed: {e}")
            return False
            
        # Test with invalid token
        try:
            response = requests.get(
                f"{self.base_url}/auth/me",
                headers=self.headers("invalid_token")
            )
            assert response.status_code == 401, "Invalid token should return 401"
            print("✅ Invalid token properly rejected")
            
        except Exception as e:
            print(f"❌ Invalid token test failed: {e}")
            return False
            
        return True
    
    def test_user_management(self):
        """Test user listing endpoint"""
        print("\n=== TESTING USER MANAGEMENT ===")
        
        if not self.admin_token:
            print("❌ No admin token available for testing")
            return False
            
        try:
            response = requests.get(
                f"{self.base_url}/users",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"Get users failed: {response.status_code} - {response.text}"
            
            data = response.json()
            assert isinstance(data, list), "Users endpoint should return a list"
            assert len(data) >= 1, "Should have at least one user (admin)"
            
            # Check user structure
            user = data[0]
            assert "id" in user, "User missing id field"
            assert "email" in user, "User missing email field"
            assert "name" in user, "User missing name field"
            assert "role" in user, "User missing role field"
            
            print(f"✅ User management working - Found {len(data)} users")
            
        except Exception as e:
            print(f"❌ User management test failed: {e}")
            return False
            
        return True
    
    def test_task_crud(self):
        """Test task CRUD operations"""
        print("\n=== TESTING TASK CRUD OPERATIONS ===")
        
        if not self.admin_token or not self.team_user_id:
            print("❌ Missing tokens/user IDs for task testing")
            return False
        
        # Test create task
        deadline = (datetime.now() + timedelta(days=7)).isoformat()
        task_data = {
            "title": "Test Task - Backend API Testing",
            "description": "This is a test task created during backend API testing to verify CRUD operations work correctly.",
            "assignedTo": self.team_user_id,
            "deadline": deadline,
            "priority": "High",
            "department": "Marketing",
            "status": "Pending"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks",
                headers=self.headers(self.admin_token),
                json=task_data
            )
            assert response.status_code == 200, f"Create task failed: {response.status_code} - {response.text}"
            
            created_task = response.json()
            assert "id" in created_task, "Created task missing id"
            assert created_task["title"] == task_data["title"], "Task title mismatch"
            assert created_task["assignedTo"] == self.team_user_id, "Task assignment mismatch"
            assert "assignedToName" in created_task, "Missing assignedToName"
            assert "assignedBy" in created_task, "Missing assignedBy"
            
            task_id = created_task["id"]
            self.created_task_ids.append(task_id)
            print("✅ Task creation successful")
            
        except Exception as e:
            print(f"❌ Task creation failed: {e}")
            return False
        
        # Test get all tasks
        try:
            response = requests.get(
                f"{self.base_url}/tasks",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"Get tasks failed: {response.status_code} - {response.text}"
            
            tasks = response.json()
            assert isinstance(tasks, list), "Tasks endpoint should return a list"
            assert len(tasks) >= 1, "Should have at least one task"
            
            # Find our created task
            our_task = next((t for t in tasks if t["id"] == task_id), None)
            assert our_task is not None, "Created task not found in task list"
            print(f"✅ Task retrieval successful - Found {len(tasks)} tasks")
            
        except Exception as e:
            print(f"❌ Task retrieval failed: {e}")
            return False
        
        # Test get specific task
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"Get specific task failed: {response.status_code} - {response.text}"
            
            task = response.json()
            assert task["id"] == task_id, "Retrieved task ID mismatch"
            assert task["title"] == task_data["title"], "Retrieved task title mismatch"
            print("✅ Specific task retrieval successful")
            
        except Exception as e:
            print(f"❌ Specific task retrieval failed: {e}")
            return False
        
        # Test update task
        update_data = {
            "title": "Updated Test Task Title",
            "status": "In Progress",
            "priority": "Medium"
        }
        
        try:
            response = requests.put(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers(self.admin_token),
                json=update_data
            )
            assert response.status_code == 200, f"Update task failed: {response.status_code} - {response.text}"
            
            updated_task = response.json()
            assert updated_task["title"] == update_data["title"], "Task title not updated"
            assert updated_task["status"] == update_data["status"], "Task status not updated"
            assert updated_task["priority"] == update_data["priority"], "Task priority not updated"
            print("✅ Task update successful")
            
        except Exception as e:
            print(f"❌ Task update failed: {e}")
            return False
        
        # Test task filtering
        try:
            # Filter by priority
            response = requests.get(
                f"{self.base_url}/tasks?priority=Medium",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, "Priority filter failed"
            filtered_tasks = response.json()
            assert all(t["priority"] == "Medium" for t in filtered_tasks), "Priority filter not working"
            
            # Filter by department
            response = requests.get(
                f"{self.base_url}/tasks?department=Marketing",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, "Department filter failed"
            filtered_tasks = response.json()
            assert all(t["department"] == "Marketing" for t in filtered_tasks), "Department filter not working"
            
            # Filter by status
            response = requests.get(
                f"{self.base_url}/tasks?status=In Progress",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, "Status filter failed"
            filtered_tasks = response.json()
            assert all(t["status"] == "In Progress" for t in filtered_tasks), "Status filter not working"
            
            print("✅ Task filtering successful")
            
        except Exception as e:
            print(f"❌ Task filtering failed: {e}")
            return False
        
        return True
    
    def test_task_permissions(self):
        """Test task permission restrictions"""
        print("\n=== TESTING TASK PERMISSIONS ===")
        
        if not self.admin_token or not self.team_token or not self.created_task_ids:
            print("❌ Missing tokens or tasks for permission testing")
            return False
        
        task_id = self.created_task_ids[0]
        
        # Test team member can view tasks
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers(self.team_token)
            )
            assert response.status_code == 200, "Team member should be able to view tasks"
            print("✅ Team member can view tasks")
            
        except Exception as e:
            print(f"❌ Team member task view failed: {e}")
            return False
        
        # Test only admin can delete tasks
        try:
            # Team member should NOT be able to delete
            response = requests.delete(
                f"{self.base_url}/tasks/{task_id}",
                headers=self.headers(self.team_token)
            )
            assert response.status_code == 403, "Team member should not be able to delete tasks"
            print("✅ Team member correctly blocked from deleting tasks")
            
        except Exception as e:
            print(f"❌ Team member delete restriction failed: {e}")
            return False
        
        return True
    
    def test_comments(self):
        """Test comment functionality"""
        print("\n=== TESTING COMMENT FUNCTIONALITY ===")
        
        if not self.admin_token or not self.created_task_ids:
            print("❌ Missing tokens or tasks for comment testing")
            return False
        
        task_id = self.created_task_ids[0]
        
        # Test create comment
        comment_data = {
            "text": "This is a test comment added during backend API testing. It verifies that the comment system works correctly."
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/tasks/{task_id}/comments",
                headers=self.headers(self.admin_token),
                json=comment_data
            )
            assert response.status_code == 200, f"Create comment failed: {response.status_code} - {response.text}"
            
            comment = response.json()
            assert "id" in comment, "Comment missing id"
            assert comment["text"] == comment_data["text"], "Comment text mismatch"
            assert comment["taskId"] == task_id, "Comment taskId mismatch"
            assert "userName" in comment, "Comment missing userName"
            assert "createdAt" in comment, "Comment missing createdAt"
            
            print("✅ Comment creation successful")
            
        except Exception as e:
            print(f"❌ Comment creation failed: {e}")
            return False
        
        # Test get comments
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}/comments",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"Get comments failed: {response.status_code} - {response.text}"
            
            comments = response.json()
            assert isinstance(comments, list), "Comments endpoint should return a list"
            assert len(comments) >= 1, "Should have at least one comment"
            
            # Check comment structure
            comment = comments[0]
            assert "id" in comment, "Comment missing id field"
            assert "text" in comment, "Comment missing text field"
            assert "userName" in comment, "Comment missing userName field"
            assert "createdAt" in comment, "Comment missing createdAt field"
            
            print(f"✅ Comment retrieval successful - Found {len(comments)} comments")
            
        except Exception as e:
            print(f"❌ Comment retrieval failed: {e}")
            return False
        
        # Test team member can also add comments
        if self.team_token:
            team_comment_data = {
                "text": "This is a comment from team member during testing."
            }
            
            try:
                response = requests.post(
                    f"{self.base_url}/tasks/{task_id}/comments",
                    headers=self.headers(self.team_token),
                    json=team_comment_data
                )
                assert response.status_code == 200, "Team member should be able to add comments"
                print("✅ Team member can add comments")
                
            except Exception as e:
                print(f"❌ Team member comment creation failed: {e}")
                return False
        
        return True
    
    def test_attachments(self):
        """Test file attachment functionality"""
        print("\n=== TESTING ATTACHMENT FUNCTIONALITY ===")
        
        if not self.admin_token or not self.created_task_ids:
            print("❌ Missing tokens or tasks for attachment testing")
            return False
        
        task_id = self.created_task_ids[0]
        
        # Create a test file
        test_content = "This is a test file for attachment testing.\nIt contains multiple lines.\nUsed to verify file upload/download works correctly."
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
            temp_file.write(test_content)
            temp_file_path = temp_file.name
        
        try:
            # Test file upload
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test_attachment.txt', f, 'text/plain')}
                headers = {"Authorization": f"Bearer {self.admin_token}"}
                
                response = requests.post(
                    f"{self.base_url}/tasks/{task_id}/attachments",
                    headers=headers,
                    files=files
                )
                assert response.status_code == 200, f"File upload failed: {response.status_code} - {response.text}"
                
                attachment = response.json()
                assert "id" in attachment, "Attachment missing id"
                assert attachment["fileName"] == "test_attachment.txt", "Attachment filename mismatch"
                assert attachment["taskId"] == task_id, "Attachment taskId mismatch"
                assert "uploadedByName" in attachment, "Attachment missing uploadedByName"
                
                attachment_id = attachment["id"]
                self.created_attachment_ids.append(attachment_id)
                print("✅ File upload successful")
                
        except Exception as e:
            print(f"❌ File upload failed: {e}")
            return False
        finally:
            # Clean up temp file
            os.unlink(temp_file_path)
        
        # Test get attachments
        try:
            response = requests.get(
                f"{self.base_url}/tasks/{task_id}/attachments",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"Get attachments failed: {response.status_code} - {response.text}"
            
            attachments = response.json()
            assert isinstance(attachments, list), "Attachments endpoint should return a list"
            assert len(attachments) >= 1, "Should have at least one attachment"
            
            # Check attachment structure
            attachment = attachments[0]
            assert "id" in attachment, "Attachment missing id field"
            assert "fileName" in attachment, "Attachment missing fileName field"
            assert "fileType" in attachment, "Attachment missing fileType field"
            assert "uploadedByName" in attachment, "Attachment missing uploadedByName field"
            
            print(f"✅ Attachment listing successful - Found {len(attachments)} attachments")
            
        except Exception as e:
            print(f"❌ Attachment listing failed: {e}")
            return False
        
        # Test file download
        try:
            response = requests.get(
                f"{self.base_url}/attachments/{attachment_id}/download",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 200, f"File download failed: {response.status_code} - {response.text}"
            
            # Check if downloaded content matches
            downloaded_content = response.text
            assert test_content in downloaded_content or downloaded_content in test_content, "Downloaded content doesn't match uploaded content"
            
            # Check headers
            assert 'content-disposition' in response.headers or 'Content-Disposition' in response.headers, "Missing content disposition header"
            
            print("✅ File download successful")
            
        except Exception as e:
            print(f"❌ File download failed: {e}")
            return False
        
        return True
    
    def test_error_handling(self):
        """Test various error scenarios"""
        print("\n=== TESTING ERROR HANDLING ===")
        
        # Test invalid task ID
        try:
            response = requests.get(
                f"{self.base_url}/tasks/invalid_id",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 400, "Invalid task ID should return 400"
            print("✅ Invalid task ID properly handled")
            
        except Exception as e:
            print(f"❌ Invalid task ID test failed: {e}")
            return False
        
        # Test non-existent task
        try:
            response = requests.get(
                f"{self.base_url}/tasks/507f1f77bcf86cd799439011",
                headers=self.headers(self.admin_token)
            )
            assert response.status_code == 404, "Non-existent task should return 404"
            print("✅ Non-existent task properly handled")
            
        except Exception as e:
            print(f"❌ Non-existent task test failed: {e}")
            return False
        
        # Test unauthorized access
        try:
            response = requests.get(
                f"{self.base_url}/tasks",
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 401, "Unauthorized access should return 401"
            print("✅ Unauthorized access properly handled")
            
        except Exception as e:
            print(f"❌ Unauthorized access test failed: {e}")
            return False
        
        return True
    
    def cleanup_test_data(self):
        """Clean up test data created during testing"""
        print("\n=== CLEANING UP TEST DATA ===")
        
        if not self.admin_token:
            print("⚠️ No admin token available for cleanup")
            return
        
        # Delete test tasks (admin only)
        for task_id in self.created_task_ids:
            try:
                response = requests.delete(
                    f"{self.base_url}/tasks/{task_id}",
                    headers=self.headers(self.admin_token)
                )
                if response.status_code == 200:
                    print(f"✅ Deleted task {task_id}")
                else:
                    print(f"⚠️ Could not delete task {task_id}: {response.status_code}")
            except Exception as e:
                print(f"⚠️ Error deleting task {task_id}: {e}")
        
        print("✅ Cleanup completed")
    
    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting comprehensive QuickAssign Backend API Testing")
        print("=" * 60)
        
        test_results = {
            "health_check": False,
            "user_registration": False,
            "user_login": False,
            "auth_me": False,
            "user_management": False,
            "task_crud": False,
            "task_permissions": False,
            "comments": False,
            "attachments": False,
            "error_handling": False
        }
        
        # Run tests
        test_results["health_check"] = self.test_health_check()
        test_results["user_registration"] = self.test_user_registration()
        test_results["user_login"] = self.test_user_login()
        test_results["auth_me"] = self.test_auth_me()
        test_results["user_management"] = self.test_user_management()
        test_results["task_crud"] = self.test_task_crud()
        test_results["task_permissions"] = self.test_task_permissions()
        test_results["comments"] = self.test_comments()
        test_results["attachments"] = self.test_attachments()
        test_results["error_handling"] = self.test_error_handling()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in test_results.items():
            status = "✅ PASS" if result else "❌ FAIL"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print(f"\nTotal Tests: {len(test_results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        
        if failed == 0:
            print("\n🎉 ALL TESTS PASSED! Backend APIs are working correctly.")
        else:
            print(f"\n⚠️ {failed} tests failed. Please check the detailed output above.")
        
        return test_results


if __name__ == "__main__":
    tester = QuickAssignAPITester()
    results = tester.run_all_tests()