{ lib, ... }:
{
  perSystem =
    { pkgs, ... }:
    {
      packages.backend = pkgs.python312Packages.buildPythonPackage rec {
        name = "ultrastar-queue-backend";
        version = "0.0.1";

        src = ./.;

        propagatedBuildInputs = with pkgs.python3Packages; [
          fastapi
          sqlmodel
          pydantic
          passlib
          pyjwt
          uvicorn
          sqlalchemy
          aiosqlite
          httpx
          pytest
          tinytag
          pydantic-settings
          alembic
          python
        ];

        meta.mainProgram = name;
      };
      devShells.backend = pkgs.mkShell {
        buildInputs = with pkgs; [
          python312
          python312Packages.virtualenv
          python312Packages.sqlmodel
          python312Packages.uvicorn
          python312Packages.fastapi
          python312Packages.pyjwt
          python312Packages.passlib
          python312Packages.pydantic-settings
          python312Packages.aiosqlite
          python312Packages.tinytag
          python312Packages.python-multipart
        ];

        shellHook = ''
          export DATABASE_URL=sqlite+aiosqlite:///db.sqlite
          export JWT_SIGNING_SECRET_KEY=secret
          export PATH_TO_ULTRASTAR_SONG_DIR=/home/felix/.ultrastardx/songs
          export ADMIN_USERNAME=knut
          export ADMIN_PASSWORD=knut
            echo "Starting Uvicorn..."
            exec uvicorn src.app.main:app --host 0.0.0.0 --port 8000
        '';
      };

    };
}
