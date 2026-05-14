from main import app
import json
print(json.dumps(app.openapi()["components"]["schemas"]["Body_upload_file_upload__post"], indent=2))
