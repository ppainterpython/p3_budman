<!-- markdownlint-disable MD033 -->

# PyExcelBudget

## Introduction

A project to learn about Python logging capabilities. Thanks to James Murphy for  his great [Modern Python Logging](https://www.youtube.com/watch?v=9L77QExPmI0) video with the [125_moder_loggin](https://github.com/mCodingLLC/VideosSampleCode/tree/master/videos/135_modern_logging) example code.

## Notes on support for JSONC in Python

I want to be able to comment JSON config files. I don't know why python json still ignores that, but it does. So, I will try the solution found in [stackoverflow: How to parse json file with c-style comments?](https://stackoverflow.com/questions/29959191/how-to-parse-json-file-with-c-style-comments) The recommendation there is to use a cpython implementation for JSON5 called [PyJSON5](https://pyjson5.readthedocs.io/en/latest/) documented [here](https://pyjson5.readthedocs.io/en/latest/).
