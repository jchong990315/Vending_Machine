# RESEARCH REPORT

1. make the project consistent on every machine ensuring it runs the same way
2. ease the management of dependencies as they are increasing as the complexity of the project increases
3. isolate each service which comes handy during troubleshoot
4. streamline the CI/CD experience

## SUMMARY

Prereq: Have docker desktop installed and your docker engine runnign

### REACT

https://www.docker.com/blog/how-to-dockerize-react-app/

The first and foremost step to dockerizing any service is to create its own Dockerfile (A Dockerfile is a text file containing instructions for building your source code)

it follows a pretty standard template.
First use the latest node version
Set the working directory inside container
Copy the package.json and package-lock.json as they contain our dependencies
install dependencies using npm install
copy the rest of the files
expose the port react would run on (3000 in our case)
define the command to start the react app

Step 2 is to create a .dockerignore file which behaves the same way as a .gitignore and tells Docker
which files or directories to exclude when building the image.

Ensure that the docker dameon is running
then build the container
docker build -t my-react-app .
This command tags the image with the name my-react-app and specifies the build context (current directory).

Finally run the docker image using
docker run -p 3000:3000 my-react-app

Open the application in browser
http://localhost:3000

When you are done
Hit ctrl+c to stop.

### DJANGO

https://www.docker.com/blog/how-to-dockerize-django-app/

Pretty much the same as above. We will have our own DockerFile for Django and here is the tempalte it follows
Select the image with the Python version you need.
Set the working directory of the application within the container.
Set the environment variables needed to build the application
Install dependencies and copy project files
Expose the Django server port and define the startup command.

Then we can build our container using:
docker build -t django-docker .

Then we can run our container using :
docker run -d -p 8000:8000 django-docker

If successful the above command will print out a hashcode.

### COMPOSE

https://docs.docker.com/compose/intro/compose-application-model/

We can manage all our dockerfiles using one .yml file. This makes the setup really easy
Need mysql to be done before this can be completed

## HOW LONG IT TOOK?

Research : 1 hour
Setup and documentation : 1 hour
Code : 30 minutes
