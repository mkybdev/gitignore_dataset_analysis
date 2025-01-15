args=(
    "\[.+\] ^\[.+\] range/leading"
    "\[.+\] ^.+\[.+\].+$ range/middle"
    "\[.+\] \[.+\]$ range/trailing"
    "\[.+\] \[[^\^].*\] range/unnegated"
    "^.*/.*$ ^/ directory_separator/leading"
    "^.*/.*$ ^.+/.+$ directory_separator/middle"
    "^.*/.*$ ^.+/$ directory_separator/trailing"
    "(?<!\*)\*(?!\*) ^\*(?!\*) asterisk/leading"
    "^\*(?!\*) ^\!\*(?!\*) asterisk/leading_negation"
    "^\*(?!\*) ^\*(?!\*)[^\/]*\/?$ asterisk/leading_global"
    "^\*(?!\*) ^\*(?!\*)[^\/]*\/[^\/]+ asterisk/leading_normal"
    "(?<!\*)\*(?!\*) (?<!\*)\*(?!\*)[^/$]*$ asterisk/last_segment"
    "(?<!\*)\*(?!\*)[^/$]*$ ^\*(?!\*)[^/$]*$ asterisk/last_segment_leading multi /\*(?!\*)[^/$]*$"
    "(?<!\*)\*(?!\*)[^/$]*$ [^/]+\*(?!\*)[^/$]+$ asterisk/last_segment_middle"
    "(?<!\*)\*(?!\*)[^/$]*$ (?<!\*)\*$ asterisk/last_segment_trailing"
    "(?<!\*)\*(?!\*) (?<!\*)\*\. asterisk/adjacent_dot multi \.\*(?!\*)"
    "(?<!\*)\*(?!\*) (?<!\*)\*\. asterisk/before_dot"
    "(?<!\*)\*(?!\*) \.\*(?!\*) asterisk/after_dot"
    "(?<!\*)\*(?!\*) (?<!^)(?<!\*)\*(?!\*|$) asterisk/middle"
    "(?<!^)(?<!\*)\*(?!\*|$) (?<!^)(?<!\*)/\*(?!\*|$) asterisk/middle_after_slash"
    "(?<!\*)\*(?!\*) (?<!\*)\*$ asterisk/trailing"
    "(?<!\*)\*(?!\*) (?<=/)(?<!\*)\*$ asterisk/directory_or_file multi ^\*$"
    "(?<!\*)\*(?!\*) ^\*(?!\*)(?=/) asterisk/directory multi (?<=[\!/])(?<!\*)\*(?!\*)(?=/)"
    "(?<!\*)\*(?!\*) (?<!\*)\*(?!\*) asterisk/character (?<=/)(?<!\*)\*$ ^\*$ ^\*(?!\*)(?=/) (?<=[\!/])(?<!\*)\*(?!\*)(?=/)"
    "(?<!\*)\*\*(?!\*) ^\*\*/ globstar/all_directories"
    "^\*\*/ ^\*\*/[^/]+/[^/] globstar/all_directories_normal"
    "(?<!\*)\*\*(?!\*) /\*\*$ globstar/all_files_in_directory"
    "/\*\*$ ^\!.*/\*\*$ globstar/all_files_in_directory_negation"
    "(?<!\*)\*\*(?!\*) /\*\*/ globstar/zero_or_more_directories"
    "(?<!\*)\*\*(?!\*) \*\* globstar/others ^\*\*/ /\*\*$ /\*\*/"
)

rm -rf "./pattern_usage_2/**"

echo "--------------------------------"
for arg in "${args[@]}"
do
    python3 ./pattern_usage_2.py ../gitignore_dataset/ignores ${arg}
    echo "--------------------------------"
done

dirs=()
for arg in "${args[@]}"
do
    arg_list=(${arg})
    dirs+=${arg_list[2]}
    dirs+=" "
done
python3 ./pattern_usage_2.py ../gitignore_dataset/ignores sum ${dirs}