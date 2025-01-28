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

  pushd ..


  mkdir -p $dir_with_version/reference
  mkdir -p $dir_with_version/rebuild
  copied_reference=$dir_with_version/reference/"$(basename $reference):$(basename $rebuild)"
  copied_rebuild=$dir_with_version/rebuild/"$(basename $reference):$(basename $rebuild)"
  runcommand cp -r $(realpath $builddir)/$reference $copied_reference
  runcommand cp -r $(realpath $builddir)/$rebuild $copied_rebuild

  relative_reference=$(realpath --relative-to=${SCRIPTDIR} $copied_reference)
  relative_rebuild=$(realpath --relative-to=${SCRIPTDIR} $copied_rebuild)

  popd
  # remove ansi escape codes from file
  # ${sed} -i 's/\x1b\[[0-9;]*m//g' ${diffoscope_file_path}
done )
