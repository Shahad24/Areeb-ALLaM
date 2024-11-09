# Areeb-ALLaM
Areeb is an interactive app designed for children to help them learn and engage with **ALLaM**, an Arabic large language model. It was developed during the Allam Hackathon 2024.

## Installation
Follow these steps to set up and run the backend of the project:

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/Shahad24/Areeb-ALLaM.git
   cd Areeb-ALLaM


2. Create a Conda environment to isolate dependencies:
   ```bash
   conda create --name areeb-env python=3.10

3. Activate the Conda environment:
   ```bash
   conda activate areeb-env
   
4. Install the required dependencies:
   ```bash
   pip install -r requirements.txt

### Setup Credentials
To configure credentials for the application, follow these steps:

Open the general_question.py and science_questions.py files.

You need to add your credentials in these files, such as API keys or any required authentication tokens.

### Running the App
   ```bash
   uvicorn main:app --reload --port 8888 --host localhost
  ```

**Note:** Due to the large size of the frontend application, we cannot push it to GitHub. However, you can find it [here](https://drive.google.com/file/d/1FkFgHRZNHuA36lBJMFktrljxmsE5OGqq/view?usp=sharing)

