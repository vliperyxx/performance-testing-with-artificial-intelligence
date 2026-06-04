MODELS = {
     "openai": {
       "name": "gpt-5.4",
       "provider": "openai"
    },
    "anthropic": {
       "name": "claude-sonnet-4-6",
       "provider": "anthropic"
    },
    "gemini": {
        "name": "gemini-3.1-pro-preview",
        "provider": "gemini"
    }
}

PERFORMANCE_TOOLS = ["k6", "locust", "jmeter", "gatling"]

TEST_TYPES = {
    "load": {
        "virtual_users": 50,
        "duration": "5m",
        "ramp_up": "30s",
        "description": "normal expected traffic during typical usage hours"
    },
    "stress": {
        "virtual_users": 200,
        "duration": "10m",
        "ramp_up": "1m",
        "description": "beyond normal capacity to find breaking points"
    },
    "spike": {
        "virtual_users": 500,
        "duration": "1m",
        "ramp_up": "5s",
        "description": "sudden burst of users"
    },
    "endurance": {
        "virtual_users": 30,
        "duration": "30m",
        "ramp_up": "2m",
        "description": "moderate sustained load to detect memory leaks and gradual degradation"
    },
    "scalability": {
        "virtual_users": 200,
        "duration": "10m",
        "ramp_up": "8m",
        "description": "gradual user increase to identify scaling thresholds"
    }
}

BASE_URL = "http://localhost:3000"

TEST_USER_IDS = [
    "1bf26f16-294f-495f-b9ac-c9f058c472c3",
    "4d745ac0-1b28-47a7-b952-1440786b0ef9",
    "e8a629aa-ab8f-41a8-bbe3-ef70de953e20",
    "d60ca496-b28e-42c0-8159-ec7010abf309",
    "3ccbdaa9-262d-4303-8c72-b910c35aaf3a",
    "233ce134-36e3-456f-95d1-726494083aae",
    "593ac756-83a0-41f1-90d8-dec0d1b46e09",
    "ac194f81-f77f-4929-9fea-13aff15f8cde",
    "bc33bc5a-5358-407d-a826-55b84e75724c",
    "6e56b126-bf5f-4177-80e5-f6122a894590",
    "aa2297bb-ead9-4323-b817-59a9eed8953d",
    "ff283a92-4cae-4346-b044-e799fd88c6db",
    "c68da683-6bdb-4982-96ad-f2565132be6c",
    "e7aef6e5-6b2d-4145-9f7a-565bcff8812a",
    "a3a330ff-fc16-46c0-8448-11b5c01a2dac",
    "90de87f1-d135-47fe-8040-e327c9f2ab07",
    "9dc67642-b420-4ecf-a2a5-7a970cfd6b11",
    "59365172-d9ca-4d74-9b94-6896e154952e",
    "316276f7-cc1b-4a34-bbbf-99aeec3eaf8d",
    "41b81a27-72de-4c07-85ea-87b1816cd6f6"
]

TEST_GOAL_IDS = [
    "554afd52-da05-40b5-9ceb-da704f94195f",
    "3f36f92c-a6d0-4499-b9b0-5791317fe516",
    "9d88d3f5-2e2d-4553-a9c3-ecf9f57bcc02",
    "32e6dd6d-564e-489f-923d-cc167668ad5b",
    "ffed77cb-5c0b-4bab-b9f8-3d0edc6ff683",
    "6efed2a0-1881-41d7-bf09-0aac683d5784",
    "41fe6e6e-af8d-4e5e-bf0f-ac3311499873",
    "ffaa4338-e5f4-4288-9ea0-a39afd0baac7",
    "ac78528c-6c3d-430f-9db6-b1967e5ed081",
    "0c0b1a41-703d-4183-838a-06f53d332610"
]

TEST_USER_EMAILS = [
    "test1745105728677@example.com",
    "test1745105867122@example.com",
    "test1745106017495@example.com",
    "test1745202843695@example.com",
    "test1745203188239@example.com",
    "test1745208155465@example.com",
    "test1745208403538@example.com",
    "test1745208862854@example.com",
    "test1745208965134@example.com",
    "test1745237301007@example.com",
    "test1745237395962@example.com",
    "test1745237496666@example.com",
    "test1745237741044@example.com",
    "testuser+094e208a@example.com",
    "test1745237909998@example.com",
    "testuser+8645ed20@example.com"
]

MODEL_ROLE = "You are a performance testing engineer who writes load test scripts for HTTP APIs."
ANALYST_ROLE = "You are a performance testing analyst who reviews test results and explains them clearly."

API_CONTEXT = "Personal Finance Accounting System."

ENDPOINTS = {
    "register": {
        "method": "POST",
        "path": "/users/register",
        "body": {
            "username": "testuser_omelnychuk",
            "email": "testuser_omelnychuk@example.com",
            "password": "perf_test5836"
        },
        "response": {
            "accessToken": "eyJhb...",
            "refreshToken": "eyJhb..."
        },
        "expected_status": 201,
        "unique_fields": ["username", "email"],
        "description": "Register a new user account"
    },
    "login": {
        "method": "POST",
        "path": "/users/login",
        "body": {
            "email": "test1745105728677@example.com",
            "password": "perf_test5836"
        },
        "response": {
            "accessToken": "eyJhb...",
            "refreshToken": "eyJhb...",
            "userId": "uuid-string"
        },
        "expected_status": 201,
        "description": "Login and receive JWT tokens"
    },
    "create_transaction": {
        "method": "POST",
        "path": "/transactions",
        "body": {
            "user_id": "{userId}",
            "amount": 1487.50,
            "type": "income",
            "category": "salary",
            "description": "April salary deposit",
            "transaction_date": "2026-04-27T12:28:45Z"
        },
        "response": {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "amount": 1487.50,
            "type": "income",
            "category": "salary",
            "description": "April salary deposit",
            "transaction_date": "2026-04-27T12:28:45Z",
            "created_at": "2026-04-27T12:28:45Z"
        },
        "expected_status": 201,
        "unique_fields": ["description", "transaction_date"],
        "description": "Create a new income or expense transaction"
    },
    "get_transactions": {
        "method": "GET",
        "path": "/transactions/{userId}",
        "body": None,
        "response": [{"id": "uuid", "amount": 1487.50, "type": "income", "category": "salary"}],
        "expected_status": 200,
        "description": "Get list of user transactions"
    },
    "get_summary": {
        "method": "GET",
        "path": "/transactions/{userId}/summary",
        "body": None,
        "response": {"income": 1487.50, "expense": 0},
        "expected_status": 200,
        "description": "Get income and expense summary for user"
    },
    "create_goal": {
        "method": "POST",
        "path": "/goals",
        "body": {
            "user_id": "{userId}",
            "goal_name": "Trip to Carpathians",
            "target_amount": 2500,
            "deadline": "2026-06-23T00:00:00Z"
        },
        "response": {
            "id": "uuid-string",
            "user_id": "uuid-string",
            "goal_name": "Trip to Carpathians",
            "target_amount": 2500,
            "current_amount": "0",
            "deadline": "2026-06-23T00:00:00Z",
            "status": "in_progress",
            "created_at": "2026-05-02T03:25:33.605Z"
        },
        "expected_status": 201,
        "unique_fields": ["goal_name"],
        "description": "Create a new financial goal"
    },
    "get_goals": {
        "method": "GET",
        "path": "/goals/{userId}",
        "body": None,
        "response": [{"id": "uuid", "goal_name": "Trip to Carpathians", "target_amount": 2500}],
        "expected_status": 200,
        "description": "Get list of user goals"
    },
    "update_goal": {
        "method": "PUT",
        "path": "/goals/{goalId}",
        "body": {
            "current_amount": 290,
            "status": "in_progress"
        },
        "response": {
            "id": "uuid-string",
            "current_amount": 290,
            "status": "in_progress"
        },
        "expected_status": 200,
        "description": "Update goal progress"
    }
}

SCENARIOS = {
    "new_user_onboarding": {
        "description": "New user registers, logs in, adds first transaction and creates first goal",
        "steps": [
            {
                "action": "register",
                "endpoint": "register",
                "note": "Register a new account for this virtual user"
            },
            {
                "action": "login",
                "endpoint": "login",
                "extract": ["userId"],
                "note": "Login with the unique email generated during the register step. Password stays as in the body."
            },
            {
                "action": "create_transaction",
                "endpoint": "create_transaction",
                "use_from_previous": ["userId"],
                "note": "Create initial income transaction (category: salary)"
            },
            {
                "action": "create_goal",
                "endpoint": "create_goal",
                "use_from_previous": ["userId"],
                "note": "Create first financial goal"
            }
        ]
    },

    "account_overview": {
        "description": "User logs in and reviews their dashboard, recent transactions and goals",
        "steps": [
            {
                "action": "login",
                "endpoint": "login",
                "extract": ["userId"],
                "note": "Login to access account data"
            },
            {
                "action": "get_summary",
                "endpoint": "get_summary",
                "use_from_previous": ["userId"],
                "note": "View account dashboard"
            },
            {
                "action": "get_transactions",
                "endpoint": "get_transactions",
                "use_from_previous": ["userId"],
                "note": "View list of recent transactions"
            },
            {
                "action": "get_goals",
                "endpoint": "get_goals",
                "use_from_previous": ["userId"],
                "note": "View active, completed and failed goals"
            }
        ]
    },

    "daily_expense_tracking": {
        "description": "User logs in and tracks daily expenses: groceries in the morning, entertainment and transport in the evening, then checks remaining balance",
        "steps": [
            {
                "action": "login",
                "endpoint": "login",
                "extract": ["userId"],
                "note": "Login to start tracking expenses"
            },
            {
                "action": "log_groceries_expense",
                "endpoint": "create_transaction",
                "use_from_previous": ["userId"],
                "note": "Add expense transaction for groceries shopping (category: groceries)"
            },
            {
                "action": "log_entertainment_expense",
                "endpoint": "create_transaction",
                "use_from_previous": ["userId"],
                "note": "Add expense transaction for cinema visit (category: entertainment)"
            },
            {
                "action": "log_transport_expense",
                "endpoint": "create_transaction",
                "use_from_previous": ["userId"],
                "note": "Add expense transaction for taxi ride home (category: transport)"
            },
            {
                "action": "get_summary",
                "endpoint": "get_summary",
                "use_from_previous": ["userId"],
                "note": "Check remaining balance after the day's spendings"
            }
        ]
    },

    "goal_progress_review": {
        "description": "User reviews all goals, funds one of them, then checks the updated balance",
        "steps": [
            {
                "action": "login",
                "endpoint": "login",
                "extract": ["userId"],
                "note": "Login to review financial goals"
            },
            {
                "action": "get_goals",
                "endpoint": "get_goals",
                "use_from_previous": ["userId"],
                "note": "Review the full list of active, completed and failed goals"
            },
            {
                "action": "fund_goal",
                "endpoint": "update_goal",
                "use_from_previous": ["userId"],
                "note": "Add money to one active goal by updating its current_amount"
            },
            {
                "action": "check_balance",
                "endpoint": "get_summary",
                "use_from_previous": ["userId"],
                "note": "Check the updated balance after funding the goal"
            }
        ]
    },

    "regular_session": {
        "description": "User performs a typical session: checks balance, browses past transactions, adds a new expense and a new financial goal, then reviews the goals list",
        "steps": [
            {
                "action": "login",
                "endpoint": "login",
                "extract": ["userId"],
                "note": "Login to start the session"
            },
            {
                "action": "check_balance",
                "endpoint": "get_summary",
                "use_from_previous": ["userId"],
                "note": "Check current account balance"
            },
            {
                "action": "review_past_transactions",
                "endpoint": "get_transactions",
                "use_from_previous": ["userId"],
                "note": "Browse the full list of transactions"
            },
            {
                "action": "log_new_expense",
                "endpoint": "create_transaction",
                "use_from_previous": ["userId"],
                "note": "Add a new expense transaction (category: utilities)"
            },
            {
                "action": "set_new_goal",
                "endpoint": "create_goal",
                "use_from_previous": ["userId"],
                "note": "Create a new financial goal"
            },
            {
                "action": "review_goals",
                "endpoint": "get_goals",
                "use_from_previous": ["userId"],
                "note": "Review all active, completed and failed goals after adding the new one"
            }
        ]
    }
}

