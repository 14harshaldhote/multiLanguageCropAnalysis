from flask import Flask, request, jsonify, render_template, url_for, redirect
from flask_restful import Resource, Api
from googletrans import Translator
import os
import uuid
import json
from model_loader import modelClassification, modelIdentification

# Ensure required directories exist
os.makedirs("models/images", exist_ok=True)
os.makedirs("models/visualizations", exist_ok=True)
os.makedirs("static/images/results", exist_ok=True)

app = Flask(__name__)
api = Api(app)

def get_classification_class(model, image_path):
    try:
        # Check if the image file exists
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")
        
        # Call the model's predict method and get the output as a dictionary
        prediction = model.predict(image_path, confidence=40, overlap=30)
        output = prediction.json()
        print("image path in classification function: ", image_path)
        
        # Get the value of the 'class' field from the output dictionary
        if 'predictions' in output and len(output['predictions']) > 0:
            class_value = output['predictions'][-1]['class']
        else:
            return None, None

        # Generate a unique filename for saving the visualization image
        filename = str(uuid.uuid4()) + '.jpg'
        visualization_path = os.path.join("models/visualizations", filename)

        # Visualize the prediction and save the image
        prediction.save(visualization_path)

        # Also save a copy to static folder for web display
        web_vis_path = os.path.join("static/images/results", filename)
        prediction.save(web_vis_path)

        # Return the classification class and visualization path
        return class_value, visualization_path, filename
    except Exception as e:
        # Handle the exception and return None
        print(f"Exception 1: An error occurred in classification: {str(e)}")
        return None, None, None


def get_identification_class(model, image_path):
    try:
        # Check if the image file exists
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"Image file not found: {image_path}")

        # Call the model's predict method and get the output as a dictionary
        prediction = model.predict(image_path, confidence=40, overlap=30)
        output = prediction.json()

        # Check if predictions array is empty
        if 'predictions' in output and len(output['predictions']) > 0:
            # Get the value of the 'class' field from the output dictionary
            class_value = output['predictions'][-1]['class']
        else:
            # Set class_value as null if predictions array is empty
            class_value = None

        # Generate a unique filename for saving the visualization image
        filename = str(uuid.uuid4()) + '.jpg'
        visualization_path = os.path.join("models/visualizations", filename)
        
        # Visualize the predictions and save the image
        prediction.save(visualization_path)
        
        # Also save a copy to static folder for web display
        web_vis_path = os.path.join("static/images/results", filename)
        prediction.save(web_vis_path)
        
        # Return the value of the 'class' field and visualization path
        return class_value, visualization_path, filename
    except Exception as e:
        # Handle the exception and return None
        print(f"Exception 2: An error occurred in identification: {str(e)}")
        return None, None, None


def runapp(image_path):
    # Get the predicted class values and visualization paths
    class1_value, visualization_path1, filename1 = get_classification_class(modelClassification, image_path)

    if class1_value and class1_value != 'healthy':
        class2_value, visualization_path2, filename2 = get_identification_class(modelIdentification, visualization_path1)

        # Print the predicted class values
        print("Classification class:", class1_value)
        print("Identification class:", class2_value)
        if class2_value is None:
            return class1_value, visualization_path1, filename1

        return class2_value, visualization_path2, filename2
    else:
        # Print the predicted class values if available
        if class1_value:
            print("Classification class:", class1_value)
            return class1_value, visualization_path1, filename1
        else:
            return None, None, None


def delete_image_file(file_path):
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print("Deleted image file:", file_path)
        else:
            print("Image file not found:", file_path)
    except Exception as e:
        print(f"Exception 3: An error occurred while deleting image file {file_path}: {str(e)}")


# API Resources
class ImageUpload(Resource):
    def post(self):
        if 'image' not in request.files:
            response = jsonify({'result': 'failure', 'message': 'No image provided'})
            response.status_code = 400
            return response

        image = request.files['image']
        if image.filename == '':
            response = jsonify({'result': 'failure', 'message': 'No image selected'})
            response.status_code = 400
            return response

        try:
            if image and image.filename.lower().endswith(('.jpg', '.png', '.jpeg')):
                # Generate a unique filename for saving the image
                filename = str(uuid.uuid4()) + '.jpg'
                image_path = os.path.join("models/images", filename)
                print("image_path :: ", image_path)
                image.save(image_path)

                res, visualization_path, vis_filename = runapp(image_path)
                print("visualization_path :: ", visualization_path)

                # Initialize default values
                cause = "NULL"
                prevention = "NULL"
                solution = "NULL"

                # Try to delete input file if it exists
                if image_path:
                    delete_image_file(image_path)

                if not res:
                    response = jsonify({'result': 'failure', 'message': 'Could not classify the image'})
                    response.status_code = 400
                    return response

                # Disease information dictionary
                disease_info = {
                    "Target spot": {
                        "cause": "Target spot, or Corynespora leaf spot, is a fungal disease affecting various crops like tomatoes, soybeans, and cotton. It is caused by the fungus Corynespora cassiicola.",
                        "prevention": "Farmers can prevent target spot by planting resistant cultivars, practicing crop rotation, and ensuring proper plant spacing for good air circulation.",
                        "solution": "Manage target spot disease on tomato leaves by pruning infected foliage, improving air circulation, practicing proper watering at the base, using mulch, implementing crop rotation, considering fungicides if necessary, and monitoring plant health."
                    },
                    "Leaf mold": {
                        "cause": "Leaf mold is primarily caused by a fungus called Fulvia fulva (formerly Cladosporium fulvum). It thrives in warm, humid conditions.",
                        "prevention": "To prevent leaf mold, farmers can use resistant varieties, practice crop rotation, ensure proper plant spacing for good air circulation, and avoid overhead irrigation.",
                        "solution": "If leaf mold occurs, farmers should remove and destroy infected plant material. Fungicides can be applied preventatively, but they should be used judiciously and as part of an integrated disease management strategy."
                    },
                    "Late blight": {
                        "cause": "Late blight is a devastating disease affecting several crops, most notably tomatoes and potatoes. It is caused by a fungus-like oomycete pathogen called Phytophthora infestans. It spreads rapidly under cool, wet conditions.",
                        "prevention": "Farmers can prevent late blight by planting resistant varieties, practicing good sanitation, providing adequate plant spacing for airflow, and avoiding overhead irrigation.",
                        "solution": "If late blight occurs, farmers should promptly remove and destroy infected plants. Fungicides can be used preventatively, especially during periods of high disease pressure. Early detection and action are critical to managing this disease."
                    },
                    "Curl virus": {
                        "cause": "Curl leaf, also known as leaf curl, is commonly caused by viral infections such as Tomato leaf curl virus or Peach leaf curl virus. It is often spread by insect vectors, particularly whiteflies.",
                        "prevention": "Farmers can prevent curl leaf by using disease-resistant varieties, controlling insect populations through integrated pest management (IPM) practices, and employing physical barriers such as nets or row covers.",
                        "solution": "Once curl leaf is established, there are no specific curative treatments. Infected plants should be removed and destroyed to prevent further spread. Future plantings should be carefully monitored for symptoms."
                    },
                    "Spider mites": {
                        "cause": "Spider mites are tiny arachnids that infest a wide range of crops, including fruits, vegetables, and ornamental plants. They pierce plant tissues and feed on sap, causing damage.",
                        "prevention": "Farmers can prevent spider mite infestations by practicing good crop hygiene, providing adequate moisture levels, promoting beneficial insects that prey on mites, and using reflective mulches.",
                        "solution": "In case of spider mite infestations, farmers can employ biological controls like predatory mites or insecticidal soaps. If necessary, selective insecticides can be used, following proper application guidelines."
                    },
                    "Mosaic virus": {
                        "cause": "Mosaic viruses are a group of viruses that affect a wide range of crops, including tomatoes, cucumbers, peppers, and many others. They are mainly transmitted through infected plant sap, insects, or contaminated tools.",
                        "prevention": "Farmers can prevent mosaic virus by using virus-free seeds or transplants, practicing strict sanitation measures, controlling insect vectors, and removing and destroying infected plants.",
                        "solution": "Unfortunately, there are no effective treatments for mosaic viruses once plants are infected. Therefore, prevention is crucial in managing this disease."
                    }
                }

                # Set information based on detected class
                if res in disease_info:
                    cause = disease_info[res]["cause"]
                    prevention = disease_info[res]["prevention"]
                    solution = disease_info[res]["solution"]
                    return jsonify({
                        "result": res,
                        "message": {
                            "cause": cause,
                            "prevention": prevention,
                            "solution": solution,
                        },
                        "image": vis_filename
                    })
                elif res == "healthy" or res == "healthy leaf":
                    return jsonify({
                        'result': res, 
                        'message': 'Your crop leaf is in healthy condition. However, to maintain this, ensure to follow good agricultural practices.',
                        'image': vis_filename
                    })
                elif res == "disease":
                    return jsonify({
                        'result': res, 
                        'message': 'Your crop leaf has disease symptoms, but the specific disease could not be identified.',
                        'image': vis_filename
                    })
                else:
                    return jsonify({
                        'result': res, 
                        'message': 'Your crop is in an identified condition. Please consult with a local agricultural expert.',
                        'image': vis_filename
                    })
            else:
                response = jsonify({'result': 'failure', 'message': 'Invalid file format. Please upload a JPG, PNG or JPEG image.'})
                response.status_code = 400
                return response
        except Exception as e:
            error_message = f"Exception 4: An exception occurred in Image Upload: {str(e)}"
            response = jsonify({'result': 'failure', 'message': error_message})
            response.status_code = 500
            return response


def translate_json_values(json_data, target_language):
    translator = Translator()
    
    def translate_value(value):
        try:
            if isinstance(value, str) and value != "NULL":
                return translator.translate(value, dest=target_language).text
            return value
        except Exception as e:
            print(f"Translation error: {str(e)}")
            return value
    
    if isinstance(json_data, dict):
        translated_data = {}
        for key, value in json_data.items():
            if isinstance(value, (dict, list)):
                translated_data[key] = translate_json_values(value, target_language)
            else:
                translated_data[key] = translate_value(value)
        return translated_data
    elif isinstance(json_data, list):
        translated_data = []
        for item in json_data:
            translated_data.append(translate_json_values(item, target_language))
        return translated_data
    else:
        return json_data


# Base class for translated responses
class TranslatedImageUpload(Resource):
    def __init__(self, language):
        self.language = language
        
    def post(self):
        try:
            # Get the response from the base ImageUpload class
            response = ImageUpload().post()
            
            # If status code is 200, translate the response
            if hasattr(response, 'status_code') and response.status_code == 200:
                response_data = response.get_json()
                translated_response_data = translate_json_values(response_data, self.language)
                return jsonify(translated_response_data)
            else:
                return response
        except Exception as e:
            error_message = f"Exception: Translation error: {str(e)}"
            response = jsonify({'result': 'failure', 'message': error_message})
            response.status_code = 500
            return response


# Register API resources
api.add_resource(ImageUpload, '/api/upload')
# Do this instead - provide a unique endpoint name for each route:
api.add_resource(TranslatedImageUpload, '/api/upload/hindi', endpoint='hindi_upload', resource_class_args=('hi',))
api.add_resource(TranslatedImageUpload, '/api/upload/tamil', endpoint='tamil_upload', resource_class_args=('ta',))
api.add_resource(TranslatedImageUpload, '/api/upload/french', endpoint='french_upload', resource_class_args=('fr',))
api.add_resource(TranslatedImageUpload, '/api/upload/italian', endpoint='italian_upload', resource_class_args=('it',))
api.add_resource(TranslatedImageUpload, '/api/upload/korean', endpoint='korean_upload', resource_class_args=('ko',))
api.add_resource(TranslatedImageUpload, '/api/upload/mandarin', endpoint='mandarin_upload', resource_class_args=('zh-cn',))
api.add_resource(TranslatedImageUpload, '/api/upload/japanese', endpoint='japanese_upload', resource_class_args=('ja',))


# Web Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return render_template('index.html', error='No file part')
    
    file = request.files['image']
    language = request.form.get('language', 'english')
    
    if file.filename == '':
        return render_template('index.html', error='No selected file')
    
    if file and file.filename.lower().endswith(('.jpg', '.jpeg', '.png')):
        # Save the file
        filename = str(uuid.uuid4()) + '.jpg'
        file_path = os.path.join('models/images', filename)
        file.save(file_path)
        
        # Process the image
        result, vis_path, vis_filename = runapp(file_path)
        
        # Delete the uploaded file
        delete_image_file(file_path)
        
        if not result:
            return render_template('index.html', error='Could not process the image')
        
        # Get disease info based on result
        disease_info = {
            "Target spot": {
                "cause": "Target spot, or Corynespora leaf spot, is a fungal disease affecting various crops like tomatoes, soybeans, and cotton. It is caused by the fungus Corynespora cassiicola.",
                "prevention": "Farmers can prevent target spot by planting resistant cultivars, practicing crop rotation, and ensuring proper plant spacing for good air circulation.",
                "solution": "Manage target spot disease on tomato leaves by pruning infected foliage, improving air circulation, practicing proper watering at the base, using mulch, implementing crop rotation, considering fungicides if necessary, and monitoring plant health."
            },
            "Leaf mold": {
                "cause": "Leaf mold is primarily caused by a fungus called Fulvia fulva (formerly Cladosporium fulvum). It thrives in warm, humid conditions.",
                "prevention": "To prevent leaf mold, farmers can use resistant varieties, practice crop rotation, ensure proper plant spacing for good air circulation, and avoid overhead irrigation.",
                "solution": "If leaf mold occurs, farmers should remove and destroy infected plant material. Fungicides can be applied preventatively, but they should be used judiciously and as part of an integrated disease management strategy."
            },
            "Late blight": {
                "cause": "Late blight is a devastating disease affecting several crops, most notably tomatoes and potatoes. It is caused by a fungus-like oomycete pathogen called Phytophthora infestans. It spreads rapidly under cool, wet conditions.",
                "prevention": "Farmers can prevent late blight by planting resistant varieties, practicing good sanitation, providing adequate plant spacing for airflow, and avoiding overhead irrigation.",
                "solution": "If late blight occurs, farmers should promptly remove and destroy infected plants. Fungicides can be used preventatively, especially during periods of high disease pressure. Early detection and action are critical to managing this disease."
            },
            "Curl virus": {
                "cause": "Curl leaf, also known as leaf curl, is commonly caused by viral infections such as Tomato leaf curl virus or Peach leaf curl virus. It is often spread by insect vectors, particularly whiteflies.",
                "prevention": "Farmers can prevent curl leaf by using disease-resistant varieties, controlling insect populations through integrated pest management (IPM) practices, and employing physical barriers such as nets or row covers.",
                "solution": "Once curl leaf is established, there are no specific curative treatments. Infected plants should be removed and destroyed to prevent further spread. Future plantings should be carefully monitored for symptoms."
            },
            "Spider mites": {
                "cause": "Spider mites are tiny arachnids that infest a wide range of crops, including fruits, vegetables, and ornamental plants. They pierce plant tissues and feed on sap, causing damage.",
                "prevention": "Farmers can prevent spider mite infestations by practicing good crop hygiene, providing adequate moisture levels, promoting beneficial insects that prey on mites, and using reflective mulches.",
                "solution": "In case of spider mite infestations, farmers can employ biological controls like predatory mites or insecticidal soaps. If necessary, selective insecticides can be used, following proper application guidelines."
            },
            "Mosaic virus": {
                "cause": "Mosaic viruses are a group of viruses that affect a wide range of crops, including tomatoes, cucumbers, peppers, and many others. They are mainly transmitted through infected plant sap, insects, or contaminated tools.",
                "prevention": "Farmers can prevent mosaic virus by using virus-free seeds or transplants, practicing strict sanitation measures, controlling insect vectors, and removing and destroying infected plants.",
                "solution": "Unfortunately, there are no effective treatments for mosaic viruses once plants are infected. Therefore, prevention is crucial in managing this disease."
            }
        }
        
        cause = "Not available"
        prevention = "Not available"
        solution = "Not available"
        
        if result in disease_info:
            cause = disease_info[result]["cause"]
            prevention = disease_info[result]["prevention"]
            solution = disease_info[result]["solution"]
        elif result == "healthy" or result == "healthy leaf":
            cause = "Your plant is healthy"
            prevention = "Continue good agricultural practices"
            solution = "No treatment needed"
        
        # If language is not English, translate the result
        if language != 'english':
            language_code = {
                'hindi': 'hi',
                'tamil': 'ta',
                'french': 'fr',
                'italian': 'it',
                'korean': 'ko',
                'mandarin': 'zh-cn',
                'japanese': 'ja'
            }.get(language, 'en')
            
            # Translate the information
            translator = Translator()
            result = translator.translate(result, dest=language_code).text
            cause = translator.translate(cause, dest=language_code).text
            prevention = translator.translate(prevention, dest=language_code).text
            solution = translator.translate(solution, dest=language_code).text
        
        return render_template('result.html', 
                              result=result,
                              cause=cause,
                              prevention=prevention,
                              solution=solution,
                              image=vis_filename)
    else:
        return render_template('index.html', error='Invalid file format. Please upload a JPG, PNG, or JPEG image')

import os
port = int(os.getenv("PORT", 10000))

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=port, debug=True)
    
    # For production with Gunicorn
    # from gunicorn.app.base import BaseApplication

    # class FlaskApplication(BaseApplication):
    #     def __init__(self, app, options=None):
    #         self.options = options or {}
    #         self.application = app
    #         super().__init__()

    #     def load_config(self):
    #         for key, value in self.options.items():
    #             self.cfg.set(key, value)

    #     def load(self):
    #         return self.application

    # options = {
    #     'bind': f'0.0.0.0:{port}',
    #     'workers': 4,  # Adjust based on your server capacity
    #     'threads': 2,  # Adjust based on your server capacity
    #     'accesslog': '-',  # Print access logs to stdout
    #     'errorlog': '-'    # Print error logs to stdout
    # }

    # FlaskApplication(app, options).run()