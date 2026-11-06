LOG FILE ANALYZER TEST PACK

Large files: server.log (1200 lines), database.log (850), application.log (650), security.log (400).
Small files: edge_cases.log (8 lines), empty.log (0), invalid_utf8.log (invalid encoding).

Use the four large files together for a 3100-line stress test.
Input: server.log database.log application.log security.log
Filter: ALL; display limit: 10; keyword: blank; start/end: blank; threshold: 3.

To test missing-file handling, add missing.log in the middle of the filenames. Do not create missing.log.

To test known exact counts, use edge_cases.log alone:
Total 8; INFO 1; WARNING 1; ERROR 3; Unknown 1; Unparsed 2.
At threshold 2, 2026-11-05 14:20 is a spike with 3 errors.
At threshold 3, there should be no spike.

Expected per-file totals for large files are in expected_counts.csv.

Run the analyzer from this folder, or provide full file paths.
Note: paths with spaces are not supported by the current filename split() implementation.
