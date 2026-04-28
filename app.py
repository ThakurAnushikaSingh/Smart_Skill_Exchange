# Main app entrypoint - updated to trigger reload
from __init__ import create_app
import os

print("DEBUG SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("DEBUG SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
