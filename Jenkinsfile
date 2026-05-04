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
                    sh 'mvn clean package -DskipTests'
                }
            }
        }

        stage('Deploy with Docker Compose') {
            steps {
                sh 'cp /opt/secrets/modulith.env ./.env'
                sh 'cp /opt/secrets/firebase-service-account.json ./firebase-service-account.json'
                echo 'Recreating Elasticsearch container...'
//                 sh 'docker compose -p tskhraapplication up -d --force-recreate elasticsearch'
                echo 'Rebuilding and starting Docker container...'
                sh 'docker compose -p tskhraapplication up -d --build'
//                 sh 'docker compose -p tskhraapplication up -d --build modulith'
//                 sh 'docker compose -p tskhraapplication up -d --build nginx'
                sh 'rm .env'
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