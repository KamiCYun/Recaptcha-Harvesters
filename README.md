# Captcha-Solver
This project was more POC than built for actual utility as seen by the messy and relatively unstructured code. Regardless, although it hasn't been updated in years, this project is still fully functional and allows you to generate Recaptcha V2 and V3 tokens through rendering the puzzles in an electron browser. This solver removes expired captcha tokens automatically and handles all aspects of token management in a local API. Many aspects of this project are still hardcoded since this was a very early POC version that was eventually dropped in favor of a new version of the solver and other methods for bypassing Recaptcha.
# Instructions
First clone or download the folder, to start it first run npm install and then npm start. Additionally, run python server.py to start the local api responsible for storing tokens. Making a get request to 127.0.0.1:5000/recaptcha/{sitename}/{recaptcha version}

