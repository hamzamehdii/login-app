pipeline {
    agent any

    environment {
        IMAGE_NAME     = "login-app"
        CONTAINER_NAME = "login-container"
        APP_PORT       = "5000"
        APP_URL        = "http://localhost:5000"
        ZAP_PORT       = "8090"
    }

    stages {

        // ── Stage 1: Pull latest code ──────────────────────────────
        stage('Checkout') {
            steps {
                echo '>>> Pulling code from GitHub...'
                checkout scm
            }
        }

        // ── Stage 2: Build Docker image ────────────────────────────
        stage('Build Image') {
            steps {
                echo '>>> Building Docker image...'
                bat "docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest ."
            }
        }

        // ── Stage 3: Deploy container ──────────────────────────────
        stage('Deploy') {
            steps {
                echo '>>> Stopping old container and deploying new one...'
                bat """
                    docker stop ${CONTAINER_NAME} 2>nul || echo no old container
                    docker rm   ${CONTAINER_NAME} 2>nul || echo no old container
                    docker run -d --name ${CONTAINER_NAME} -p ${APP_PORT}:5000 ${IMAGE_NAME}:latest
                """
                // Give the app 5 seconds to start before testing
                sleep(time: 5, unit: 'SECONDS')
            }
        }

        // ── Stage 4: Health check ──────────────────────────────────
        stage('Health Check') {
            steps {
                echo '>>> Verifying app is responding...'
                bat "powershell -Command \"Invoke-WebRequest -Uri ${APP_URL} -UseBasicParsing\""
            }
        }

        // ── Stage 5: Selenium functional tests ────────────────────
        stage('Selenium Tests') {
            steps {
                echo '>>> Running Selenium UI tests...'
                bat """
                    cd tests
                    pytest test_login.py -v ^
                        --html=selenium-report.html ^
                        --self-contained-html
                """
            }
            post {
                always {
                    // Publish the HTML report inside Jenkins UI
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'tests',
                        reportFiles: 'selenium-report.html',
                        reportName: 'Selenium Report'
                    ])
                }
            }
        }

        // ── Stage 6: Postman API tests ─────────────────────────────
        stage('Postman API Tests') {
            steps {
                echo '>>> Running Postman collection via Newman...'
                bat """
                    newman run postman\\login-app-tests.json ^
                        --reporters cli,htmlextra ^
                        --reporter-htmlextra-export postman\\newman-report.html
                """
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'postman',
                        reportFiles: 'newman-report.html',
                        reportName: 'Postman API Report'
                    ])
                }
            }
        }

        // ── Stage 7: JMeter performance tests ─────────────────────
        stage('JMeter Performance Tests') {
            steps {
                echo '>>> Running JMeter load test...'
                bat """
                    if exist jmeter\\html-report rmdir /s /q jmeter\\html-report
                    jmeter -n ^
                        -t jmeter\\login-load-test.jmx ^
                        -l jmeter\\results.jtl ^
                        -e -o jmeter\\html-report
                """
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: false,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'jmeter/html-report',
                        reportFiles: 'index.html',
                        reportName: 'JMeter Performance Report'
                    ])
                }
            }
        }

        // ── Stage 8: ZAP security scan ─────────────────────────────
        stage('OWASP ZAP Security Scan') {
            steps {
                echo '>>> Running ZAP baseline scan...'
                bat """
                    if exist zap-report rmdir /s /q zap-report
                    mkdir zap-report
                    zap.bat -cmd ^
                        -quickurl ${APP_URL} ^
                        -quickout %CD%\\zap-report\\zap-report.html ^
                        -quickprogress
                """
            }
            post {
                always {
                    publishHTML(target: [
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: 'zap-report',
                        reportFiles: 'zap-report.html',
                        reportName: 'ZAP Security Report'
                    ])
                }
            }
        }

        // ── Stage 9: Image vulnerability scan ─────────────────────
        stage('Trivy Image Scan') {
            steps {
                echo '>>> Scanning Docker image for CVEs...'
                bat "docker run --rm aquasec/trivy:latest image --exit-code 0 --severity HIGH,CRITICAL ${IMAGE_NAME}:latest"
            }
        }

    }

    // ── Post-pipeline actions ──────────────────────────────────────
    post {
        success {
            echo '=== PIPELINE PASSED === App deployed and all tests passed.'
        }
        failure {
            echo '=== PIPELINE FAILED === Check individual stage logs above.'
            bat "docker logs ${CONTAINER_NAME} 2>nul || echo container not running"
        }
        always {
            echo '>>> Pipeline complete. Reports available in Jenkins sidebar.'
        }
    }
}