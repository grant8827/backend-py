"""
Custom migration for social_django to handle UUID user foreign keys
"""

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    initial = True
    
    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Create social_auth_association table with UUID user_id
            CREATE TABLE IF NOT EXISTS "social_auth_association" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "server_url" varchar(255) NOT NULL,
                "handle" varchar(255) NOT NULL,
                "secret" varchar(255) NOT NULL,
                "issued" integer NOT NULL,
                "lifetime" integer NOT NULL,
                "assoc_type" varchar(64) NOT NULL
            );

            -- Create social_auth_code table
            CREATE TABLE IF NOT EXISTS "social_auth_code" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "email" varchar(254) NOT NULL,
                "code" varchar(32) NOT NULL,
                "verified" boolean NOT NULL,
                "timestamp" timestamptz NOT NULL
            );

            -- Create social_auth_nonce table
            CREATE TABLE IF NOT EXISTS "social_auth_nonce" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "server_url" varchar(255) NOT NULL,
                "timestamp" integer NOT NULL,
                "salt" varchar(65) NOT NULL
            );

            -- Create social_auth_partial table
            CREATE TABLE IF NOT EXISTS "social_auth_partial" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "token" varchar(32) NOT NULL,
                "next_step" smallint NOT NULL,
                "backend" varchar(32) NOT NULL,
                "timestamp" timestamptz NOT NULL,
                "data" text NOT NULL
            );

            -- Create social_auth_usersocialauth table with UUID user_id
            CREATE TABLE IF NOT EXISTS "social_auth_usersocialauth" (
                "id" bigserial NOT NULL PRIMARY KEY,
                "provider" varchar(32) NOT NULL,
                "uid" varchar(255) NOT NULL,
                "extra_data" text NOT NULL,
                "user_id" uuid NOT NULL,
                "created" timestamptz NOT NULL DEFAULT NOW(),
                "modified" timestamptz NOT NULL DEFAULT NOW()
            );

            -- Create indexes
            CREATE INDEX IF NOT EXISTS "social_auth_association_server_url_handle_078befa2_uniq" 
                ON "social_auth_association" ("server_url", "handle");
            CREATE INDEX IF NOT EXISTS "social_auth_code_email_801b2d02" 
                ON "social_auth_code" ("email");
            CREATE INDEX IF NOT EXISTS "social_auth_code_code_a2393167" 
                ON "social_auth_code" ("code");
            CREATE INDEX IF NOT EXISTS "social_auth_code_timestamp_176b341f" 
                ON "social_auth_code" ("timestamp");
            CREATE INDEX IF NOT EXISTS "social_auth_nonce_server_url_f6284463" 
                ON "social_auth_nonce" ("server_url");
            CREATE INDEX IF NOT EXISTS "social_auth_nonce_timestamp_50f47845" 
                ON "social_auth_nonce" ("timestamp");
            CREATE INDEX IF NOT EXISTS "social_auth_partial_token_3017fea3" 
                ON "social_auth_partial" ("token");
            CREATE INDEX IF NOT EXISTS "social_auth_partial_timestamp_50f47845" 
                ON "social_auth_partial" ("timestamp");
            CREATE INDEX IF NOT EXISTS "social_auth_usersocialauth_provider_e6b5e668" 
                ON "social_auth_usersocialauth" ("provider");
            CREATE INDEX IF NOT EXISTS "social_auth_usersocialauth_user_id_17d28448" 
                ON "social_auth_usersocialauth" ("user_id");

            -- Create unique constraints
            CREATE UNIQUE INDEX IF NOT EXISTS "social_auth_usersocialauth_provider_uid_e6b5e668_uniq" 
                ON "social_auth_usersocialauth" ("provider", "uid");

            -- Add foreign key constraint to users table with UUID
            ALTER TABLE "social_auth_usersocialauth" 
                DROP CONSTRAINT IF EXISTS "social_auth_usersocialauth_user_id_17d28448_fk_users_id";
            
            ALTER TABLE "social_auth_usersocialauth" 
                ADD CONSTRAINT "social_auth_usersocialauth_user_id_17d28448_fk_users_id" 
                FOREIGN KEY ("user_id") REFERENCES "users" ("id") DEFERRABLE INITIALLY DEFERRED;
            """,
            reverse_sql="""
            DROP TABLE IF EXISTS "social_auth_association";
            DROP TABLE IF EXISTS "social_auth_code";  
            DROP TABLE IF EXISTS "social_auth_nonce";
            DROP TABLE IF EXISTS "social_auth_partial";
            DROP TABLE IF EXISTS "social_auth_usersocialauth";
            """
        ),
    ]