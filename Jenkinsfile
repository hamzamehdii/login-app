pipeline {
    agent any

    environment {
        IMAGE_NAME = "login-app"
        CONTAINER_NAME = "login-container"
        APP_PORT = "5000"
    }

    stages {

        stage('Checkout') {
            steps {
                echo 'Pulling code from repository...'
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                bat "docker build -t ${IMAGE_NAME}:latest ."
            }
        }

        stage('Stop Old Container') {
            steps {
                echo 'Removing old container if it exists...'
                bat """
                    docker stop ${CONTAINER_NAME} || exit 0
                    docker rm ${CONTAINER_NAME} || exit 0
                """
            }
        }

        stage('Deploy Container') {
            steps {
                echo 'Starting new container...'
                bat "docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 ${IMAGE_NAME}:latest"
            }
        }

        stage('Health Check') {
            steps {
                echo 'Waiting for app to start...'
                sleep(time: 5, unit: 'SECONDS')
                bat "curl -f http://localhost:${APP_PORT} || exit 1"
            }
        }

        stage('Basic Functional Test') {
            steps {
                echo 'Running functional tests...'
                bat """
                    curl -s -o NUL -w "%%{http_code}" http://localhost:${APP_PORT} > status.txt
                    type status.txt
                    findstr "200" status.txt
                """
            }
        }

    }

    post {
        success {
            echo 'Pipeline succeeded! App is deployed and tested.'
        }
        failure {
            echo 'Pipeline failed. Check the logs above.'
            bat "docker logs ${CONTAINER_NAME} || exit 0"
        }
    }
}