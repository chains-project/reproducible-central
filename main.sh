#!/bin/bash
export CI=true

success_count=0
failure_count=0
# Set the path to the result directory
RESULT_DIR="./release-counter"

# Set the path to the rebuild_to_get_diffoscope.sh script
REBUILD_SCRIPT="./rebuild.sh"

# Check if the result directory exists
if [ ! -d "$RESULT_DIR" ]; then
    echo "Error: Result directory not found: $RESULT_DIR"
    exit 1
fi

# Check if the rebuild script exists and is executable
if [ ! -x "$REBUILD_SCRIPT" ]; then
    echo "Error: Rebuild script not found or not executable: $REBUILD_SCRIPT"
    exit 1
fi

# Find all buildspec files in the result directory and its subdirectories
find "$RESULT_DIR" -type f -name "*.buildspec" | while read -r buildspec; do
    echo "Processing buildspec: $buildspec"
    
    buildspec_dir=$(dirname "$buildspec")

    if ls $buildspec_dir/*.buildcompare 1> /dev/null 2>&1;
    then
        echo "Skipping $buildspec as .buildcompare file exists"
        continue
    fi

    # Call the rebuild_to_get_diffoscope.sh script with the buildspec file
    "$REBUILD_SCRIPT" "$buildspec"
    
    # Check the exit status of the rebuild script
    if [ $? -ne 0 ]; then
        echo "Warning: rebuild_to_get_diffoscope.sh failed for $buildspec"
        ((failure_count++))
    else
        ((success_count++))
    fi
    
    echo "Finished processing: $buildspec"
    echo "----------------------------------------"
done

echo "All buildspec files have been processed."
echo "Summary: $success_count successes, $failure_count failures"
