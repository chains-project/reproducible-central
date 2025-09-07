FROM debian:trixie-20250203-slim

# Create a non-root user
RUN useradd -ms /bin/bash user

RUN apt-get update && apt-get install -y curl

RUN apt-get update && \
apt-get install -y -q bash-completion bison build-essential clang debhelper default-jdk-headless devscripts doxygen fakeroot flex g++ gdb git graphviz libffi-dev libncurses5-dev libtool make mcpp pkg-config python3-dev sqlite3 swig zlib1g-dev cmake ruby libboost-system-dev libboost-filesystem-dev libboost-thread-dev libboost-date-time-dev libsqlite3-dev nodejs npm

# Install Soufflé
RUN curl -L https://github.com/souffle-lang/souffle/releases/download/2.5/x86_64-ubuntu-2404-souffle-2.5-Linux.deb -o x86_64-ubuntu-2404-souffle-2.5-Linux.deb
RUN dpkg -i x86_64-ubuntu-2404-souffle-2.5-Linux.deb

# Install diff2html-cli
RUN npm install -g diff2html-cli

COPY daleq-1.2.3.jar /daleq.jar

# Create the output directory and set permissions
RUN mkdir /output && chown user:user /output

# Switch to the non-root user
USER user

ENTRYPOINT ["java", "-jar", "/daleq.jar"]