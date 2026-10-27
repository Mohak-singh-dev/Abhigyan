import os
import re
import sys
from sqlalchemy import create_engine, text

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app.config import settings

def sanitized_error_message(error, url):
    """Keep useful driver diagnostics while removing connection credentials/endpoints."""
    message = str(error)
    message = re.sub(r"(?i)postgres(?:ql)?(?:\+\w+)?://[^\s'\"]+", "[CONNECTION_URL]", message)
    for secret in (url.password, url.username, url.host, settings.DATABASE_URL):
        if secret:
            message = message.replace(secret, "[REDACTED]")
    message = re.sub(r"(?i)(password|passwd|pwd)\s*=\s*[^\s,]+", r"\1=[REDACTED]", message)
    message = re.sub(r"(?i)(user(?:name)?\s*=\s*)[^\s,]+", r"\1[REDACTED]", message)
    return message

def check_database_connection():
    url = settings.sqlalchemy_database_url
    if any(marker in (url.password or "") for marker in ("YOUR-PASSWORD",)) or any(marker in (url.host or "") for marker in ("YOUR-SUPABASE-HOST", "YOUR-POOLER-HOST")):
        print("STATUS: PLACEHOLDER_DETECTED")
        print("Set DATABASE_URL in backend/.env to the connection string from your Supabase project's Connect dialog.")
        sys.exit(2)

    print("Checking configured Supabase PostgreSQL connection (endpoint details withheld)...")

    try:
        target_engine = create_engine(url, pool_pre_ping=True)
        with target_engine.connect() as connection:
            version = connection.execute(text("SELECT version();")).scalar()
            connection.execute(text("SELECT 1;"))
            print("SUCCESS: Connected to Supabase PostgreSQL.")
            print(f"PostgreSQL Version: {version}")
            return True

    except Exception as e:
        # Diagnose common connection failures without printing driver messages,
        # which can contain usernames or connection details.
        original = getattr(e, "orig", e)
        err_msg = str(original).lower()
        if isinstance(e, ModuleNotFoundError) or isinstance(original, ModuleNotFoundError):
            print("ERROR: PostgreSQL driver dependency is missing. Install backend/requirements.txt.")
        elif "password authentication failed" in err_msg or "invalid authorization specification" in err_msg:
            print("ERROR: Supabase rejected database authentication. Check the locally configured credentials and URL-encode reserved password characters.")
        elif "server does not support ssl" in err_msg:
            print("ERROR: The configured endpoint does not support SSL. The connection resolved to local IPv6 loopback (::1), so it is not reaching a remote Supabase Session Pooler.")
            print("Keep SSL enabled and replace DATABASE_URL in backend/.env with the exact Session pooler connection string from Supabase > Connect.")
        elif "ssl" in err_msg and any(word in err_msg for word in ("certificate", "verify", "encryption", "sslmode")):
            print("ERROR: TLS/SSL negotiation failed. Supabase connections require SSL; verify the connection string's SSL mode and certificate settings.")
        elif "could not translate host name" in err_msg or "name or service not known" in err_msg or "getaddrinfo failed" in err_msg:
            print("ERROR: DNS could not resolve the configured database host. Verify the copied Supabase endpoint and network DNS access.")
        elif "timeout" in err_msg or "timed out" in err_msg:
            print("ERROR: The database connection timed out. Check network access and the selected Supabase connection endpoint.")
        elif "connection refused" in err_msg or "could not connect to server" in err_msg:
            print("ERROR: The database endpoint refused the connection. Verify the copied Supabase port and network access.")
        elif "too many clients" in err_msg or "remaining connection slots" in err_msg:
            print("ERROR: Supabase refused the connection because the database connection limit was reached.")
        elif "does not exist" in err_msg and "database" in err_msg:
            print("ERROR: The configured database name does not exist in Supabase. Check the database name in the copied connection string.")
        else:
            code = getattr(original, "pgcode", None)
            suffix = f" (PostgreSQL error code {code})" if code else ""
            detail = sanitized_error_message(original, url)
            print(f"ERROR: Supabase database check failed with {type(original).__name__}{suffix}.")
            print(f"Safe driver detail: {detail}")
        sys.exit(1)

if __name__ == "__main__":
    check_database_connection()
