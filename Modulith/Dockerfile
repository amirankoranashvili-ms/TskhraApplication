FROM eclipse-temurin:21-jre

WORKDIR /app

# Copy the built jar from the Maven target directory.
# Make sure to run `mvn clean package` at the project root before building the image.
ARG JAR_FILE=target/Modulith-0.0.1-SNAPSHOT.jar
COPY ${JAR_FILE} app.jar

# The application will listen on this port inside the container.
EXPOSE 8081

ENTRYPOINT ["java","-jar","/app/app.jar"]

