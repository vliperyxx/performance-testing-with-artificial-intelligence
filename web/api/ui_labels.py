TEST_TYPE_LABELS = {
    "load": "Навантажувальне тестування",
    "stress": "Стрес-тестування",
    "spike": "Спайк-тестування",
    "endurance": "Тестування на витривалість",
    "scalability": "Тестування масштабованості",
}

MODEL_LABELS = {
    "openai": "GPT-5.4 (OpenAI)",
    "anthropic": "Claude Sonnet 4.6 (Anthropic)",
    "gemini": "Gemini 3.1 Pro Preview (Google)",
}

TOOL_LABELS = {
    "k6": "Grafana K6",
    "locust": "Locust",
    "jmeter": "Apache JMeter",
    "gatling": "Gatling",
}

ENDPOINT_LABELS = {
    "register": "Реєстрація нового користувача",
    "login": "Авторизація користувача",
    "create_transaction": "Створення нової транзакції",
    "get_transactions": "Отримання транзакцій",
    "get_summary": "Отримання балансу користувача",
    "create_goal": "Створення нової фінансової цілі",
    "get_goals": "Отримання фінансових цілей",
    "update_goal": "Оновлення фінансової цілі",
}

SCENARIO_LABELS = {
    "new_user_onboarding": "Ознайомлення нового користувача з функціоналом системи",
    "account_overview": "Огляд особистого кабінету",
    "daily_expense_tracking": "Облік щоденних витрат",
    "goal_progress_review": "Перевірка прогресу фінансових цілей",
    "regular_session": "Звичайна сесія користувача",
}

LOAD_SETUP_LABELS = {
    "default": "Використати стандартні параметри",
    "manual": "Вказати параметри вручну",
    "ai": "Згенерувати параметри за допомогою ШІ",
}

TARGET_TYPE_LABELS = {
    "endpoint": "Кінцева точка (Endpoint)",
    "flow": "Сценарій користувача (User Flow)",
}