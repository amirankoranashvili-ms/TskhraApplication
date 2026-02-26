FROM eclipse-temurin:21-jre

WORKDIR /app

# Make sure to run `mvn clean package` at the project root before building the image.
ARG JAR_FILE=target/Modulith-0.0.1-SNAPSHOT.jar
COPY ${JAR_FILE} app.jar

EXPOSE 8081

ENTRYPOINT ["java","-jar","/app/app.jar"]

