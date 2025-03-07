# Image Classification and Identification API

This project provides a Flask-based API for image classification and identification of plant diseases using machine learning models. The API allows users to upload images of plant leaves and receive predictions about their health status, along with relevant information about potential diseases.

## Features

- **Image Upload**: Users can upload images in JPG, PNG, or JPEG formats.
- **Disease Classification**: The API classifies the uploaded images and identifies potential diseases affecting the plants.
- **Disease Information**: For identified diseases, the API provides detailed information including causes, prevention methods, and solutions.
- **Multi-language Support**: The API supports translations of results into multiple languages including Hindi, Tamil, French, Italian, Korean, Mandarin, and Japanese.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables for the Roboflow API keys:
   ```bash
   export ROBOFLOW_API_KEY_CLASSIFICATION="your_classification_api_key"
   export ROBOFLOW_API_KEY_IDENTIFICATION="your_identification_api_key"
   ```

## Usage

1. Start the Flask application:
   ```bash
   python app.py
   ```

2. Access the API endpoints:
   - **Upload Image**: `POST /api/upload`
   - **Upload Image with Translation**: `POST /api/upload/<language>`

3. Example of a request using `curl`:
   ```bash
   curl -X POST -F "image=@path_to_your_image.jpg" http://localhost:10000/api/upload
   ```

## API Responses

The API returns JSON responses with the following structure:

- **Success Response**:
  ```json
  {
      "result": "Disease Name",
      "message": {
          "cause": "Cause of the disease",
          "prevention": "Prevention methods",
          "solution": "Solutions to manage the disease"
      },
      "image": "visualization_image_filename.jpg"
  }
  ```

- **Error Response**:
  ```json
  {
      "result": "failure",
      "message": "Error message"
  }
  ```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Flask](https://flask.palletsprojects.com/) - The web framework used.
- [Roboflow](https://roboflow.com/) - For providing the machine learning models.
- [Google Translate API](https://cloud.google.com/translate/docs) - For translation services.
