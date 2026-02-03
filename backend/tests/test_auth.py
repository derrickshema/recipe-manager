"""
Authentication Tests

These tests verify that our authentication system works correctly:
- User registration
- Login with correct/incorrect credentials
- Protected endpoints require authentication

HOW TO READ THESE TESTS
=======================
Each test follows the "AAA" pattern:
- Arrange: Set up the test data
- Act: Perform the action being tested
- Assert: Verify the result

Test names describe what they test:
- test_register_user_success → "Test that registering a user succeeds"
- test_login_wrong_password → "Test that login with wrong password fails"

NOTE: The login endpoint is /auth/token (not /auth/login)
"""

import pytest


class TestRegistration:
    """Tests for user registration endpoint."""
    
    def test_register_user_success(self, client, test_user_data):
        """
        Test that a new user can register successfully.
        
        This is a "happy path" test - everything works as expected.
        """
        # Act: Send registration request
        response = client.post("/auth/register", json=test_user_data)
        
        # Assert: Check response
        assert response.status_code == 201, f"Expected 201, got {response.status_code}: {response.json()}"
        
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "id" in data  # User should have an ID
        assert "password" not in data  # Password should NOT be in response!
        assert "hashed_password" not in data  # Hash should NOT be exposed!
    
    def test_register_duplicate_username(self, client, test_user_data, test_customer):
        """
        Test that registering with an existing username fails.
        
        We use test_customer fixture which creates a user first,
        then try to register with the same username.
        """
        # Arrange: Use the existing customer's username
        duplicate_data = {
            "first_name": "Another",
            "last_name": "User",
            "username": test_customer.username,  # Already exists!
            "email": "newemail@example.com",
            "password": "NewPassword123!",
        }
        
        # Act
        response = client.post("/auth/register", json=duplicate_data)
        
        # Assert: Should fail with 400 Bad Request
        assert response.status_code == 400
        assert "username" in response.json()["detail"].lower()
    
    def test_register_duplicate_email(self, client, test_user_data, test_customer):
        """Test that registering with an existing email fails."""
        duplicate_data = {
            "first_name": "Another",
            "last_name": "User",
            "username": "newusername",
            "email": test_customer.email,  # Already exists!
            "password": "NewPassword123!",
        }
        
        response = client.post("/auth/register", json=duplicate_data)
        
        assert response.status_code == 400
        assert "email" in response.json()["detail"].lower()


class TestLogin:
    """Tests for login endpoint (/auth/token)."""
    
    def test_login_success(self, client, test_customer):
        """Test that a user can log in with correct credentials."""
        # Act - Note: endpoint is /auth/token
        response = client.post(
            "/auth/token",
            json={
                "username": test_customer.username,
                "password": "CustomerPass123!",  # Matches fixture
            }
        )
        
        # Assert
        assert response.status_code == 200, f"Login failed: {response.json()}"
        
        data = response.json()
        assert data["username"] == test_customer.username
        
        # Check that cookie was set (httpOnly cookies for auth)
        assert "access_token" in response.cookies
    
    def test_login_wrong_password(self, client, test_customer):
        """Test that login fails with wrong password."""
        response = client.post(
            "/auth/token",
            json={
                "username": test_customer.username,
                "password": "WrongPassword123!",
            }
        )
        
        assert response.status_code == 401
        assert "access_token" not in response.cookies
    
    def test_login_nonexistent_user(self, client):
        """Test that login fails for non-existent user."""
        response = client.post(
            "/auth/token",
            json={
                "username": "doesnotexist",
                "password": "SomePassword123!",
            }
        )
        
        # Should be 401 Unauthorized
        assert response.status_code == 401


class TestProtectedEndpoints:
    """Tests for authentication on protected endpoints."""
    
    def test_get_me_without_auth(self, client):
        """
        Test that /auth/me requires authentication.
        
        This endpoint returns the current user's profile.
        Without logging in, it should return 401 Unauthorized.
        """
        response = client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_me_with_auth(self, client, test_customer):
        """Test that /auth/me works when logged in."""
        # First, log in via /auth/token
        login_response = client.post(
            "/auth/token",
            json={
                "username": test_customer.username,
                "password": "CustomerPass123!",
            }
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.json()}"
        
        # Now access protected endpoint (cookies are automatically sent)
        response = client.get("/auth/me")
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_customer.username
    
    def test_logout(self, client, test_customer):
        """Test that logout clears the auth cookie."""
        # Log in first via /auth/token
        login_response = client.post(
            "/auth/token",
            json={
                "username": test_customer.username,
                "password": "CustomerPass123!",
            }
        )
        assert login_response.status_code == 200
        
        # Verify we're logged in
        assert client.get("/auth/me").status_code == 200
        
        # Log out
        response = client.post("/auth/logout")
        assert response.status_code == 200
        
        # Verify we're logged out
        assert client.get("/auth/me").status_code == 401
