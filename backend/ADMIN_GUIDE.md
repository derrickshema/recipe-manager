# System Administration Guide

## Overview
This document explains how system administrators are created and what they can do in the Recipe Manager application.

## How System Admins are Created

### Real-World Pattern
In production applications like Microsoft Azure, Paycom, or Salesforce:
1. **Initial admin** is created during system setup (not through public registration)
2. **Subsequent admins** are created by existing admins through protected endpoints
3. **Never** through public-facing registration forms

### Our Implementation

#### Step 1: Create Initial Superadmin (One-Time Setup)

Run this command after setting up your database:

```bash
cd backend
python create_superadmin.py
```

**For production**, use environment variables:
```bash
export SUPERADMIN_USERNAME="your_admin"
export SUPERADMIN_PASSWORD="strong_password_here"
export SUPERADMIN_EMAIL="admin@yourcompany.com"
python create_superadmin.py
```

#### Step 2: Additional Admins (Future Feature)

In the future, you can add an endpoint for superadmins to create other superadmins:
- `POST /admin/users/create-superadmin` (requires existing superadmin authentication)

## Superadmin Permissions

### ✅ What Superadmins CAN Do

1. **User Management (View Only)**
   - View all users in the system
   - View user details (name, email, role)
   - Suspend/unsuspend user accounts
   - View user activity logs (future feature)

2. **Restaurant Approval Workflow**
   - View all restaurants (pending, approved, rejected, suspended)
   - **Approve** restaurant registrations
   - **Reject** restaurant registrations (with reason)
   - **Suspend** restaurants for policy violations

3. **System Oversight**
   - View dashboard statistics
   - Monitor system health
   - Generate reports

4. **User Support**
   - Help users reset passwords (future: generate reset tokens)
   - Resolve account access issues
   - Handle customer support tickets

### ❌ What Superadmins CANNOT Do

1. **Cannot Alter User Data**
   - Cannot edit user's personal info (name, email, phone)
   - Users must update their own profiles

2. **Cannot Manage Restaurant Operations**
   - Cannot edit restaurant menus
   - Cannot create/edit recipes on behalf of restaurants
   - Cannot add/remove restaurant staff
   - Cannot process orders

3. **Cannot Access Restaurant Private Data**
   - Cannot view restaurant's financial information
   - Cannot access proprietary recipes or trade secrets
   - Restaurant owners maintain full control of their data

## Permission Model Summary

| Action | Customer | Restaurant Owner | Superadmin |
|--------|----------|-----------------|-----------|
| Browse restaurants | ✅ | ✅ | ✅ View all |
| Place orders | ✅ | ❌ | ❌ |
| Edit own profile | ✅ | ✅ | ✅ |
| Create restaurant | ❌ | ✅ | ❌ |
| Edit restaurant data | ❌ | ✅ Own only | ❌ |
| Manage restaurant staff | ❌ | ✅ Own only | ❌ |
| Approve restaurants | ❌ | ❌ | ✅ |
| Suspend users | ❌ | ❌ | ✅ |
| View all users | ❌ | ❌ | ✅ |

## Restaurant Registration Flow

### Current Flow
1. Restaurant owner registers via `/register/restaurant`
2. Account created with `approval_status: PENDING`
3. Owner can log in but restaurant is not visible to customers
4. **Superadmin reviews and approves/rejects**
5. Once approved, restaurant appears in customer listings

### API Endpoints for Admins

```
GET  /admin/restaurants/pending          # List pending restaurants
GET  /admin/restaurants?approval_status=approved  # Filter by status
PATCH /admin/restaurants/{id}/approve    # Approve restaurant
PATCH /admin/restaurants/{id}/reject     # Reject restaurant
PATCH /admin/restaurants/{id}/suspend    # Suspend restaurant

GET  /admin/users                        # List all users
GET  /admin/users?role=customer          # Filter by role
PATCH /admin/users/{id}/suspend          # Suspend user
PATCH /admin/users/{id}/unsuspend        # Unsuspend user

GET  /admin/stats                        # Dashboard statistics
```

## Password Reset Flow (Future Enhancement)

### User Self-Service (Primary)
1. User clicks "Forgot Password"
2. Enters email address
3. Receives reset link via email
4. Clicks link and sets new password

### Admin Assistance (Rare Cases)
1. User contacts support ("I lost access to my email")
2. Admin verifies user identity (security questions, ID verification)
3. Admin generates one-time reset token
4. Admin securely sends token to user via verified channel
5. User uses token to reset password

**Note**: Admin never sees or sets user's actual password - only generates secure reset tokens.

## Security Best Practices

1. **Never expose superadmin creation via public endpoints**
2. **Use environment variables for initial admin credentials**
3. **Require strong passwords for admin accounts**
4. **Enable 2FA for admin accounts (future)**
5. **Log all admin actions for audit trail (future)**
6. **Limit number of superadmin accounts**
7. **Regular review of admin access**

## Next Steps

To implement the full admin panel:
1. ✅ Backend routes created (`admin_routes.py`)
2. ✅ Bootstrap script created (`create_superadmin.py`)
3. ⏳ Create frontend admin dashboard UI
4. ⏳ Implement password reset functionality
5. ⏳ Add audit logging for admin actions
6. ⏳ Add email notifications for approval/rejection

## Testing the Admin System

```bash
# 1. Create superadmin
python create_superadmin.py

# 2. Login as superadmin
curl -X POST http://localhost:8000/auth/token \
  -d "username=admin&password=admin123"

# 3. Use token to access admin endpoints
curl -X GET http://localhost:8000/admin/restaurants/pending \
  -H "Authorization: Bearer YOUR_TOKEN"

# 4. Approve a restaurant
curl -X PATCH http://localhost:8000/admin/restaurants/1/approve \
  -H "Authorization: Bearer YOUR_TOKEN"
```
