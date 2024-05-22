# TCF-FRONTEND WEB APP
### These dependencies are required:
- Material UI:
    - `npm install @mui/icons-material @mui/material @emotion/react @emotion/styled`
- React Beautiful DND:
    - `npm i react-beautiful-dnd`
- React Material UI Carousel:
    - `npm i react-slick`
- React-Router-Dom:
    - `npm i react-router-dom`
- Axios
    - `npm i axios`
- React-Gesture-Responder:
    - `npm i react-gesture-responder --legacy-peer-deps`
- React-Grid-DND:
    - `npm i react-grid-dnd --legacy-peer-deps`


### For React Native, we use Capacitor.js
- Capacitor.js:
    - `npm install @capacitor/cli @capacitor/core`
- Native platforms:
    - `npm install @capacitor/ios @capacitor/android`

### Steps:
1. Initializing capacitor.js: 
    - `npx cap init`
2. Add native platforms needed:
    - `npm cap add ios`
    - `npm cap add android`


# Backend
1. Create a virtual env
`python3 -m venv env`
2. Activate virtual env
`source env/bin/activate`
3. Install dependencies
`pip3 install -r requirements.txt`
## Updating database
- `python manage.py makemigrations`
- `python manage.py migrate`
## Create django admin
`python manage.py createsuperuser`
## Run server
`python manage.py runserver`