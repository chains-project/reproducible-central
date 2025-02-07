#!/usr/bin/env bash

export SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"

. "${SCRIPTDIR}/bin/includes/bashcolors.sh"
. "${SCRIPTDIR}/bin/includes/logging.sh"

. "${SCRIPTDIR}/bin/includes/fetchSource.sh"
. "${SCRIPTDIR}/bin/includes/compareOutput.sh"

. "${SCRIPTDIR}/bin/includes/rebuildToolMvn.sh"
. "${SCRIPTDIR}/bin/includes/rebuildToolSbt.sh"
. "${SCRIPTDIR}/bin/includes/rebuildToolGradle.sh"

. "${SCRIPTDIR}/bin/includes/displayResult.sh"

export RESULT_DIR=$SCRIPTDIR/results


# ----------------------------------------------------------------------------------------------------

logtofile "" $RESULT_DIR/maven-module.log

buildspec=$1
if [ -z "${buildspec}" ]
then
  fatal "usage: rebuild.sh <file>.buildspec [staging|snapshot]"
fi
if [ -n "$2" ]
then
  referenceRepo=https://repository.apache.org/content/repositories/$2/
fi

echo -e "Rebuilding from buildspec \033[1m${buildspec}\033[0m"

. ${buildspec} || fatal "could not source ${buildspec}"

# The defaults when unspecified
DEFAULT_locale="en_US"
DEFAULT_timezone="UTC"
DEFAULT_umask=0002
DEFAULT_referenceRepo="https://repo.maven.apache.org/maven2/"

DEFAULT_oci_engine="docker"
DEFAULT_docker_build_opts=""
DEFAULT_podman_build_opts="--format docker"
DEFAULT_docker_run_opts=""
DEFAULT_podman_run_opts="--userns=keep-id"
DEFAULT_oci_engine_volumeflags=""
DEFAULT_oci_engine_build_opts="$([[ 'docker' == ${RB_OCI_ENGINE:-$DEFAULT_oci_engine} ]] && echo $DEFAULT_docker_build_opts || echo $DEFAULT_podman_build_opts)"
DEFAULT_oci_engine_run_opts="$([[ 'docker' == ${RB_OCI_ENGINE:-$DEFAULT_oci_engine} ]] && echo $DEFAULT_docker_run_opts || echo $DEFAULT_podman_run_opts)"

logtofile "Starting project $groupId:$artifactId:$version" $RESULT_DIR/maven-module.log

# Initialize JSON array if it doesn't exist

echo "| 1. rebuild what binaries?"
displayOptional  "referenceRepo" "$DEFAULT_referenceRepo"
displayMandatory "groupId"
displayMandatory "artifactId"
displayMandatory "version"
echo "| 2. from which sources?"
if [ -z "${sourceDistribution}" ]
then
  displayMandatory "gitRepo"
  displayMandatory "gitTag"
else
  displayMandatory "sourceDistribution"
fi
echo "| 3. with which rebuild environment?"
displayMandatory "tool"
displayMandatory "jdk"
displayOptional  "toolchains"
displayMandatory "newline"
displayOptional  "timezone"    "$DEFAULT_timezone"
displayOptional  "locale"      "$DEFAULT_locale"
displayOptional  "umask"       "$DEFAULT_umask"
displayOptional  "os"
displayOptional  "arch"
echo "| 4. how?"
displayMandatory "command"
[ -n "${RB_SHELL}" ] && RB_OCI_ENGINE="interactive shell"
displayOptional  "RB_OCI_ENGINE" "$DEFAULT_oci_engine"
displayOptional  "execBefore"
displayOptional  "execAfter"
echo "| 5. expected results?"
displayMandatory "buildinfo"
displayOptional  "diffoscope"
displayOptional  "issue"

[ -z "${timezone}" ] && timezone=$DEFAULT_timezone
[ -z "${locale}" ] && locale=$DEFAULT_locale
[ -z "${umask}" ] && umask=$DEFAULT_umask
[ -z "${RB_OCI_ENGINE}" ] && export RB_OCI_ENGINE=$DEFAULT_oci_engine
[ -z "${RB_OCI_ENGINE_BUILD_OPTS}" ] && export RB_OCI_ENGINE_BUILD_OPTS=$DEFAULT_oci_engine_build_opts
[ -z "${RB_OCI_ENGINE_RUN_OPTS}" ] && export RB_OCI_ENGINE_RUN_OPTS=$DEFAULT_oci_engine_run_opts
[ -z "${RB_OCI_VOLUME_FLAGS}" ] && export RB_OCI_VOLUME_FLAGS=$DEFAULT_oci_engine_volume_flags

base="$SCRIPTDIR"

pushd "$(dirname $(dirname ${buildspec}))" >/dev/null || fatal "Could not move into ${buildspec}"

echo
# set umask for the script execution itself because Git updates are better with target umask
umask $umask
export MVN_UMASK=${umask}
fetchSource

project_root=$(pwd)


pushd ../../${version} > /dev/null || fatal "Unable to move into ../../${version}"

if [ $artifactId == "jakarta.persistence-api" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/api --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "felix-parent" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/pom --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [[ $artifactId == "orc" && $groupId == "org.apache.orc" ]]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/java --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "maven-bundle-plugin" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/tools/maven-bundle-plugin --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "org.apache.felix.http.parent" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/http/parent --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "org.apache.felix.healthcheck.core" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/healthcheck/core --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "org.apache.felix.feature" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/features --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "cucumber-jvm" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $groupId == "io.cucumber" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/java --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $groupId == "org.apache.karaf" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/ --plain-text output.txt --json output.json --exclude-profiles &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [[ $artifactId == "bnd-plugin-parent" && $version == "7.0.0" ]]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/maven-plugins --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "bnd-plugin-parent" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/maven --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "kubernetes-client-project" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/kubernetes-model-generator --plain-text output.txt --json output.json --exclude-profiles &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
elif [ $artifactId == "mybatis-generator" ]
then
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root/core --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
else
  runcommand java -jar $SCRIPTDIR/maven-module-graph-1.0.0-SNAPSHOT.jar --project-root $project_root --plain-text output.txt --json output.json &> release.log
  exit_code=$?
  echo "counter_exit_code=$exit_code" >> $RESULT_DIR/maven-module.log
fi

popd > /dev/null || fatal "Unable to return to starting directory"

popd > /dev/null || fatal "Unable to return to starting directory"



