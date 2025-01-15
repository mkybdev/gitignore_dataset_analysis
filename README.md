# gitignore_dataset_analysis

Analysis programs for [gitignore_dataset](https://github.com/mkybdev/gitignore_dataset) and [refactorign](https://github.com/mkybdev/refactorign)

## Reproduction

Make sure that gitignore_dataset is located **one level above** and refactorign is installed.

### Ignore Files Behavior

For .gitignore, .npmignore, and .dockerignore, the results of applying each file to the same directory structure can be compared.

1. Move to the directory of which ignore file you want to test. (e.g. ``./ignore-test/gitignore-test``)

2. Run ``test.sh``, which shows the paths of files that are not ignored.

    As for .gitignore, ``test.sh`` will show ignored files.
    In addition, note that the content of .gitignore is commented out so that the directory structure is retained.
    Please uncomment it out.

### Metacharacter Usage Analysis

Run ``pattern_usage.sh`` and ``pattern_usage_2.sh`` to analyze the frequency of some metacharacters.

Results are saved to ``./pattern_usage`` and ``./pattern_usage_2`` for each metacharacter.

```bash
bash pattern_usage.sh
bash pattern_usage_2.sh
```

### Refactoring Algorithm

1. Run ``generate.py`` to run refactorign for each .gitignore in the dataset and generate required information.

    Generated data is saved to ``./result``.

    ```bash
    python3 generate.py [TARGET_ID]
    ```

2. Run ``inspection.py`` to generate graphs, calculate statistics.

    Graphs are saved to ``./inspection``.

    ```bash
    python3 inspection.py
    ```

    Some of the results are cached to .pkl file.

3. Run ``validate.py`` to validate generated (refactored) .gitignores, checking whether they perform the same as their original ones.

    ```bash
    python3 validate.py [TARGET_ID]
    ```