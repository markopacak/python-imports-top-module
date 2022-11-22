# Move Python imports to the top of the module

This is in experimental phase.

Move imports defined inside functions to the top of the module.

Inspired by [this Pandas script](https://github.com/MarcoGorelli/pandas/blob/standard-library-imports/scripts/standard_library_imports_should_be_global.py) from Marco Gorelli, 
this application aims to automate the refactoring of import statements.

## Usage

    python ./reorder-imports.py <root-folder-of-your-project>

E.g:  
    
    python ./reorder-imports.py /home/user/workspace/my-project


## Current issues

Multi-line imports are not refactored correctly.

