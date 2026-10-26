ROUTES = (
    {"method": "GET", "path": "/health", "description": "Application and SQLite health"},
    {"method": "GET", "path": "/api/v1/auth/health", "description": "Authentication fixture status"},
    {"method": "POST", "path": "/api/v1/auth/validate", "description": "Validate a local demo token"},
    {"method": "GET", "path": "/api/v1/users/me", "description": "Read the bearer-token demo user"},
    {"method": "GET", "path": "/api/v1/operations/status", "description": "Operator permission example"},
    {"method": "GET", "path": "/api/v1/admin/status", "description": "Admin-only authorization example"},
    {"method": "GET", "path": "/api/v1/metrics", "description": "Read process-local request metrics"},
    {"method": "GET", "path": "/api/v1/routes", "description": "List this local gateway route table"},
    {"method": "GET", "path": "/api/v1/demo/issues", "description": "Read static ECP issue fixtures"},
)
