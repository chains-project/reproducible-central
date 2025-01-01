import os
import glob
import re
import shutil
import json


BASE_DIR = 'minified_results'

CATEGORIES_ROOT = 'categories'

OTHER_FILES = os.path.join(CATEGORIES_ROOT, 'other_files')
GIT_FILES = os.path.join(CATEGORIES_ROOT, 'git_files')
FILES_IDENTICAL_REGARDLESS_OF_NAMES = os.path.join(CATEGORIES_ROOT, 'files_identical_regardless_of_names')
BUILD_TIMESTAMP = os.path.join(CATEGORIES_ROOT, 'build_timestamp')
MANIFEST = os.path.join(CATEGORIES_ROOT, 'manifest')
BINARY_DATA = os.path.join(CATEGORIES_ROOT, 'binary_data')
ORDERING_DIFFERENCES = os.path.join(CATEGORIES_ROOT, 'ordering_differences')
FILETYPE = os.path.join(CATEGORIES_ROOT, 'filetype')
FILE_LIST = os.path.join(CATEGORIES_ROOT, 'file_list')
CYCLONEDX = os.path.join(CATEGORIES_ROOT, 'cyclonedx')
DIRECTORY_FILE_TYPE = os.path.join(CATEGORIES_ROOT, 'directory_file_type')
NOTICE = os.path.join(CATEGORIES_ROOT, 'notice')

CATEGORIES = [
    OTHER_FILES,
    FILES_IDENTICAL_REGARDLESS_OF_NAMES,
    BUILD_TIMESTAMP,
    MANIFEST,
    BINARY_DATA,
    ORDERING_DIFFERENCES,
    FILETYPE,
    FILE_LIST,
    CYCLONEDX,
    DIRECTORY_FILE_TYPE,
    NOTICE
]

for category in CATEGORIES:
    os.makedirs(category, exist_ok=True)


def create_cluster(directories_to_create, diffoscope_file, new_root):
    os.makedirs(os.path.join(new_root, "/".join(directories_to_create)), exist_ok=True)
    shutil.copy(diffoscope_file, os.path.join(new_root, "/".join(directories_to_create)))


def does_file_have_buildtimestamp(diffoscope_file_content):
    # TODO: this is false positive: /home/aman/Desktop/experiments/reproducible-central/categories/build_timestamp/org.spdx/spdx-maven-plugin/0.7.0/META-INF_maven_org.spdx_spdx-maven-plugin_pom.properties.diffoscope.json
    regexes = [
        r"[+-]#[A-Za-z]{3} [A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2} [A-Z]+ \d{4}",
        r"[+-]schema\. // Generated on: \d{4}\.\d{2}\.\d{2} at \d{2}:\d{2}:\d{2} [APap][Mm] [A-Z]{3} //",
        r"[+-]\s+<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z</timestamp>",
        r"[+-]\s+<project\.build\.outputTimestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z</project\.build\.outputTimestamp>",
        r"[+-].*Built on : ([A-Za-z]{3} \d{2}, \d{4}) \((\d{2}:\d{2}:\d{2}) ([A-Z]{3})\)",
        r"[+-](axisBuiltOnRaw|builtOn)=([A-Za-z]{3} \d{2}, \d{4}|\d{3} \d{2}, \d{4}) \(\d{2}:\d{2}:\d{2} [A-Z]{3}\)",
        r"[+-]\s+<project\.build\.outputTimestamp>\d+</project\.build\.outputTimestamp>",
        r"date=\"([A-Za-z]{3} [A-Za-z]{3} \d{1,2} \d{2}:\d{2}:\d{2} [A-Z]{3} \d{4})",
        r"\(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{4}\)",
        r"^[+-].*\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$",
        r"[+-]# Generated at: [A-Za-z]{3} [A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2} [A-Z]{3} \d{4}$",
    ]
    for regex in regexes:
        if re.search(regex, diffoscope_file_content) is not None:
            return True
    return False

def is_manifest(diffoscope_file_name):
    return 'MANIFEST.MF' in diffoscope_file_name

def identical_files(diffoscope_file_json_dict):
    comments = diffoscope_file_json_dict.get('comments', [])
    return any(comment.lower() == 'Files identical despite different names'.lower() for comment in comments)

def is_notice(diffoscope_file_name):
    return 'NOTICE' in diffoscope_file_name

def is_ordering_differences(diffoscope_file_json_dict):
    if 'Ordering differences only'.lower() in str(diffoscope_file_json_dict).lower():
        return True
    return False
def file_becomes_directory_or_vice_versa(diffoscope_file_json_dict):
    unified_diff = _get_or_recurse_for_unified_diff(diffoscope_file_json_dict)
    if not unified_diff:
        return False
    return '-type: directory\n+type: file' in unified_diff or '+type: directory\n-type: file' in unified_diff

def _get_or_recurse_for_unified_diff(diffoscope_file_json_dict):
    unified_diff = diffoscope_file_json_dict.get('unified_diff', '')
    if unified_diff:
        return unified_diff
    else:
        for detail in diffoscope_file_json_dict.get('details', []):
            unified_diff = _get_or_recurse_for_unified_diff(detail)
            if unified_diff:
                return unified_diff
    return None

def is_there_change_in_build_timestamp(diffoscope_file_json_dict):
    if 'file list' in diffoscope_file_json_dict.get('source1', ''):
        return False
    # if _in_META_INF(diffoscope_file_json_dict):
    #     unified_diff = diffoscope_file_json_dict.get('unified_diff', '')
    #     # If unified_diff is None, then it is an empty file to avoid regex error
    #     unified_diff = '' if unified_diff is None else unified_diff
    #     regex = r"[-+]\#\w{3}\s\w{3}\s\d{2}\s\d{2}:\d{2}:\d{2}\s\w{1,10}\s\d{4}"
    #     return re.search(regex, unified_diff) is not None
    # if diffoscope_file_json_dict.get('source1', '').endswith('.pom'):
    #     regex = r"<project\.build\.outputTimestamp>(\d+|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)<\/project\.build\.outputTimestamp>"
    #     unified_diff = _get_or_recurse_for_unified_diff(diffoscope_file_json_dict)
    #     # If unified_diff is None, then it is an empty file to avoid regex error
    #     unified_diff = '' if unified_diff is None else unified_diff
    #     return re.search(regex, unified_diff) is not None
    # if diffoscope_file_json_dict.get('source1', '').endswith('.xsl'):
    #     regex = r"^[\+\-] \* .* Built on : (\w{3} \d{2}, \d{4}) \((\d{2}:\d{2}:\d{2} [A-Z]+)\)"
    #     unified_diff = _get_or_recurse_for_unified_diff(diffoscope_file_json_dict)
    #     # If unified_diff is None, then it is an empty file to avoid regex error
    #     unified_diff = '' if unified_diff is None else unified_diff
    #     return re.search(regex, unified_diff) is not None   
    # if diffoscope_file_json_dict.get('source1', '').endswith('.properties'):
    #     regex = r"\((\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\+\d{4})\)"
    #     unified_diff = _get_or_recurse_for_unified_diff(diffoscope_file_json_dict)
    #     # If unified_diff is None, then it is an empty file to avoid regex error
    #     unified_diff = '' if unified_diff is None else unified_diff
    #     return re.search(regex, unified_diff) is not None
    regex = r"(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?Z)|(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\+\d{4})?)|([A-Za-z]{3} [A-Za-z]{3} \d{2} \d{2}:\d{2}:\d{2} [A-Z]+ \d{4})|(\d{4}\.\d{2}\.\d{2} at \d{2}:\d{2}:\d{2} [AP]M [A-Z]+)"
    unified_diff = _get_or_recurse_for_unified_diff(diffoscope_file_json_dict)
    # If unified_diff is None, then it is an empty file to avoid regex error
    unified_diff = '' if unified_diff is None else unified_diff
    return re.search(regex, unified_diff) is not None

def is_there_change_in_binary_data(diffoscope_file_json_dict):
    unified_diff = diffoscope_file_json_dict.get('unified_diff', '')
    if not unified_diff:
        return False
    regex = r"[\-\+][0-9a-f]{8}:[\s0-9a-f]{40}"
    return re.search(regex, unified_diff) is not None

def is_there_change_in_cyclonedx(diffoscope_file_name):
    return 'cyclonedx' in diffoscope_file_name

def is_there_change_in_filetype(diffoscope_file_json_dict):
    return 'filetype' in diffoscope_file_json_dict.get('source1', '')

def is_there_change_in_file_list(diffoscope_file_json_dict):
    return 'file list' in diffoscope_file_json_dict.get('source1', '')

if __name__ == "__main__":
    for root, dirs, files in os.walk(BASE_DIR):
        for minified_diffoscope_file in files:
            added_to_cluster = False
            if '.diffoscope.json' in minified_diffoscope_file:
                with open(os.path.join(root, minified_diffoscope_file), 'r') as f:
                    content = json.load(f)
                    if identical_files(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), FILES_IDENTICAL_REGARDLESS_OF_NAMES)
                        added_to_cluster = True
                    if is_manifest(minified_diffoscope_file):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), MANIFEST)
                        added_to_cluster = True
                    if is_notice(minified_diffoscope_file):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), NOTICE)
                        added_to_cluster = True
                    if is_ordering_differences(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), ORDERING_DIFFERENCES)
                        added_to_cluster = True
                    if file_becomes_directory_or_vice_versa(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), DIRECTORY_FILE_TYPE)
                        added_to_cluster = True
                    if is_there_change_in_build_timestamp(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), BUILD_TIMESTAMP)
                        added_to_cluster = True
                    if is_there_change_in_binary_data(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), BINARY_DATA)
                        added_to_cluster = True
                    if is_there_change_in_cyclonedx(minified_diffoscope_file):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), CYCLONEDX)
                        added_to_cluster = True
                    if is_there_change_in_filetype(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), FILETYPE)
                        added_to_cluster = True
                    if is_there_change_in_file_list(content):
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), FILE_LIST)
                        added_to_cluster = True
                    # elif 'git.properties' in minified_diffoscope_file:
                    #     directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                    #     create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), GIT_FILES)
                    # elif does_file_have_buildtimestamp(content):
                    #     directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                    #     create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), BUILD_TIMESTAMP)
                    if not added_to_cluster:
                        directories_to_create = os.path.dirname(os.path.join(root, minified_diffoscope_file)).split(os.path.sep)[1:]
                        create_cluster(directories_to_create, os.path.join(root, minified_diffoscope_file), OTHER_FILES)
                