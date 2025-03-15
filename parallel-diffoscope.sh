#!/bin/bash

# Define an array of JAR files
desktop_JARS=(
    "legend-engine-pure-code-compiled-core-4.4.7.jar:legend-engine-pure-code-compiled-core-4.4.7.jar"
    "legend-engine-pure-code-compiled-core-4.7.0.jar:legend-engine-pure-code-compiled-core-4.7.0.jar"
    "legend-engine-pure-code-compiled-core-4.4.8.jar:legend-engine-pure-code-compiled-core-4.4.8.jar"
    "legend-engine-xt-relationalStore-pure-4.56.0.jar:legend-engine-xt-relationalStore-pure-4.56.0.jar"
    "legend-engine-xt-sql-pure-metamodel-4.56.0.jar:legend-engine-xt-sql-pure-metamodel-4.56.0.jar"
    "legend-engine-xt-elasticsearch-V7-pure-metamodel-4.56.0.jar:legend-engine-xt-elasticsearch-V7-pure-metamodel-4.56.0.jar"
    "legend-engine-pure-code-compiled-core-4.56.0-sources.jar:legend-engine-pure-code-compiled-core-4.56.0-sources.jar"
    "legend-engine-xt-analytics-mapping-pure-4.56.0.jar:legend-engine-xt-analytics-mapping-pure-4.56.0.jar"
    "legend-engine-xt-serviceStore-pure-4.56.0.jar:legend-engine-xt-serviceStore-pure-4.56.0.jar"
    "legend-engine-pure-runtime-java-extension-compiled-functions-json-4.56.0.jar:legend-engine-pure-runtime-java-extension-compiled-functions-json-4.56.0.jar"
    "legend-engine-xt-protobuf-pure-4.56.0.jar:legend-engine-xt-protobuf-pure-4.56.0.jar"
    "legend-engine-xt-openapi-pure-4.56.0.jar:legend-engine-xt-openapi-pure-4.56.0.jar"
    "legend-engine-pure-code-compiled-core-4.56.0.jar:legend-engine-pure-code-compiled-core-4.56.0.jar"
    "legend-engine-xt-authentication-pure-4.56.0.jar:legend-engine-xt-authentication-pure-4.56.0.jar"
)

# Base path for source files

# Loop over JAR files and run in parallel

compare_jars() {
    BASE_PATH="/mnt/hdd2/amansha/reproducible-central/results/org.finos.legend.engine/legend-engine"
    JAR=$1
    echo "Comparing $JAR"
    SINGLE_JAR=$(echo "$JAR" | cut -d ':' -f 1)
    echo "Single JAR: $SINGLE_JAR"
    VERSION=$(echo "$JAR" | sed -E 's/.*-([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

    DIFFOSCOPE_FILE="${SINGLE_JAR}.diffoscope.json"

    echo "Diffoscope file: $DIFFOSCOPE_FILE"
    
    REF_PATH="$BASE_PATH/$VERSION/reference/$JAR"
    REB_PATH="$BASE_PATH/$VERSION/rebuild/$JAR"

    docker run --rm --user $(id -u) \
        -w /mnt \
        --mount type=bind,source="$REF_PATH",target=/input1 \
        --mount type=bind,source="$REB_PATH",target=/input2 \
        -v $(pwd):/mnt \
        algomaster99/diffoscope:latest \
        /input1 /input2 \
        --json /mnt/results/org.finos.legend.engine/legend-engine/$VERSION/$DIFFOSCOPE_FILE

}

export -f compare_jars

# Run comparisons in parallel using the specified number of cores
parallel -j 12 compare_jars ::: "${desktop_JARS[@]}"
echo "All comparisons completed."
