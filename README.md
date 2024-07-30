# BA Schaefer Code



## Getting started

- install the requirements from requirements.txt

## How to use (for manual testing)

### API
- run src/main.py
- test at http://127.0.0.1:8000/docs (no frontend added yet)

### Ultrastar file parser
- add path to dir with ultrastar song files at PATH_TO_ULTRASTAR_SONG_DIR in .env
  - song examples are included in song_examples
- run src/ultrastar_file/__init__.py

## Used Sources

- https://www.youtube.com/watch?v=vkEhatGH1kI
- https://arunanshub.hashnode.dev/async-database-operations-with-sqlmodel
- https://github.com/tiangolo/sqlmodel/issues/626
- https://sqlmodel.tiangolo.com/tutorial/
- https://github.com/jod35/lib-api
- https://github.com/jod35/fastapi-beyond-CRUD
- https://www.youtube.com/playlist?list=PL-2EBeDYMIbQghmnb865lpdmYyWU3I5F1
- https://usdx.eu/format/#specs
- https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
  - used for src/ultrastar_file/parser get_song_file_paths()
