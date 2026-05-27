class TenantNotFoundError(Exception):
    def __init__(self, identifier: str):
        super().__init__(f"Tenant not found: {identifier}")


class TenantAlreadyExistsError(Exception):
    def __init__(self, short_name: str):
        super().__init__(f"Tenant with short_name '{short_name}' already exists")


class UserNotFoundError(Exception):
    def __init__(self, identifier: str):
        super().__init__(f"User not found: {identifier}")


class UserAlreadyExistsError(Exception):
    def __init__(self, email: str):
        super().__init__(f"User with email '{email}' already exists")
