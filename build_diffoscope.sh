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

counter=0
grep '# diffoscope ' ${compare} | ${sed} -e 's/# diffoscope //' | ( while read -r line
do
  ((counter++))
  # Split $line into path1 and path2

  relpath1=$(echo "$line" | cut -d' ' -f1)
  relpath2=$(echo "$line" | cut -d' ' -f2)
  path1=$builddir/$relpath1
  path2=$builddir/$relpath2
  diffoscope_file="$(basename $relpath1).diffoscope.json"
  diffoscope_file_path=$(dirname ${compare})/${diffoscope_file}


  dir_with_version=$(pwd)
  pushd ..
  echo -e "$counter / $count \033[1m$relpath1 $relpath2\033[0m"
  runcommand docker run --rm \
      -w /mnt \
      -v $(realpath $builddir):/mnt \
      -v $(realpath $path1):/$relpath1 \
      -v $(realpath $path2):/$relpath2 \
      -v $dir_with_version:/output \
      custom-diffoscope \
        --no-progress \
        --json /output/$(basename ${diffoscope_file_path}) \
        /$relpath1 /$relpath2
  exit_code=$?
  logtofile "diffoscope exit_code=$exit_code" $RESULT_DIR/out.log
  popd
  # remove ansi escape codes from file
  ${sed} -i 's/\x1b\[[0-9;]*m//g' ${diffoscope_file_path}
done )
