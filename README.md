# gitignore_dataset_analysis

Analysis programs for [gitignore_dataset](https://github.com/mkybdev/gitignore_dataset) and [refactorign](https://github.com/mkybdev/refactorign)

## Reproduction

Make sure that gitignore_dataset is located **one level above** and refactorign is installed.

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

3. Run ``validate.py`` to validate generated (refactored) .gitignores, checking whether they perform the same as their original ones.

    ```bash
    python3 validate.py [TARGET_ID]
    ```