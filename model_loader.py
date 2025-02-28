from roboflow import Roboflow
import os

# Create directories if they don't exist
os.makedirs("models/images", exist_ok=True)
os.makedirs("models/visualizations", exist_ok=True)
os.makedirs("static/images/results", exist_ok=True)

# Initialize Roboflow for classification model
rf1 = Roboflow(api_key="OMK13lODzeEz6X1NFfoF")
project1 = rf1.workspace().project("leaf-classification-0gekz")
modelClassification = project1.version(1).model

# Initialize Roboflow for identification model 
rf2 = Roboflow(api_key="kVjiNm6VQczdBaSdhwOg")
project2 = rf2.workspace().project("healthy_pest_disease")
modelIdentification = project2.version(1).model