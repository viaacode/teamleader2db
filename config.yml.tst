viaa:
  logging:
    level: DEBUG
app:
  teamleader:
    auth_uri: 'https://focus.teamleader.eu'
    api_uri: 'https://api.focus.teamleader.eu'
    client_id: 'fill_me_in'
    client_secret: 'fill_me_in'
    redirect_uri: 'https://public_openshift_route/sync/oauth'
    secret_code_state: 'code_to_validate_callback'
    code: 'code_from_callback'
    auth_token: 'valid_auth_token'
    refresh_token: 'valid_refresh_token'
  postgresql_teamleader:
    database: "avo_development"
    host: "pg_host"
    password: "postgres"
    user: "postgres"
    port: 5432
    sslmode: 'disable'
  table_names:
    oauth_table: 'tl_auth'
    companies_table: 'tl_companies'
    contacts_table: 'tl_contacts'
    departments_table: 'tl_departments'
    events_table: 'tl_events'
    invoices_table: 'tl_invoices'
    projects_table: 'tl_projects'
    users_table: 'tl_users'
    custom_fields_table: 'tl_custom_fields'
