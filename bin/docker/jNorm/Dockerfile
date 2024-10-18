FROM openjdk:17

# Create a non-root user
RUN useradd -ms /bin/bash user

COPY jnorm-jar-with-dependencies.jar /jnorm.jar

# Create the output directory and set permissions
RUN mkdir /output && chown user:user /output

# Switch to the non-root user
USER user

ENTRYPOINT ["java", "-jar", "/jnorm.jar"]