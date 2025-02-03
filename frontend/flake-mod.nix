{ lib, ... }:
{
  perSystem =
    { pkgs, ... }:
    {
      packages.frontend = pkgs.buildNpmPackage rec {
        pname = "ultrastar-queue-frontend";
        version = "0.0.1";

        src = ./.;

        npmDepsHash = "sha256-s9bJv1YS3qqsDFL9UbnRRbBRh7rKpt5qJ8H0szRhz9I=";

        installPhase = ''
          installPath="$out/lib/node_modules/${pname}"
          mkdir -p $(dirname $installPath)

          cp -r build $installPath
          cp -r package*.json $installPath

          mkdir $out/bin

          cat << EOF > $out/bin/${pname}
          #!/usr/bin/env bash
          ${lib.getExe pkgs.nodejs_20} $installPath
          EOF

          chmod +x $out/bin/${pname}
        '';

        meta.mainProgram = pname;
      };

      devShells.frontend = pkgs.mkShell {
        nativeBuildInputs = with pkgs; [
          nodejs
          prefetch-npm-deps
        ];
      };
    };
}
