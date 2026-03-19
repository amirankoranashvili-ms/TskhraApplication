pipeline {
    agent any

    options {
        skipDefaultCheckout(false)
    }

    stages {
        stage('Pull Latest Code') {
            steps {
                echo 'Code pulled successfully!'
            }
        }

        stage('Build Maven Project') {
            steps {
                dir('Modulith') {
                    echo 'Building Maven project...'
                    sh 'mvn clean package'
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                echo 'Rebuilding and starting Docker container...'
                sh 'docker compose -p tskhraapplication up -d --build modulith'
            }
        }
    }

    post {
        success {
            echo '✅ Deployment successful!'
        }
        failure {
            echo '❌ Deployment failed.'
        }
    }
}