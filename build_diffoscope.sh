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

jNorm_successful_normalization=0
echo $jNorm_successful_normalization > /tmp/jNorm_successful_normalization.txt
jNorm_failed_normalization=0
echo $jNorm_failed_normalization > /tmp/jNorm_failed_normalization.txt
jNorm_failures=0
echo $jNorm_failures > /tmp/jNorm_failures.txt
dir_with_version=$(pwd)

counter=0
grep '# diffoscope ' ${compare} | ${sed} -e 's/# diffoscope //' | ( while read -r line
do
  ((counter++))
  # Split $line into path1 and path2

  reference=$(echo "$line" | cut -d' ' -f1)
  rebuild=$(echo "$line" | cut -d' ' -f2)
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
  # logtofile "diffoscope exit_code=$exit_code" $RESULT_DIR/out.log

  logtofile "jNorm $(basename $reference)" $RESULT_DIR/out.log
  mkdir -p $dir_with_version/$(basename $reference)/jNorm/
  runcommand docker run --user $(id -u) --rm \
    -w /mnt \
    -v $(realpath $builddir):/mnt \
    -v $(realpath $path1):/$reference \
    -v $dir_with_version:/output \
    algomaster99/jnorm \
      -o -n -s -a -p \
      -i /$reference \
      -d /output/$(basename $reference)/jNorm/reference/ &> $dir_with_version/$(basename $reference)/jNorm/reference.log
  exit_code=$?
  logtofile "reference exit_code=$exit_code" $RESULT_DIR/out.log

  jnorm_reference_exit_code=$exit_code

  runcommand docker run --user $(id -u) --rm \
    -w /mnt \
    -v $(realpath $builddir):/mnt \
    -v $(realpath $path2):/$rebuild \
    -v $dir_with_version:/output \
    algomaster99/jnorm \
      -o -n -s -a -p \
      -i /$rebuild \
      -d /output/$(basename $rebuild)/jNorm/rebuild/ &> $dir_with_version/$(basename $rebuild)/jNorm/rebuild.log
  exit_code=$?
  logtofile "rebuild exit_code=$exit_code" $RESULT_DIR/out.log

  jnorm_rebuild_exit_code=$exit_code

  diff -u $dir_with_version/$(basename $reference)/jNorm/reference/ $dir_with_version/$(basename $rebuild)/jNorm/rebuild/ > $dir_with_version/$(basename $reference)/jNorm/diff.diff
  exit_code=$?
  logtofile "jNorm diff exit_code=$exit_code" $RESULT_DIR/out.log

  jnorm_diff_exit_code=$exit_code

  runcommand cp $(realpath $builddir)/$reference $dir_with_version/$(basename $reference)/jNorm/reference
  runcommand cp $(realpath $builddir)/$rebuild $dir_with_version/$(basename $rebuild)/jNorm/rebuild

  jNorm_successful_normalization=$(< /tmp/jNorm_successful_normalization.txt)
  jNorm_failed_normalization=$(< /tmp/jNorm_failed_normalization.txt)
  jNorm_failures=$(< /tmp/jNorm_failures.txt)

  if [ $jnorm_reference_exit_code -eq 0 ] && [ $jnorm_rebuild_exit_code -eq 0 ] && [ $jnorm_diff_exit_code -eq 0 ]
  then
    (( jNorm_successful_normalization++ ))
    echo $jNorm_successful_normalization > /tmp/jNorm_successful_normalization.txt
  elif [ $jnorm_reference_exit_code -eq 0 ] && [ $jnorm_rebuild_exit_code -eq 0 ] && [ $jnorm_diff_exit_code -eq 1 ]
  then
    (( jNorm_failed_normalization++ ))
    echo $jNorm_failed_normalization > /tmp/jNorm_failed_normalization.txt
  else
    (( jNorm_failures++ ))
    echo $jNorm_failures > /tmp/jNorm_failures.txt
  fi

  popd
  # remove ansi escape codes from file
  ${sed} -i 's/\x1b\[[0-9;]*m//g' ${diffoscope_file_path}
done )

echo "jNorm_successful_normalization=$(< /tmp/jNorm_successful_normalization.txt)" > $dir_with_version/jNorm_summary.txt
echo "jNorm_failed_normalization=$(< /tmp/jNorm_failed_normalization.txt)" >> $dir_with_version/jNorm_summary.txt
echo "jNorm_failures=$(< /tmp/jNorm_failures.txt)" >> $dir_with_version/jNorm_summary.txt
