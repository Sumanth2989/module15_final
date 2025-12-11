"""
This module previously exported login/register routes that conflicted with the
application's main HTML router. Those handlers have been consolidated into
`app/schemas/user.py` (HTML) and `app/routers/users.py` (API). To avoid
duplicate routes and ambiguous behavior, this module intentionally exposes no
routes at top-level.

If you want namespaced auth endpoints later, add them under a prefix such as
`/auth` to avoid colliding with the site's public `/login` and `/register`.
"""

from fastapi import APIRouter

router = APIRouter()