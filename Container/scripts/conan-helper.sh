#!/bin/bash
set -e

usage() {
    echo "Usage: $0"
    echo -e "\t --get-package PKG_NAME VERSION BUILD_TYPE COMPILER_VERSION CPP_STD"
    echo -e "\t --get-path PKG_NAME VERSION"
    exit 1
}

function get_path {
    json_data=$(conan list "$pkg_name/$version:*" --format json)
    revision=$(echo "$json_data" | jq -r ".\"Local Cache\".\"$pkg_name/$version\".revisions | keys[0]")
    package=$(echo "$json_data" | jq -r ".\"Local Cache\".\"$pkg_name/$version\".revisions.\"$revision\".packages | keys[0]")

    conan cache path "$pkg_name/$version#$revision:$package"
}

if [ $# -lt 3 ]; then
    usage
fi

func=$1
pkg_name=$2
version=$3
shift 3

case $func in
    --get-path)
        get_path "$@"
        ;;
    --get-package)
        get_package "$@"
        ;;
    *)
        usage
        ;;
esac
