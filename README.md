# multitenant-ai-platform


  ---
  What was created / changed
  
  src/exceptions.py (new)
  Domain exceptions for both tenant and user sides. The API layer catches these and maps them to the right HTTP status — 409 Conflict for duplicates, 404 Not Found for missing records. Neither the service nor the repo ever
  import FastAPI.

  src/repository/tenant_repository.py (new)
  All SQL lives here and nowhere else. TenantService never calls select(), db.add(), or db.commit() — it only calls self._repo.* methods. This is the core of encapsulation: the DB layer is hidden behind a clean interface.

  src/service/tenant_manager.py (rewritten)
  TenantService.__init__ now takes a TenantRepository, not a raw AsyncSession. Business logic (duplicate check, API key generation, short_name mismatch guard) lives here and only here.

  src/api/tenant.py (rewritten)
  get_tenant_service() is the single FastAPI dependency factory — it wires db → TenantRepository → TenantService. Each endpoint receives a ready-made TenantService, catches only the specific domain exception it expects, and
  returns a proper HTTP status code (201 for create, 404 vs 409 instead of a blanket 400).

  src/schemas/tenant_schemas.py (fixed)
  - UpdateTenantRequest.expiry_date is now datetime (was str) with the same validator
  - ListTenantRequest.orderBy is Literal["asc", "desc"] — Pydantic rejects anything else at the boundary before it ever reaches the DB

  ---
  When you implement the user side, you can follow the exact same pattern: UserRepository in src/repository/user_repository.py, reuse the UserAlreadyExistsError / UserNotFoundError already in src/exceptions.py, and wire it
  via a get_auth_service() dependency in src/api/auth.py.