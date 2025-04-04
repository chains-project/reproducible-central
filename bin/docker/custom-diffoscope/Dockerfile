# Start from the official diffoscope image
FROM registry.salsa.debian.org/reproducible-builds/diffoscope:latest

# Set the working directory
WORKDIR /mnt

# Copy Procyon dependencies
COPY ./bin/docker/custom-diffoscope/procyon-dependencies/procyon-decompiler-0.6.0.jar /usr/share/java/
COPY ./bin/docker/custom-diffoscope/procyon-dependencies/procyon /usr/bin/procyon


# Set the entrypoint to run diffoscope
ENTRYPOINT ["diffoscope"]
