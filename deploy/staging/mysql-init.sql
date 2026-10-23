-- Staging databases and accounts (CR-008). The application and the backup job connect only over TLS.
CREATE DATABASE IF NOT EXISTS syn_stg_django;
CREATE DATABASE IF NOT EXISTS syn_stg_platform;
CREATE DATABASE IF NOT EXISTS syn_stg_registry;
CREATE DATABASE IF NOT EXISTS syn_stg_ops;
CREATE DATABASE IF NOT EXISTS syn_stg_vault;
CREATE DATABASE IF NOT EXISTS syn_stg_records;
CREATE DATABASE IF NOT EXISTS syn_stg_dw;
CREATE USER IF NOT EXISTS 'syntegra'@'%' IDENTIFIED BY 'staging-db-password' REQUIRE SSL;
GRANT ALL PRIVILEGES ON `syn\_stg\_%`.* TO 'syntegra'@'%';
CREATE USER IF NOT EXISTS 'backup'@'%' IDENTIFIED BY 'staging-backup-password' REQUIRE SSL;
GRANT SELECT, SHOW VIEW, TRIGGER, EVENT, LOCK TABLES ON `syn\_stg\_%`.* TO 'backup'@'%';
