#!/bin/bash

# Array of JAR files to compare
desktop_JARS=(
    "legend-engine-pure-runtime-java-extension-compiled-functions-json-4.56.0.jar:legend-engine-pure-runtime-java-extension-compiled-functions-json-4.56.0.jar"
    "legend-engine-xt-protobuf-pure-4.56.0.jar:legend-engine-xt-protobuf-pure-4.56.0.jar"
    "legend-engine-xt-openapi-pure-4.56.0.jar:legend-engine-xt-openapi-pure-4.56.0.jar"
    "legend-engine-pure-code-compiled-core-4.56.0.jar:legend-engine-pure-code-compiled-core-4.56.0.jar"
    "legend-engine-xt-authentication-pure-4.56.0.jar:legend-engine-xt-authentication-pure-4.56.0.jar"
)

# Base path for source files
BASE_PATH="/mnt/hdd2/amansha/reproducible-central/results/org.finos.legend.engine/legend-engine"

# Function to compare JAR files
compare_jars() {
    JAR_PAIR=$1
    JAR=$(echo "$JAR_PAIR" | awk -F':' '{print $1}')
    echo "Comparing $JAR"
    
    VERSION=$(echo "$JAR" | sed -E 's/.*-([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

    REF_PATH="$BASE_PATH/$VERSION/reference/$JAR_PAIR"
    REB_PATH="$BASE_PATH/$VERSION/rebuild/$JAR_PAIR"

    docker run --rm --user $(id -u) \
        -w /mnt \
        --mount type=bind,source="$REF_PATH",target=/input1 \
        --mount type=bind,source="$REB_PATH",target=/input2 \
        -v $(pwd):/mnt \
        algomaster99/diffoscope:latest \
        /input1 /input2 \
        --json /mnt/results/org.finos.legend.engine/legend-engine/$VERSION/$JAR
}

export -f compare_jars

# Run comparisons in parallel
parallel -j 12 compare_jars ::: "${desktop_JARS[@]}"

echo "All comparisons completed."