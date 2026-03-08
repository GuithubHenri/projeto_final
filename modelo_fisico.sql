BEGIN;
--
-- Create model Cliente
--
CREATE TABLE "app_cliente" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nome" varchar(100) NOT NULL, "email" varchar(254) NOT NULL, "telefone" varchar(20) NOT NULL, "criado_em" datetime NOT NULL, "usuario_id" integer NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Pedido
--
CREATE TABLE "app_pedido" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "codigo" varchar(20) NOT NULL UNIQUE, "status" varchar(20) NOT NULL, "origem" varchar(100) NOT NULL, "destino" varchar(100) NOT NULL, "criado_em" datetime NOT NULL, "atualizado_em" datetime NOT NULL, "cliente_id" bigint NOT NULL REFERENCES "app_cliente" ("id") DEFERRABLE INITIALLY DEFERRED, "responsavel_id" integer NULL REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model EventoRastreio
--
CREATE TABLE "app_eventorastreio" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "descricao" varchar(255) NOT NULL, "criado_em" datetime NOT NULL, "pedido_id" bigint NOT NULL REFERENCES "app_pedido" ("id") DEFERRABLE INITIALLY DEFERRED);
--
-- Create model Perfil
--
CREATE TABLE "app_perfil" ("id" integer NOT NULL PRIMARY KEY AUTOINCREMENT, "nivel" varchar(20) NOT NULL, "usuario_id" integer NOT NULL UNIQUE REFERENCES "auth_user" ("id") DEFERRABLE INITIALLY DEFERRED);
CREATE INDEX "app_pedido_cliente_id_e42e9f61" ON "app_pedido" ("cliente_id");
CREATE INDEX "app_pedido_responsavel_id_ace760f9" ON "app_pedido" ("responsavel_id");
CREATE INDEX "app_eventorastreio_pedido_id_bf1d4d0a" ON "app_eventorastreio" ("pedido_id");
COMMIT;