import os

# Define the folder structure
folders = [
    "static/css",
    "static/js",
    "static/images",
    "templates",
    "models/images",
    "models/visualizations"
]

files = [
    "static/css/style.css",
    "static/js/script.js",
    "templates/index.html",
    "templates/result.html",
    "app.py",
    "model_loader.py",
    "requirements.txt",
    "README.md"
]

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create empty files
for file in files:
    with open(file, "w") as f:
        pass

print("Project structure created successfully! ✅")
