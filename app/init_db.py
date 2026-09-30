"""Initialize the configured database schema for a fresh deployment."""
import app.main as m
m.Base.metadata.create_all(m.engine)
print("ReconAI database schema initialized.")
