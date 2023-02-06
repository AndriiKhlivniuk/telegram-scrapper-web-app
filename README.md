# telegram_srcapper
<h2>Create Docker Image</h2><br>
docker build -t fastapi-image .   <br>

<h2>Run Docker image</h2><br>
docker run -p 80:80 fastapi-image <br>
(This will start the server o your localhost. to access the application navigate to localhost:80 in your browser)

<h2>Admin login</h2><br>
Navigate to localhost:80/adminlogin and enter login "admin". This will  generate token for you, copy this token<br>

<h2>User login</h2><br>
Navigate to localhost:80/login and paste the token that you have been copied. This will give you access to the application<br>

<h2>Usage</h2><br>
Navigate to localhost:80 (root directory) and follow the instrucitons 


