#!/bin/bash

# Define an array of JAR files
dekstop_JARS=(
    "legend-engine-pure-code-compiled-core-4.4.7.jar"
    "legend-engine-pure-code-compiled-core-4.7.0.jar"
    "legend-engine-pure-code-compiled-core-4.4.8.jar"
    "legend-engine-xt-relationalStore-pure-4.56.0.jar"
    "legend-engine-xt-sql-pure-metamodel-4.56.0.jar"
    "legend-engine-xt-elasticsearch-V7-pure-metamodel-4.56.0.jar"
    "legend-engine-pure-code-compiled-core-4.56.0-sources.jar"
    "legend-engine-xt-analytics-mapping-pure-4.56.0.jar"
    "legend-engine-xt-serviceStore-pure-4.56.0.jar"
    "legend-engine-pure-runtime-java-extension-compiled-functions-json-4.56.0.jar"
    "legend-engine-xt-protobuf-pure-4.56.0.jar"
    "legend-engine-xt-openapi-pure-4.56.0.jar"
    "legend-engine-pure-code-compiled-core-4.56.0.jar"
    "legend-engine-xt-authentication-pure-4.56.0.jar"
)

# Base path for source files
BASE_PATH="/mnt/hdd2/amansha/reproducible-central/results/org.finos.legend.engine/legend-engine"

# Loop over JAR files and run in parallel
for JAR in "${desktop_JARS[@]}"; do
    VERSION=$(echo "$JAR" | grep -oE "[0-9]+\.[0-9]+\.[0-9]+")
    
    docker run --rm --user $(id -u) \
        -w /mnt \
        --mount type=bind,source=$BASE_PATH/$VERSION/reference/$JAR,target=/input1 \
        --mount type=bind,source=$BASE_PATH/$VERSION/rebuild/$JAR,target=/input2 \
        -v $(pwd):/mnt \
        algomaster99/diffoscope:latest \
        /input1 /input2 \
        --json /mnt/results/org.finos.legend.engine/legend-engine/$VERSION/$JAR &

done

# Wait for all background processes to finish
wait
echo "All comparisons completed."
