{ outputs }:
{ lib
, pkgs
, config
, ...
}:
{
  options.services.ultrastar-queue =
    let
      t = lib.types;
    in
    {
      enable = lib.mkEnableOption "enable the ultrastar queue manager";

      backend = {
        src = lib.mkOption {
          description = "source of the backend";
          type = t.nullOr t.str;
          default = null;
        };

        devShell = lib.mkOption {
          description = "nix-shell to run the backend";
          type = t.nullOr t.nonEmptyStr;
          default = null;
        };

        environmentFile = lib.mkOption {
          description = "environment file to load into the systemd service";
          type = t.nullOr t.nonEmptyStr;
          default = null;
        };

        host = lib.mkOption {
          description = "host address to bind to";
          type = t.nonEmptyStr;
          default = "0.0.0.0";
        };

        port = lib.mkOption {
          description = "port to bind to";
          type = t.port;
          default = 8080;
        };

        databaseUrl = lib.mkOption {
          description = "URL to the database";
          type = t.nonEmptyStr;
        };

        JWTSecret = lib.mkOption {
          description = "secret key for JWT";
          type = t.nonEmptyStr;
        };

        ultraStarSongDir = lib.mkOption {
          description = "directory containing the Ultrastar songs";
          type = t.nonEmptyStr;
        };

        adminUser = lib.mkOption {
          description = "username of the admin user";
          type = t.nonEmptyStr;
        };

        adminPassword = lib.mkOption {
          description = "password of the admin user";
          type = t.nonEmptyStr;
        };
      };
    };

  config =
    let
      cfgB = config.services.ultrastar-queue.backend;
    in
    lib.mkIf cfgB.enable {
      users.groups.ultrastar-queue = { };
      users.users.ultrastar-queue = {
        isSystemUser = true;
        group = "ultrastar-queue";
      };

      systemd.services.ultrastar-queue = {
        after = [ "network.target" ];
        wantedBy = [ "multi-user.target" ];
        preStart = ''
          mkdir /var/lib/ultraStarQueue
          cp -r ${cfgB.src} /var/lib/ultraStarQueue
          chown -R ${config.users.users.ultrastar-queue.name}:${config.users.groups.ultrastar-queue.name} /var/lib/ultraStarQueue
          cd /var/lib/ultraStarQueue
          alembic upgrade head
        '';
        serviceConfig = {
          environment = {
            DATABASE_URL = cfgB.databaseUrl;
            JWT_SIGNING_SECRET_KEY = cfgB.JWTSecret;
            PATH_TO_ULTRASTAR_SONG_DIR = cfgB.ultraStarSongDir;
            ADMIN_USERNAME = cfgB.adminUser;
            ADMIN_PASSWORD = cfgB.adminPassword;
          };
          EnvironmentFile = cfgB.environmentFile;
          ExecStart = "cd /var/lib/ultraStarQueue && /usr/bin/env nix-shell ${cfgB.devShell}";
          Type = "exec";
          User = config.users.users.ultrastar-queue.name;
          Restart = "always";
          RestartSec = 5;
          CapabilityBoundingSet = [ "" ];
          DeviceAllow = [ "" ];
          DevicePolicy = "closed";
          LockPersonality = true;
          MemoryDenyWriteExecute = true;
          NoNewPrivileges = true;
          PrivateDevices = true;
          PrivateTmp = true;
          PrivateUsers = true;
          ProcSubset = "pid";
          ProtectClock = true;
          ProtectControlGroups = true;
          ProtectHome = true;
          ProtectHostname = true;
          ProtectKernelLogs = true;
          ProtectKernelModules = true;
          ProtectKernelTunables = true;
          ProtectProc = "noaccess";
          ProtectSystem = "strict";
          RemoveIPC = true;
          RestrictAddressFamilies = [
            "AF_INET"
            "AF_INET6"
            "AF_UNIX"
          ];
          RestrictNamespaces = true;
          RestrictRealtime = true;
          RestrictSUIDSGID = true;
          SystemCallArchitectures = "native";
          SystemCallFilter = [
            "@system-service"
            "~@privileged"
          ];
          UMask = "0077";
        };
      };
    };
}

