## Exercise 1 - Task 1 : Docker Hub Account
- Visited https://www.docker.com/ and created a Docker Hub account.
- Account username: <nahyung4>
## Exercise 1 - Task 2 : Install Docker Desktop
- Installed Docker Desktop for Mac.
- Signed in to Docker Hub from the app.
## Exercise 1 – Task 3 : Verify Docker Daemon
docker --version
## Exercise 1 - Task 4 : Complete the Docker Desktop Tutorial
### Step 1 - Clone Repository
git clone https://github.com/docker/getting-started.git
cd getting-started
### Step 2 - Build Image
docker build -t docker101tutorial .
### Step 3: Run Container
docker run -d -p 80:80 --name docker-tutorial docker101tutorial
### Step 4: Tag Image
DOCKER_USER=nahyung4
docker tag docker101tutorial $DOCKER_USER/docker101tutorial:v1
### Step 5: Push Image to Docker Hub
docker login
docker push $DOCKER_USER/docker101tutorial:v1
### Step 6: Verify on Docker Hub
- Repository: `nahyung4/docker101tutorial`
- Tag: `v1` confirmed visible on Docker Hub.
## Exercise 2 – Task 0: Clean Up
docker ps -a
docker stop docker-tutorial
docker rm docker-tutorial
## Exercise 2 – Task 1: BusyBox Container
docker run -it --rm busybox
# inside BusyBox:
ls
mkdir test
whoami
exit
### Exercise 2 – Task 2 – Step 1: Run Nginx
docker run -d -p 80:80 --name web nginx
http://127.0.0.1
### Exercise 2 – Task 2 – Step 4: Cleanup
docker stop web
docker rm web
