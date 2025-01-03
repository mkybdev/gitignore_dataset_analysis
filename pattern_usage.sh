args=(
    "\\\ escape"
    "^# comment"
    "^\! negation"
    "(?<!\\\)/ directory_separator/directory_separator" 
    "^.*/.+$ directory_separator/relative_path" 
    "^.*/$ directory_separator/only_directories"
    "(?<!\*)\*(?!\*) asterisk"
    "\? question_mark"
    "\[.+\] range"
    "(?<!\*)\*\*(?!\*) globstar/all"
    "^\*\*/ globstar/all_directories"
    "/\*\*$ globstar/all_files_in_directory"
    "/\*\*/ globstar/zero_or_more_directories"
    "\*\* globstar/others ^\*\*/ /\*\*$ /\*\*/"
)

rm -rf "./pattern_usage/**"

echo "--------------------------------"
for arg in "${args[@]}"
do
    python3 ./pattern_usage.py ${arg}
    echo "--------------------------------"
done

dirs=()
for arg in "${args[@]}"
do
    arg_list=(${arg})
    dirs+=${arg_list[1]}
    dirs+=" "
done
python3 ./pattern_usage.py sum ${dirs}