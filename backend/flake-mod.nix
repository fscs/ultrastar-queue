{ inputs, lib, ... }:
{
  perSystem =
    { pkgs, ... }:
    let
      poetry2nix = inputs.poetry2nix.lib.mkPoetry2Nix { inherit pkgs; };
    in
    {
      packages.backend = poetry2nix.mkPoetryApplication {
        projectDir = ./.;

        python = pkgs.python312;
        overrides = poetry2nix.overrides.withDefaults (
          final: prev: {
            tinytag = pkgs.python312Packages.tinytag;
          }
        );

        nativeBuildInputs = [ pkgs.makeWrapper ];

        postInstall = ''
          srcPath="$out/lib/python3.12/site-packages/src"

          cp ${./alembic.ini} $srcPath/alembic.ini

          substituteInPlace $srcPath/alembic.ini \
            --replace "src/alembic" "$srcPath/alembic"

            wrapProgram $out/bin/ultrastar-queue-backend \
              --set ALEMBIC_CONFIG_PATH $srcPath/alembic.ini
        '';

        meta.mainProgram = "ultrastar-queue-backend";
      };
    };
}
