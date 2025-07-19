# Role-Based Access Control (RBAC) Implementation

## Overview

This document explains the RBAC implementation in the SMS backend system, which ensures proper role-based access control for frontend UI rendering.

## User Roles

The system supports the following user roles (defined in `src/enums/users.py`):

- **STUDENT**: Basic student access
- **STAFF**: Staff member access (includes student permissions)
- **ADMIN**: Administrator access (includes staff permissions)
- **SUPER_ADMIN**: Super administrator access (highest level)

## Authentication Flow

### 1. Login Process

When a user logs in via `/api/v1/user/login`:

1. **Credentials Verification**: User ID and PIN are verified
2. **Token Creation**: JWT token is created with both `user_id` and `role` information
3. **Cookie Setting**: Token is stored in HTTP-only cookie for security

```python
# Token payload structure
{
    "user_id": "1000001",
    "role": "admin",
    "exp": 1234567890
}
```

### 2. Token Verification

The system provides two token verification methods:

- `verify_token()`: Returns only user_id (legacy)
- `verify_token_with_role()`: Returns both user_id and role (recommended)

## API Endpoints

### Authentication Endpoints

#### POST `/api/v1/user/login`
- **Purpose**: Authenticate user and get access token
- **Request**: `{"user_id": "1000001", "pin": "123456"}`
- **Response**: `{"access_token": "...", "token_type": "bearer"}`

#### GET `/api/v1/user/me`
- **Purpose**: Get current user information with role and profile
- **Authentication**: Required
- **Response**: 
```json
{
    "user_id": "1000001",
    "role": "admin",
    "profile": {
        "profile_id": "uuid",
        "first_name": "John",
        "last_name": "Doe",
        "email": "john@example.com",
        // ... other profile fields
    }
}
```

### Role-Protected Endpoints

#### GET `/api/v1/user/admin-only`
- **Purpose**: Admin-only functionality example
- **Required Role**: `admin` or `super_admin`
- **Response**: User information with admin access confirmation

#### GET `/api/v1/user/staff-and-admin`
- **Purpose**: Staff and admin functionality example
- **Required Role**: `staff`, `admin`, or `super_admin`
- **Response**: User information with staff/admin access confirmation

## Frontend Integration

### 1. Login Flow

```javascript
// Frontend login example
const loginResponse = await fetch('/api/v1/user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: '1000001', pin: '123456' })
});

if (loginResponse.ok) {
    // Token is automatically stored in HTTP-only cookie
    // Redirect to dashboard or get user info
    const userInfo = await fetch('/api/v1/user/me');
    const userData = await userInfo.json();
    
    // Store user role in frontend state
    setUserRole(userData.role);
    setUserProfile(userData.profile);
}
```

### 2. Role-Based UI Rendering

```javascript
// React component example
const Dashboard = () => {
    const [userRole, setUserRole] = useState(null);
    const [userProfile, setUserProfile] = useState(null);

    useEffect(() => {
        // Get user info on component mount
        fetchUserInfo();
    }, []);

    const renderUI = () => {
        switch (userRole) {
            case 'super_admin':
                return <SuperAdminDashboard profile={userProfile} />;
            case 'admin':
                return <AdminDashboard profile={userProfile} />;
            case 'staff':
                return <StaffDashboard profile={userProfile} />;
            case 'student':
                return <StudentDashboard profile={userProfile} />;
            default:
                return <LoadingSpinner />;
        }
    };

    return (
        <div>
            <Header userRole={userRole} profile={userProfile} />
            {renderUI()}
        </div>
    );
};
```

### 3. Route Protection

```javascript
// Protected route component
const ProtectedRoute = ({ requiredRoles, children }) => {
    const [userRole, setUserRole] = useState(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        checkUserAccess();
    }, []);

    const checkUserAccess = async () => {
        try {
            const response = await fetch('/api/v1/user/me');
            if (response.ok) {
                const userData = await response.json();
                setUserRole(userData.role);
                
                if (!requiredRoles.includes(userData.role)) {
                    // Redirect to unauthorized page
                    navigate('/unauthorized');
                }
            } else {
                // Redirect to login
                navigate('/login');
            }
        } catch (error) {
            navigate('/login');
        } finally {
            setIsLoading(false);
        }
    };

    if (isLoading) return <LoadingSpinner />;
    
    return requiredRoles.includes(userRole) ? children : null;
};

// Usage
<ProtectedRoute requiredRoles={['admin', 'super_admin']}>
    <AdminPanel />
</ProtectedRoute>
```

## Backend Role Protection

### Using Predefined Dependencies

```python
from src.api.dependencies.auth import require_admin, require_staff

@router.get("/admin-endpoint")
async def admin_only_function(
    current_user_data: tuple[UserInDb, ProfileInDb] = Depends(require_admin)
):
    user, profile = current_user_data
    # Only admins can access this endpoint
    return {"message": "Admin access granted"}
```

### Using Custom Role Requirements

```python
from src.api.dependencies.auth import require_role

@router.get("/custom-role-endpoint")
async def custom_role_function(
    current_user_data: tuple[UserInDb, ProfileInDb] = Depends(require_role(["staff", "admin"]))
):
    user, profile = current_user_data
    # Only staff and admin can access this endpoint
    return {"message": "Staff/Admin access granted"}
```

## Security Features

### 1. Token Security
- JWT tokens include role information
- Tokens are stored in HTTP-only cookies
- Automatic token expiration
- Role verification on each request

### 2. Role Validation
- Server-side role verification
- Role mismatch detection
- Automatic role hierarchy enforcement

### 3. Error Handling
- 401 Unauthorized: Invalid credentials
- 403 Forbidden: Insufficient role permissions
- Proper error messages for debugging

## Database Schema

### Users Table
```sql
CREATE TABLE users (
    user_id VARCHAR(7) PRIMARY KEY,
    role VARCHAR(255) NOT NULL,
    pin_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE
);
```

### Profiles Table
```sql
CREATE TABLE profiles (
    profile_id UUID PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    -- ... other profile fields
);
```

## Testing RBAC

### 1. Test Different Roles
```bash
# Test admin login
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1000001", "pin": "123456"}'

# Test staff login
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1000002", "pin": "123456"}'

# Test student login
curl -X POST http://localhost:8000/api/v1/user/login \
  -H "Content-Type: application/json" \
  -d '{"user_id": "1000003", "pin": "123456"}'
```

### 2. Test Protected Endpoints
```bash
# Get user info (should include role)
curl -X GET http://localhost:8000/api/v1/user/me \
  -H "Cookie: access_token=your_token_here"

# Test admin-only endpoint
curl -X GET http://localhost:8000/api/v1/user/admin-only \
  -H "Cookie: access_token=your_token_here"
```

## Best Practices

### 1. Frontend
- Always check user role before rendering UI components
- Implement route protection for sensitive pages
- Store user role in application state
- Handle role changes gracefully

### 2. Backend
- Use role-based dependencies for endpoint protection
- Validate roles on every authenticated request
- Implement proper error handling for unauthorized access
- Log role-based access attempts for audit purposes

### 3. Security
- Never trust client-side role information
- Always verify roles server-side
- Use HTTP-only cookies for token storage
- Implement proper session management

## Troubleshooting

### Common Issues

1. **Role not included in token**: Ensure login endpoint includes role in token creation
2. **Frontend not receiving role**: Check `/me` endpoint returns role information
3. **Permission denied errors**: Verify user has required role for endpoint
4. **Token expiration**: Implement proper token refresh mechanism

### Debug Steps

1. Check token payload: Decode JWT token to verify role inclusion
2. Verify database role: Check user's role in database
3. Test endpoint directly: Use curl to test protected endpoints
4. Check frontend state: Verify role is properly stored in frontend 