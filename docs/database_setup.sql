-- Execute como root do MySQL. Troque TROQUE_ESTA_SENHA por senhas longas e aleatórias (32+ caracteres).
-- Prefira senhas só com letras e números para evitar problemas de escape.

-- LOCAL
CREATE DATABASE IF NOT EXISTS compre_dev CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'compre_dev_app'@'localhost' IDENTIFIED BY 'TROQUE_ESTA_SENHA';
GRANT ALL PRIVILEGES ON compre_dev.* TO 'compre_dev_app'@'localhost';

-- HOMOLOGAÇÃO (as bases compre_hml e compre já existem; crie só os usuários dedicados)
-- CREATE USER IF NOT EXISTS 'compre_hml_app'@'localhost' IDENTIFIED BY 'TROQUE_ESTA_SENHA';
-- GRANT ALL PRIVILEGES ON compre_hml.* TO 'compre_hml_app'@'localhost';

-- PRODUÇÃO
-- CREATE USER IF NOT EXISTS 'compre_app'@'localhost' IDENTIFIED BY 'TROQUE_ESTA_SENHA';
-- GRANT ALL PRIVILEGES ON compre.* TO 'compre_app'@'localhost';

-- Nota: ALL PRIVILEGES permite o Alembic alterar tabelas. Endurecimento futuro: separar um usuário
-- de migrations (DDL) de um usuário de execução da API (somente SELECT/INSERT/UPDATE/DELETE).
-- O usuário app_user atual: confira o que ele acessa com  SHOW GRANTS FOR 'app_user'@'localhost';
FLUSH PRIVILEGES;
