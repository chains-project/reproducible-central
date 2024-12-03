#!/usr/bin/env bash

. "${SCRIPTDIR}/bin/includes/logging.sh"

# path to .buildcompare file
compare=$1
# relative path to source code, usually buildcache/${artifactId}
builddir=$2

diffoscope_file=$(dirname ${compare})/$(basename ${compare} .buildcompare).diffoscope
count="$(grep "^# diffoscope" ${compare} | wc -l)"

[ $count -eq 0 ] && echo "No diffoscope command listed in $compare" && exit

echo -e "saving build diffoscope file to \033[1m${diffoscope_file}\033[0m for $count issues"

sed="sed"
if [ "$(uname -s)" ==  "Darwin" ]
then
  command -v gsed >/dev/null 2>&1 || { echo "require GNU sed: brew install gsed  Aborting."; exit 1; }
  sed="gsed"
fi

dir_with_version=$(pwd)

counter=0
grep '# diffoscope ' ${compare} | ${sed} -e 's/# diffoscope //' | ( while read -r line
do
  ((counter++))
  # Split $line into path1 and path2

  reference=$(echo "$line" | cut -d' ' -f1)
  rebuild=$(echo "$line" | cut -d' ' -f2)
  echo "$line"
  echo "Reference: $reference"
  echo "Rebuild: $rebuild"
  path1=$builddir/$reference
  path2=$builddir/$rebuild
  diffoscope_file="$(basename $reference).diffoscope.json"
  diffoscope_file_path=$(dirname ${compare})/${diffoscope_file}


  pushd ..
  # echo -e "$counter / $count \033[1m$reference $rebuild\033[0m"
  # runcommand docker run --rm \
  #     -w /mnt \
  #     -v $(realpath $builddir):/mnt \
  #     -v $(realpath $path1):/$reference \
  #     -v $(realpath $path2):/$rebuild \
  #     -v $dir_with_version:/output \
  #     custom-diffoscope \
  #       --no-progress \
  #       --json /output/$(basename ${diffoscope_file_path}) \
  #       /$reference /$rebuild
  # exit_code=$?

  mkdir -p $dir_with_version/jNorm/$(basename $reference):$(basename $rebuild)/
  runcommand docker run --user $(id -u) --rm \
    -w /mnt \
    -v $(realpath $builddir):/mnt \
    -v $(realpath $path1):/$reference \
    -v $dir_with_version:/output \
    algomaster99/jnorm \
      -o -n -s -a -p \
      -i /$reference \
      -d /output/jNorm/$(basename $reference):$(basename $rebuild)/reference/ &> $dir_with_version/jNorm/$(basename $reference):$(basename $rebuild)/reference.log
  exit_code=$?

  jnorm_reference_exit_code=$exit_code

  runcommand docker run --user $(id -u) --rm \
    -w /mnt \
    -v $(realpath $builddir):/mnt \
    -v $(realpath $path2):/$rebuild \
    -v $dir_with_version:/output \
    algomaster99/jnorm \
      -o -n -s -a -p \
      -i /$rebuild \
      -d /output/jNorm/$(basename $reference):$(basename $rebuild)/rebuild/ &> $dir_with_version/jNorm/$(basename $reference):$(basename $rebuild)/rebuild.log
  exit_code=$?

  jnorm_rebuild_exit_code=$exit_code

  diff -u $dir_with_version/jNorm/$(basename $reference):$(basename $rebuild)/reference/ $dir_with_version/jNorm/$(basename $reference):$(basename $rebuild)/rebuild/ > $dir_with_version/jNorm/$(basename $reference):$(basename $rebuild)/diff.diff
  exit_code=$?

  jnorm_diff_exit_code=$exit_code

  mkdir -p $dir_with_version/reference
  mkdir -p $dir_with_version/rebuild
  copied_reference=$dir_with_version/reference/"$(basename $reference):$(basename $rebuild)"
  copied_rebuild=$dir_with_version/rebuild/"$(basename $reference):$(basename $rebuild)"
  runcommand cp $(realpath $builddir)/$reference $copied_reference
  runcommand cp $(realpath $builddir)/$rebuild $copied_rebuild

  relative_reference=$(realpath --relative-to=${SCRIPTDIR} $copied_reference)
  relative_rebuild=$(realpath --relative-to=${SCRIPTDIR} $copied_rebuild)

  # Determine jNorm status
  if [ $jnorm_reference_exit_code -eq 0 ] && [ $jnorm_rebuild_exit_code -eq 0 ] && [ $jnorm_diff_exit_code -eq 0 ]
  then
    jnorm_status=0  # successful normalization, no diff
  elif [ $jnorm_reference_exit_code -eq 0 ] && [ $jnorm_rebuild_exit_code -eq 0 ] && [ $jnorm_diff_exit_code -eq 1 ]
  then
    jnorm_status=1  # successful normalization, has diff
  else
    jnorm_status=2  # normalization failed
  fi

  # Update JSON with new artifact
  tmp_json=$(mktemp)
  jq --arg name "$(basename $reference)" \
    --arg status "$jnorm_status" \
    --arg reference_path "$([ -z "$copied_reference" ] && echo "" || echo "$relative_reference")" \
    --arg rebuild_path "$([ -z "$copied_rebuild" ] && echo "" || echo "$relative_rebuild")" \
    '.artifacts += [{"artifact_name": $name, "jNorm": ($status|tonumber), "reference": $reference_path, "rebuild": $rebuild_path}]' \
    "$dir_with_version/jNorm/jNorm_summary.json" > "$tmp_json" && mv "$tmp_json" "$dir_with_version/jNorm/jNorm_summary.json"

  popd
  # remove ansi escape codes from file
  # ${sed} -i 's/\x1b\[[0-9;]*m//g' ${diffoscope_file_path}
done )
