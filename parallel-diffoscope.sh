#!/bin/bash

# Define an array of JAR files
desktop_JARS=(
    "legend-engine-server-4.4.5-shaded.jar:legend-engine-server-4.4.5-shaded.jar"
    "legend-engine-server-4.4.6-shaded.jar:legend-engine-server-4.4.6-shaded.jar"
    "legend-engine-server-4.4.7-shaded.jar:legend-engine-server-4.4.7-shaded.jar"
    "legend-engine-server-4.4.8-shaded.jar:legend-engine-server-4.4.8-shaded.jar"
    "legend-engine-server-4.5.0-shaded.jar:legend-engine-server-4.5.0-shaded.jar"
    "legend-engine-server-4.6.0-shaded.jar:legend-engine-server-4.6.0-shaded.jar"
    "legend-engine-server-4.6.2-shaded.jar:legend-engine-server-4.6.2-shaded.jar"
    "legend-engine-server-4.7.0-shaded.jar:legend-engine-server-4.7.0-shaded.jar"
    "hive-jdbc-4.0.0-standalone.jar:hive-jdbc-4.0.0-standalone.jar"
    "legend-engine-xt-relationalStore-spanner-jdbc-shaded-4.56.0.jar:legend-engine-xt-relationalStore-spanner-jdbc-shaded-4.56.0.jar"
)

# Base path for source files

# Loop over JAR files and run in parallel

compare_jars() {
    BASE_PATH="/mnt/hdd2/amansha/reproducible-central/results/org.finos.legend.engine/legend-engine"
    JAR=$1
    if [[ "$1" == "hive-jdbc-4.0.0-standalone.jar:hive-jdbc-4.0.0-standalone.jar" ]] 
    then
        BASE_PATH="/mnt/hdd2/amansha/reproducible-central/results/org.apache.hive/hive"
    fi
    echo "JNORM $JAR"
    SINGLE_JAR=$(echo "$JAR" | cut -d ':' -f 1)
    echo "Single JAR: $SINGLE_JAR"
    VERSION=$(echo "$JAR" | sed -E 's/.*-([0-9]+\.[0-9]+\.[0-9]+).*/\1/')

    DIFFOSCOPE_FILE="${SINGLE_JAR}.diffoscope.json"

    echo "Diffoscope file: $DIFFOSCOPE_FILE"
    
    REF_PATH="$BASE_PATH/$VERSION/reference/$JAR"
    REB_PATH="$BASE_PATH/$VERSION/rebuild/$JAR"

    docker run --rm --user $(id -u) \
        -w /mnt \
        --mount type=bind,source="$REF_PATH",target=/reference.jar \
        -v $(pwd):/mnt \
        algomaster99/jnorm:latest \
        -o \
        -n \
        -a \
        -s \
        -p \
        -c \
        -r2 \
        -i /reference.jar \
        -d $BASE_PATH/$VERSION/jnorm/reference/$JAR &> $BASE_PATH/$VERSION/jnorm/reference/${SINGLE_JAR}.jnorm.log
    
    reference_exit_code=$?
    
    docker run --rm --user $(id -u) \
        -w /mnt \
        --mount type=bind,source="$REB_PATH",target=/rebuild.jar \
        -v $(pwd):/mnt \
        algomaster99/jnorm:latest \
        -o \
        -n \
        -a \
        -s \
        -p \
        -c \
        -r2 \
        -i /rebuild.jar \
        -d $BASE_PATH/$VERSION/jnorm/rebuild/$JAR &> $BASE_PATH/$VERSION/jnorm/rebuild/${SINGLE_JAR}.jnorm.log

    rebuild_exit_code=$?
    
    diff -u $BASE_PATH/$VERSION/jnorm/reference/$JAR $BASE_PATH/$VERSION/jnorm/rebuild/$JAR &> $BASE_PATH/$VERSION/jnorm/${SINGLE_JAR}.diff

    diff_exit_code=$?

    echo "{\"reference\": $reference_exit_code, \"rebuild\": $rebuild_exit_code, \"diff\": $diff_exit_code}" > $BASE_PATH/$VERSION/jnorm/${SINGLE_JAR}.json

}

export -f compare_jars

# Run comparisons in parallel using the specified number of cores
parallel -j 12 compare_jars ::: "${desktop_JARS[@]}"
echo "All comparisons completed."
