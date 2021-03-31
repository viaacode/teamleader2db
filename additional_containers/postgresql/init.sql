CREATE TABLE IF NOT EXISTS entities(
    id serial PRIMARY KEY,
    ldap_entryuuid uuid NOT NULL UNIQUE,
    type VARCHAR,
    ldap_content jsonb,
    ldap_modifytimestamp timestamp with time zone,
    created_at timestamp with time zone NOT NULL DEFAULT now(),
    updated_at timestamp with time zone NOT NULL DEFAULT now()
);

