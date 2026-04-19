FROM maven:3.9.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY pom.xml .
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre
RUN groupadd --system app && useradd --system --gid app --uid 10001 --home /app app
WORKDIR /app
COPY --from=build /app/target/*.jar /app/app.jar
RUN chown -R app:app /app
USER app
EXPOSE 8080
ENV JAVA_OPTS=""
ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS -jar /app/app.jar"]
