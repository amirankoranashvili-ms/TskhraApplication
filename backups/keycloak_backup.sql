--
-- PostgreSQL database dump
--

\restrict GFY7KexulMgJsyQzdfOYDaaHxVRB81u0Jyz9CR5zp9dKay95Ltj0PzvuYB7ahBG

-- Dumped from database version 16.11
-- Dumped by pg_dump version 16.11

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admin_event_entity; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.admin_event_entity (
    id character varying(36) NOT NULL,
    admin_event_time bigint,
    realm_id character varying(255),
    operation_type character varying(255),
    auth_realm_id character varying(255),
    auth_client_id character varying(255),
    auth_user_id character varying(255),
    ip_address character varying(255),
    resource_path character varying(2550),
    representation text,
    error character varying(255),
    resource_type character varying(64),
    details_json text
);


ALTER TABLE public.admin_event_entity OWNER TO admin;

--
-- Name: associated_policy; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.associated_policy (
    policy_id character varying(36) NOT NULL,
    associated_policy_id character varying(36) NOT NULL
);


ALTER TABLE public.associated_policy OWNER TO admin;

--
-- Name: authentication_execution; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.authentication_execution (
    id character varying(36) NOT NULL,
    alias character varying(255),
    authenticator character varying(36),
    realm_id character varying(36),
    flow_id character varying(36),
    requirement integer,
    priority integer,
    authenticator_flow boolean DEFAULT false NOT NULL,
    auth_flow_id character varying(36),
    auth_config character varying(36)
);


ALTER TABLE public.authentication_execution OWNER TO admin;

--
-- Name: authentication_flow; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.authentication_flow (
    id character varying(36) NOT NULL,
    alias character varying(255),
    description character varying(255),
    realm_id character varying(36),
    provider_id character varying(36) DEFAULT 'basic-flow'::character varying NOT NULL,
    top_level boolean DEFAULT false NOT NULL,
    built_in boolean DEFAULT false NOT NULL
);


ALTER TABLE public.authentication_flow OWNER TO admin;

--
-- Name: authenticator_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.authenticator_config (
    id character varying(36) NOT NULL,
    alias character varying(255),
    realm_id character varying(36)
);


ALTER TABLE public.authenticator_config OWNER TO admin;

--
-- Name: authenticator_config_entry; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.authenticator_config_entry (
    authenticator_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.authenticator_config_entry OWNER TO admin;

--
-- Name: broker_link; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.broker_link (
    identity_provider character varying(255) NOT NULL,
    storage_provider_id character varying(255),
    realm_id character varying(36) NOT NULL,
    broker_user_id character varying(255),
    broker_username character varying(255),
    token text,
    user_id character varying(255) NOT NULL
);


ALTER TABLE public.broker_link OWNER TO admin;

--
-- Name: client; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client (
    id character varying(36) NOT NULL,
    enabled boolean DEFAULT false NOT NULL,
    full_scope_allowed boolean DEFAULT false NOT NULL,
    client_id character varying(255),
    not_before integer,
    public_client boolean DEFAULT false NOT NULL,
    secret character varying(255),
    base_url character varying(255),
    bearer_only boolean DEFAULT false NOT NULL,
    management_url character varying(255),
    surrogate_auth_required boolean DEFAULT false NOT NULL,
    realm_id character varying(36),
    protocol character varying(255),
    node_rereg_timeout integer DEFAULT 0,
    frontchannel_logout boolean DEFAULT false NOT NULL,
    consent_required boolean DEFAULT false NOT NULL,
    name character varying(255),
    service_accounts_enabled boolean DEFAULT false NOT NULL,
    client_authenticator_type character varying(255),
    root_url character varying(255),
    description character varying(255),
    registration_token character varying(255),
    standard_flow_enabled boolean DEFAULT true NOT NULL,
    implicit_flow_enabled boolean DEFAULT false NOT NULL,
    direct_access_grants_enabled boolean DEFAULT false NOT NULL,
    always_display_in_console boolean DEFAULT false NOT NULL
);


ALTER TABLE public.client OWNER TO admin;

--
-- Name: client_attributes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_attributes (
    client_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value text
);


ALTER TABLE public.client_attributes OWNER TO admin;

--
-- Name: client_auth_flow_bindings; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_auth_flow_bindings (
    client_id character varying(36) NOT NULL,
    flow_id character varying(36),
    binding_name character varying(255) NOT NULL
);


ALTER TABLE public.client_auth_flow_bindings OWNER TO admin;

--
-- Name: client_initial_access; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_initial_access (
    id character varying(36) NOT NULL,
    realm_id character varying(36) NOT NULL,
    "timestamp" integer,
    expiration integer,
    count integer,
    remaining_count integer
);


ALTER TABLE public.client_initial_access OWNER TO admin;

--
-- Name: client_node_registrations; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_node_registrations (
    client_id character varying(36) NOT NULL,
    value integer,
    name character varying(255) NOT NULL
);


ALTER TABLE public.client_node_registrations OWNER TO admin;

--
-- Name: client_scope; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_scope (
    id character varying(36) NOT NULL,
    name character varying(255),
    realm_id character varying(36),
    description character varying(255),
    protocol character varying(255)
);


ALTER TABLE public.client_scope OWNER TO admin;

--
-- Name: client_scope_attributes; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_scope_attributes (
    scope_id character varying(36) NOT NULL,
    value character varying(2048),
    name character varying(255) NOT NULL
);


ALTER TABLE public.client_scope_attributes OWNER TO admin;

--
-- Name: client_scope_client; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_scope_client (
    client_id character varying(255) NOT NULL,
    scope_id character varying(255) NOT NULL,
    default_scope boolean DEFAULT false NOT NULL
);


ALTER TABLE public.client_scope_client OWNER TO admin;

--
-- Name: client_scope_role_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.client_scope_role_mapping (
    scope_id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL
);


ALTER TABLE public.client_scope_role_mapping OWNER TO admin;

--
-- Name: component; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.component (
    id character varying(36) NOT NULL,
    name character varying(255),
    parent_id character varying(36),
    provider_id character varying(36),
    provider_type character varying(255),
    realm_id character varying(36),
    sub_type character varying(255)
);


ALTER TABLE public.component OWNER TO admin;

--
-- Name: component_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.component_config (
    id character varying(36) NOT NULL,
    component_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value text
);


ALTER TABLE public.component_config OWNER TO admin;

--
-- Name: composite_role; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.composite_role (
    composite character varying(36) NOT NULL,
    child_role character varying(36) NOT NULL
);


ALTER TABLE public.composite_role OWNER TO admin;

--
-- Name: credential; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.credential (
    id character varying(36) NOT NULL,
    salt bytea,
    type character varying(255),
    user_id character varying(36),
    created_date bigint,
    user_label character varying(255),
    secret_data text,
    credential_data text,
    priority integer
);


ALTER TABLE public.credential OWNER TO admin;

--
-- Name: databasechangelog; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.databasechangelog (
    id character varying(255) NOT NULL,
    author character varying(255) NOT NULL,
    filename character varying(255) NOT NULL,
    dateexecuted timestamp without time zone NOT NULL,
    orderexecuted integer NOT NULL,
    exectype character varying(10) NOT NULL,
    md5sum character varying(35),
    description character varying(255),
    comments character varying(255),
    tag character varying(255),
    liquibase character varying(20),
    contexts character varying(255),
    labels character varying(255),
    deployment_id character varying(10)
);


ALTER TABLE public.databasechangelog OWNER TO admin;

--
-- Name: databasechangelog_ext_entity; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.databasechangelog_ext_entity (
    id character varying(255) NOT NULL,
    author character varying(255) NOT NULL,
    filename character varying(255) NOT NULL,
    dateexecuted timestamp without time zone NOT NULL,
    orderexecuted integer NOT NULL,
    exectype character varying(10) NOT NULL,
    md5sum character varying(35),
    description character varying(255),
    comments character varying(255),
    tag character varying(255),
    liquibase character varying(20),
    contexts character varying(255),
    labels character varying(255),
    deployment_id character varying(10)
);


ALTER TABLE public.databasechangelog_ext_entity OWNER TO admin;

--
-- Name: databasechangeloglock; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.databasechangeloglock (
    id integer NOT NULL,
    locked boolean NOT NULL,
    lockgranted timestamp without time zone,
    lockedby character varying(255)
);


ALTER TABLE public.databasechangeloglock OWNER TO admin;

--
-- Name: default_client_scope; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.default_client_scope (
    realm_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL,
    default_scope boolean DEFAULT false NOT NULL
);


ALTER TABLE public.default_client_scope OWNER TO admin;

--
-- Name: event_entity; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.event_entity (
    id character varying(36) NOT NULL,
    client_id character varying(255),
    details_json character varying(2550),
    error character varying(255),
    ip_address character varying(255),
    realm_id character varying(255),
    session_id character varying(255),
    event_time bigint,
    type character varying(255),
    user_id character varying(255),
    details_json_long_value text
);


ALTER TABLE public.event_entity OWNER TO admin;

--
-- Name: fed_user_attribute; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_attribute (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36),
    value character varying(2024),
    long_value_hash bytea,
    long_value_hash_lower_case bytea,
    long_value text
);


ALTER TABLE public.fed_user_attribute OWNER TO admin;

--
-- Name: fed_user_consent; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_consent (
    id character varying(36) NOT NULL,
    client_id character varying(255),
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36),
    created_date bigint,
    last_updated_date bigint,
    client_storage_provider character varying(36),
    external_client_id character varying(255)
);


ALTER TABLE public.fed_user_consent OWNER TO admin;

--
-- Name: fed_user_consent_cl_scope; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_consent_cl_scope (
    user_consent_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL
);


ALTER TABLE public.fed_user_consent_cl_scope OWNER TO admin;

--
-- Name: fed_user_credential; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_credential (
    id character varying(36) NOT NULL,
    salt bytea,
    type character varying(255),
    created_date bigint,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36),
    user_label character varying(255),
    secret_data text,
    credential_data text,
    priority integer
);


ALTER TABLE public.fed_user_credential OWNER TO admin;

--
-- Name: fed_user_group_membership; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_group_membership (
    group_id character varying(36) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36)
);


ALTER TABLE public.fed_user_group_membership OWNER TO admin;

--
-- Name: fed_user_required_action; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_required_action (
    required_action character varying(255) DEFAULT ' '::character varying NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36)
);


ALTER TABLE public.fed_user_required_action OWNER TO admin;

--
-- Name: fed_user_role_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.fed_user_role_mapping (
    role_id character varying(36) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    storage_provider_id character varying(36)
);


ALTER TABLE public.fed_user_role_mapping OWNER TO admin;

--
-- Name: federated_identity; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.federated_identity (
    identity_provider character varying(255) NOT NULL,
    realm_id character varying(36),
    federated_user_id character varying(255),
    federated_username character varying(255),
    token text,
    user_id character varying(36) NOT NULL
);


ALTER TABLE public.federated_identity OWNER TO admin;

--
-- Name: federated_user; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.federated_user (
    id character varying(255) NOT NULL,
    storage_provider_id character varying(255),
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.federated_user OWNER TO admin;

--
-- Name: group_attribute; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.group_attribute (
    id character varying(36) DEFAULT 'sybase-needs-something-here'::character varying NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(255),
    group_id character varying(36) NOT NULL
);


ALTER TABLE public.group_attribute OWNER TO admin;

--
-- Name: group_role_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.group_role_mapping (
    role_id character varying(36) NOT NULL,
    group_id character varying(36) NOT NULL
);


ALTER TABLE public.group_role_mapping OWNER TO admin;

--
-- Name: identity_provider; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.identity_provider (
    internal_id character varying(36) NOT NULL,
    enabled boolean DEFAULT false NOT NULL,
    provider_alias character varying(255),
    provider_id character varying(255),
    store_token boolean DEFAULT false NOT NULL,
    authenticate_by_default boolean DEFAULT false NOT NULL,
    realm_id character varying(36),
    add_token_role boolean DEFAULT true NOT NULL,
    trust_email boolean DEFAULT false NOT NULL,
    first_broker_login_flow_id character varying(36),
    post_broker_login_flow_id character varying(36),
    provider_display_name character varying(255),
    link_only boolean DEFAULT false NOT NULL,
    organization_id character varying(255),
    hide_on_login boolean DEFAULT false
);


ALTER TABLE public.identity_provider OWNER TO admin;

--
-- Name: identity_provider_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.identity_provider_config (
    identity_provider_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.identity_provider_config OWNER TO admin;

--
-- Name: identity_provider_mapper; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.identity_provider_mapper (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    idp_alias character varying(255) NOT NULL,
    idp_mapper_name character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.identity_provider_mapper OWNER TO admin;

--
-- Name: idp_mapper_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.idp_mapper_config (
    idp_mapper_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.idp_mapper_config OWNER TO admin;

--
-- Name: jgroups_ping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.jgroups_ping (
    address character varying(200) NOT NULL,
    name character varying(200),
    cluster_name character varying(200) NOT NULL,
    ip character varying(200) NOT NULL,
    coord boolean
);


ALTER TABLE public.jgroups_ping OWNER TO admin;

--
-- Name: keycloak_group; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.keycloak_group (
    id character varying(36) NOT NULL,
    name character varying(255),
    parent_group character varying(36) NOT NULL,
    realm_id character varying(36),
    type integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.keycloak_group OWNER TO admin;

--
-- Name: keycloak_role; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.keycloak_role (
    id character varying(36) NOT NULL,
    client_realm_constraint character varying(255),
    client_role boolean DEFAULT false NOT NULL,
    description character varying(255),
    name character varying(255),
    realm_id character varying(255),
    client character varying(36),
    realm character varying(36)
);


ALTER TABLE public.keycloak_role OWNER TO admin;

--
-- Name: migration_model; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.migration_model (
    id character varying(36) NOT NULL,
    version character varying(36),
    update_time bigint DEFAULT 0 NOT NULL
);


ALTER TABLE public.migration_model OWNER TO admin;

--
-- Name: offline_client_session; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.offline_client_session (
    user_session_id character varying(36) NOT NULL,
    client_id character varying(255) NOT NULL,
    offline_flag character varying(4) NOT NULL,
    "timestamp" integer,
    data text,
    client_storage_provider character varying(36) DEFAULT 'local'::character varying NOT NULL,
    external_client_id character varying(255) DEFAULT 'local'::character varying NOT NULL,
    version integer DEFAULT 0
);


ALTER TABLE public.offline_client_session OWNER TO admin;

--
-- Name: offline_user_session; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.offline_user_session (
    user_session_id character varying(36) NOT NULL,
    user_id character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    created_on integer NOT NULL,
    offline_flag character varying(4) NOT NULL,
    data text,
    last_session_refresh integer DEFAULT 0 NOT NULL,
    broker_session_id character varying(1024),
    version integer DEFAULT 0
);


ALTER TABLE public.offline_user_session OWNER TO admin;

--
-- Name: org; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.org (
    id character varying(255) NOT NULL,
    enabled boolean NOT NULL,
    realm_id character varying(255) NOT NULL,
    group_id character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(4000),
    alias character varying(255) NOT NULL,
    redirect_url character varying(2048)
);


ALTER TABLE public.org OWNER TO admin;

--
-- Name: org_domain; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.org_domain (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    verified boolean NOT NULL,
    org_id character varying(255) NOT NULL
);


ALTER TABLE public.org_domain OWNER TO admin;

--
-- Name: policy_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.policy_config (
    policy_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value text
);


ALTER TABLE public.policy_config OWNER TO admin;

--
-- Name: protocol_mapper; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.protocol_mapper (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    protocol character varying(255) NOT NULL,
    protocol_mapper_name character varying(255) NOT NULL,
    client_id character varying(36),
    client_scope_id character varying(36)
);


ALTER TABLE public.protocol_mapper OWNER TO admin;

--
-- Name: protocol_mapper_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.protocol_mapper_config (
    protocol_mapper_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.protocol_mapper_config OWNER TO admin;

--
-- Name: realm; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm (
    id character varying(36) NOT NULL,
    access_code_lifespan integer,
    user_action_lifespan integer,
    access_token_lifespan integer,
    account_theme character varying(255),
    admin_theme character varying(255),
    email_theme character varying(255),
    enabled boolean DEFAULT false NOT NULL,
    events_enabled boolean DEFAULT false NOT NULL,
    events_expiration bigint,
    login_theme character varying(255),
    name character varying(255),
    not_before integer,
    password_policy character varying(2550),
    registration_allowed boolean DEFAULT false NOT NULL,
    remember_me boolean DEFAULT false NOT NULL,
    reset_password_allowed boolean DEFAULT false NOT NULL,
    social boolean DEFAULT false NOT NULL,
    ssl_required character varying(255),
    sso_idle_timeout integer,
    sso_max_lifespan integer,
    update_profile_on_soc_login boolean DEFAULT false NOT NULL,
    verify_email boolean DEFAULT false NOT NULL,
    master_admin_client character varying(36),
    login_lifespan integer,
    internationalization_enabled boolean DEFAULT false NOT NULL,
    default_locale character varying(255),
    reg_email_as_username boolean DEFAULT false NOT NULL,
    admin_events_enabled boolean DEFAULT false NOT NULL,
    admin_events_details_enabled boolean DEFAULT false NOT NULL,
    edit_username_allowed boolean DEFAULT false NOT NULL,
    otp_policy_counter integer DEFAULT 0,
    otp_policy_window integer DEFAULT 1,
    otp_policy_period integer DEFAULT 30,
    otp_policy_digits integer DEFAULT 6,
    otp_policy_alg character varying(36) DEFAULT 'HmacSHA1'::character varying,
    otp_policy_type character varying(36) DEFAULT 'totp'::character varying,
    browser_flow character varying(36),
    registration_flow character varying(36),
    direct_grant_flow character varying(36),
    reset_credentials_flow character varying(36),
    client_auth_flow character varying(36),
    offline_session_idle_timeout integer DEFAULT 0,
    revoke_refresh_token boolean DEFAULT false NOT NULL,
    access_token_life_implicit integer DEFAULT 0,
    login_with_email_allowed boolean DEFAULT true NOT NULL,
    duplicate_emails_allowed boolean DEFAULT false NOT NULL,
    docker_auth_flow character varying(36),
    refresh_token_max_reuse integer DEFAULT 0,
    allow_user_managed_access boolean DEFAULT false NOT NULL,
    sso_max_lifespan_remember_me integer DEFAULT 0 NOT NULL,
    sso_idle_timeout_remember_me integer DEFAULT 0 NOT NULL,
    default_role character varying(255)
);


ALTER TABLE public.realm OWNER TO admin;

--
-- Name: realm_attribute; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_attribute (
    name character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL,
    value text
);


ALTER TABLE public.realm_attribute OWNER TO admin;

--
-- Name: realm_default_groups; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_default_groups (
    realm_id character varying(36) NOT NULL,
    group_id character varying(36) NOT NULL
);


ALTER TABLE public.realm_default_groups OWNER TO admin;

--
-- Name: realm_enabled_event_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_enabled_event_types (
    realm_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.realm_enabled_event_types OWNER TO admin;

--
-- Name: realm_events_listeners; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_events_listeners (
    realm_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.realm_events_listeners OWNER TO admin;

--
-- Name: realm_localizations; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_localizations (
    realm_id character varying(255) NOT NULL,
    locale character varying(255) NOT NULL,
    texts text NOT NULL
);


ALTER TABLE public.realm_localizations OWNER TO admin;

--
-- Name: realm_required_credential; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_required_credential (
    type character varying(255) NOT NULL,
    form_label character varying(255),
    input boolean DEFAULT false NOT NULL,
    secret boolean DEFAULT false NOT NULL,
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.realm_required_credential OWNER TO admin;

--
-- Name: realm_smtp_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_smtp_config (
    realm_id character varying(36) NOT NULL,
    value character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.realm_smtp_config OWNER TO admin;

--
-- Name: realm_supported_locales; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.realm_supported_locales (
    realm_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.realm_supported_locales OWNER TO admin;

--
-- Name: redirect_uris; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.redirect_uris (
    client_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.redirect_uris OWNER TO admin;

--
-- Name: required_action_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.required_action_config (
    required_action_id character varying(36) NOT NULL,
    value text,
    name character varying(255) NOT NULL
);


ALTER TABLE public.required_action_config OWNER TO admin;

--
-- Name: required_action_provider; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.required_action_provider (
    id character varying(36) NOT NULL,
    alias character varying(255),
    name character varying(255),
    realm_id character varying(36),
    enabled boolean DEFAULT false NOT NULL,
    default_action boolean DEFAULT false NOT NULL,
    provider_id character varying(255),
    priority integer
);


ALTER TABLE public.required_action_provider OWNER TO admin;

--
-- Name: resource_attribute; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_attribute (
    id character varying(36) DEFAULT 'sybase-needs-something-here'::character varying NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(255),
    resource_id character varying(36) NOT NULL
);


ALTER TABLE public.resource_attribute OWNER TO admin;

--
-- Name: resource_policy; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_policy (
    resource_id character varying(36) NOT NULL,
    policy_id character varying(36) NOT NULL
);


ALTER TABLE public.resource_policy OWNER TO admin;

--
-- Name: resource_scope; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_scope (
    resource_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL
);


ALTER TABLE public.resource_scope OWNER TO admin;

--
-- Name: resource_server; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_server (
    id character varying(36) NOT NULL,
    allow_rs_remote_mgmt boolean DEFAULT false NOT NULL,
    policy_enforce_mode smallint NOT NULL,
    decision_strategy smallint DEFAULT 1 NOT NULL
);


ALTER TABLE public.resource_server OWNER TO admin;

--
-- Name: resource_server_perm_ticket; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_server_perm_ticket (
    id character varying(36) NOT NULL,
    owner character varying(255) NOT NULL,
    requester character varying(255) NOT NULL,
    created_timestamp bigint NOT NULL,
    granted_timestamp bigint,
    resource_id character varying(36) NOT NULL,
    scope_id character varying(36),
    resource_server_id character varying(36) NOT NULL,
    policy_id character varying(36)
);


ALTER TABLE public.resource_server_perm_ticket OWNER TO admin;

--
-- Name: resource_server_policy; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_server_policy (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    description character varying(255),
    type character varying(255) NOT NULL,
    decision_strategy smallint,
    logic smallint,
    resource_server_id character varying(36) NOT NULL,
    owner character varying(255)
);


ALTER TABLE public.resource_server_policy OWNER TO admin;

--
-- Name: resource_server_resource; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_server_resource (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    type character varying(255),
    icon_uri character varying(255),
    owner character varying(255) NOT NULL,
    resource_server_id character varying(36) NOT NULL,
    owner_managed_access boolean DEFAULT false NOT NULL,
    display_name character varying(255)
);


ALTER TABLE public.resource_server_resource OWNER TO admin;

--
-- Name: resource_server_scope; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_server_scope (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    icon_uri character varying(255),
    resource_server_id character varying(36) NOT NULL,
    display_name character varying(255)
);


ALTER TABLE public.resource_server_scope OWNER TO admin;

--
-- Name: resource_uris; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.resource_uris (
    resource_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.resource_uris OWNER TO admin;

--
-- Name: revoked_token; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.revoked_token (
    id character varying(255) NOT NULL,
    expire bigint NOT NULL
);


ALTER TABLE public.revoked_token OWNER TO admin;

--
-- Name: role_attribute; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.role_attribute (
    id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    value character varying(255)
);


ALTER TABLE public.role_attribute OWNER TO admin;

--
-- Name: scope_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.scope_mapping (
    client_id character varying(36) NOT NULL,
    role_id character varying(36) NOT NULL
);


ALTER TABLE public.scope_mapping OWNER TO admin;

--
-- Name: scope_policy; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.scope_policy (
    scope_id character varying(36) NOT NULL,
    policy_id character varying(36) NOT NULL
);


ALTER TABLE public.scope_policy OWNER TO admin;

--
-- Name: user_attribute; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_attribute (
    name character varying(255) NOT NULL,
    value character varying(255),
    user_id character varying(36) NOT NULL,
    id character varying(36) DEFAULT 'sybase-needs-something-here'::character varying NOT NULL,
    long_value_hash bytea,
    long_value_hash_lower_case bytea,
    long_value text
);


ALTER TABLE public.user_attribute OWNER TO admin;

--
-- Name: user_consent; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_consent (
    id character varying(36) NOT NULL,
    client_id character varying(255),
    user_id character varying(36) NOT NULL,
    created_date bigint,
    last_updated_date bigint,
    client_storage_provider character varying(36),
    external_client_id character varying(255)
);


ALTER TABLE public.user_consent OWNER TO admin;

--
-- Name: user_consent_client_scope; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_consent_client_scope (
    user_consent_id character varying(36) NOT NULL,
    scope_id character varying(36) NOT NULL
);


ALTER TABLE public.user_consent_client_scope OWNER TO admin;

--
-- Name: user_entity; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_entity (
    id character varying(36) NOT NULL,
    email character varying(255),
    email_constraint character varying(255),
    email_verified boolean DEFAULT false NOT NULL,
    enabled boolean DEFAULT false NOT NULL,
    federation_link character varying(255),
    first_name character varying(255),
    last_name character varying(255),
    realm_id character varying(255),
    username character varying(255),
    created_timestamp bigint,
    service_account_client_link character varying(255),
    not_before integer DEFAULT 0 NOT NULL
);


ALTER TABLE public.user_entity OWNER TO admin;

--
-- Name: user_federation_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_federation_config (
    user_federation_provider_id character varying(36) NOT NULL,
    value character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.user_federation_config OWNER TO admin;

--
-- Name: user_federation_mapper; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_federation_mapper (
    id character varying(36) NOT NULL,
    name character varying(255) NOT NULL,
    federation_provider_id character varying(36) NOT NULL,
    federation_mapper_type character varying(255) NOT NULL,
    realm_id character varying(36) NOT NULL
);


ALTER TABLE public.user_federation_mapper OWNER TO admin;

--
-- Name: user_federation_mapper_config; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_federation_mapper_config (
    user_federation_mapper_id character varying(36) NOT NULL,
    value character varying(255),
    name character varying(255) NOT NULL
);


ALTER TABLE public.user_federation_mapper_config OWNER TO admin;

--
-- Name: user_federation_provider; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_federation_provider (
    id character varying(36) NOT NULL,
    changed_sync_period integer,
    display_name character varying(255),
    full_sync_period integer,
    last_sync integer,
    priority integer,
    provider_name character varying(255),
    realm_id character varying(36)
);


ALTER TABLE public.user_federation_provider OWNER TO admin;

--
-- Name: user_group_membership; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_group_membership (
    group_id character varying(36) NOT NULL,
    user_id character varying(36) NOT NULL,
    membership_type character varying(255) NOT NULL
);


ALTER TABLE public.user_group_membership OWNER TO admin;

--
-- Name: user_required_action; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_required_action (
    user_id character varying(36) NOT NULL,
    required_action character varying(255) DEFAULT ' '::character varying NOT NULL
);


ALTER TABLE public.user_required_action OWNER TO admin;

--
-- Name: user_role_mapping; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.user_role_mapping (
    role_id character varying(255) NOT NULL,
    user_id character varying(36) NOT NULL
);


ALTER TABLE public.user_role_mapping OWNER TO admin;

--
-- Name: web_origins; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.web_origins (
    client_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.web_origins OWNER TO admin;

--
-- Name: webhook; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.webhook (
    id character varying(36) NOT NULL,
    enabled boolean DEFAULT true NOT NULL,
    url character varying(2048) NOT NULL,
    secret character varying(100),
    created_at timestamp without time zone,
    created_by_user_id character varying(36),
    realm_id character varying(36),
    algorithm character varying(255) DEFAULT 'HmacSHA256'::character varying
);


ALTER TABLE public.webhook OWNER TO admin;

--
-- Name: webhook_event; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.webhook_event (
    id character varying(36) NOT NULL,
    realm_id character varying(36) NOT NULL,
    event_type character varying(36) NOT NULL,
    event_id character varying(36),
    admin_event_id character varying(36),
    event_object jsonb
);


ALTER TABLE public.webhook_event OWNER TO admin;

--
-- Name: webhook_event_types; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.webhook_event_types (
    webhook_id character varying(36) NOT NULL,
    value character varying(255) NOT NULL
);


ALTER TABLE public.webhook_event_types OWNER TO admin;

--
-- Name: webhook_send; Type: TABLE; Schema: public; Owner: admin
--

CREATE TABLE public.webhook_send (
    id character varying(36) NOT NULL,
    event_type character varying(255) NOT NULL,
    webhook_id character varying(36) NOT NULL,
    webhook_event_id character varying(36) NOT NULL,
    sent_at timestamp without time zone,
    retries integer,
    status integer
);


ALTER TABLE public.webhook_send OWNER TO admin;

--
-- Data for Name: admin_event_entity; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.admin_event_entity (id, admin_event_time, realm_id, operation_type, auth_realm_id, auth_client_id, auth_user_id, ip_address, resource_path, representation, error, resource_type, details_json) FROM stdin;
\.


--
-- Data for Name: associated_policy; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.associated_policy (policy_id, associated_policy_id) FROM stdin;
3064dc90-e62f-4046-b113-e974414ae787	c4f8dde2-c2ad-4809-b5a2-d0516c18ad41
\.


--
-- Data for Name: authentication_execution; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.authentication_execution (id, alias, authenticator, realm_id, flow_id, requirement, priority, authenticator_flow, auth_flow_id, auth_config) FROM stdin;
00f495c3-49b5-4f7f-9908-0a96c5a2e250	\N	auth-cookie	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0f2d5899-3103-436c-a5bb-2a8ab084c3ef	2	10	f	\N	\N
86d06d8d-09b7-4f6f-9507-3dcce3b7c878	\N	auth-spnego	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0f2d5899-3103-436c-a5bb-2a8ab084c3ef	3	20	f	\N	\N
fdc58be1-d206-4bbc-bcd4-18b213b336fb	\N	identity-provider-redirector	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0f2d5899-3103-436c-a5bb-2a8ab084c3ef	2	25	f	\N	\N
a0216282-e57a-48ef-98ff-b645206eb134	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0f2d5899-3103-436c-a5bb-2a8ab084c3ef	2	30	t	3e23af10-8f7c-49c1-8e9f-3024aa8d9aec	\N
9e80f2d3-5cc4-445c-aa5b-57c9ef2bb75d	\N	auth-username-password-form	eacf1fae-7916-43d5-b7e0-7abf35df7d49	3e23af10-8f7c-49c1-8e9f-3024aa8d9aec	0	10	f	\N	\N
8b8eefc0-de40-49fa-804f-98bd00b4af0d	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	3e23af10-8f7c-49c1-8e9f-3024aa8d9aec	1	20	t	59cf5f49-82af-4e72-ba6c-63bf2b4331a8	\N
dc157784-10d9-4bf0-a72c-58d5f5ae9f71	\N	conditional-user-configured	eacf1fae-7916-43d5-b7e0-7abf35df7d49	59cf5f49-82af-4e72-ba6c-63bf2b4331a8	0	10	f	\N	\N
a7ede6e9-afb2-4594-9179-85121f6bae3f	\N	auth-otp-form	eacf1fae-7916-43d5-b7e0-7abf35df7d49	59cf5f49-82af-4e72-ba6c-63bf2b4331a8	0	20	f	\N	\N
2475b65b-1d6b-4ea6-9c09-c4d842588a9b	\N	direct-grant-validate-username	eacf1fae-7916-43d5-b7e0-7abf35df7d49	9d8b54ea-18d0-43f6-861d-49dde066e744	0	10	f	\N	\N
c523011f-0dda-4be8-b2f1-2805dd63f227	\N	direct-grant-validate-password	eacf1fae-7916-43d5-b7e0-7abf35df7d49	9d8b54ea-18d0-43f6-861d-49dde066e744	0	20	f	\N	\N
acd2dac1-ff81-4392-8846-b95801487045	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	9d8b54ea-18d0-43f6-861d-49dde066e744	1	30	t	5d295af3-d981-45d1-82d0-235e46eccfd5	\N
2c2eae18-08de-46d8-a27d-fa54960c8de7	\N	conditional-user-configured	eacf1fae-7916-43d5-b7e0-7abf35df7d49	5d295af3-d981-45d1-82d0-235e46eccfd5	0	10	f	\N	\N
eb7c758b-2d47-4acc-8665-de940d3e7d54	\N	direct-grant-validate-otp	eacf1fae-7916-43d5-b7e0-7abf35df7d49	5d295af3-d981-45d1-82d0-235e46eccfd5	0	20	f	\N	\N
ae808a08-5d15-4230-a02f-df779e1cd76c	\N	registration-page-form	eacf1fae-7916-43d5-b7e0-7abf35df7d49	8403259f-d43a-4f64-be20-385b6b23c6ab	0	10	t	62fbe709-6987-44c1-b195-dd1064ffc2f8	\N
f3682319-6620-4a21-8eb5-52c7f0d278f0	\N	registration-user-creation	eacf1fae-7916-43d5-b7e0-7abf35df7d49	62fbe709-6987-44c1-b195-dd1064ffc2f8	0	20	f	\N	\N
959e2cbf-2519-47ec-b69c-734982bee970	\N	registration-password-action	eacf1fae-7916-43d5-b7e0-7abf35df7d49	62fbe709-6987-44c1-b195-dd1064ffc2f8	0	50	f	\N	\N
7bfa2ff5-605c-4a3a-8f4e-cf29c5c2d192	\N	registration-recaptcha-action	eacf1fae-7916-43d5-b7e0-7abf35df7d49	62fbe709-6987-44c1-b195-dd1064ffc2f8	3	60	f	\N	\N
27336631-617c-457e-9641-756e568dac89	\N	registration-terms-and-conditions	eacf1fae-7916-43d5-b7e0-7abf35df7d49	62fbe709-6987-44c1-b195-dd1064ffc2f8	3	70	f	\N	\N
e11774ba-00d0-436a-ad96-fab8bdf39ab7	\N	reset-credentials-choose-user	eacf1fae-7916-43d5-b7e0-7abf35df7d49	eab126c3-628a-42d3-850e-e685b877712e	0	10	f	\N	\N
fd8a2c81-4c2f-471c-8668-0bdfeb54d911	\N	reset-credential-email	eacf1fae-7916-43d5-b7e0-7abf35df7d49	eab126c3-628a-42d3-850e-e685b877712e	0	20	f	\N	\N
76dc0c0c-468d-4cbd-9809-c4a1ef5a151c	\N	reset-password	eacf1fae-7916-43d5-b7e0-7abf35df7d49	eab126c3-628a-42d3-850e-e685b877712e	0	30	f	\N	\N
aee9d7ce-c1fe-41ca-bcbf-809bf39fe939	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	eab126c3-628a-42d3-850e-e685b877712e	1	40	t	a274fdb0-fd55-4e03-97cd-b7a7a0fcfe82	\N
76076ce8-9715-4f09-bd75-27e39e6b61b8	\N	conditional-user-configured	eacf1fae-7916-43d5-b7e0-7abf35df7d49	a274fdb0-fd55-4e03-97cd-b7a7a0fcfe82	0	10	f	\N	\N
adce3c79-d601-438c-b222-c1383059bcd4	\N	reset-otp	eacf1fae-7916-43d5-b7e0-7abf35df7d49	a274fdb0-fd55-4e03-97cd-b7a7a0fcfe82	0	20	f	\N	\N
fa6a7b07-e477-41bc-873c-bac16b8bdee9	\N	client-secret	eacf1fae-7916-43d5-b7e0-7abf35df7d49	718bda0f-7a85-4b50-a55d-12b6ac640a44	2	10	f	\N	\N
16fe76f5-8d67-4b13-92c1-58d32a7ca673	\N	client-jwt	eacf1fae-7916-43d5-b7e0-7abf35df7d49	718bda0f-7a85-4b50-a55d-12b6ac640a44	2	20	f	\N	\N
10bfa304-cff1-46d3-80ea-32b047274675	\N	client-secret-jwt	eacf1fae-7916-43d5-b7e0-7abf35df7d49	718bda0f-7a85-4b50-a55d-12b6ac640a44	2	30	f	\N	\N
2c4560a5-4eef-418a-8a33-f212e181b8f8	\N	client-x509	eacf1fae-7916-43d5-b7e0-7abf35df7d49	718bda0f-7a85-4b50-a55d-12b6ac640a44	2	40	f	\N	\N
4d4b8ff5-3a18-4287-9752-b403f6134df3	\N	idp-review-profile	eacf1fae-7916-43d5-b7e0-7abf35df7d49	b982b519-a444-4d10-b939-5ccb89cc296b	0	10	f	\N	b1f2c658-63ee-4c7a-8d84-6ddf386178d3
e9fcc7f2-b1c7-471d-a1b1-29131899fd3a	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	b982b519-a444-4d10-b939-5ccb89cc296b	0	20	t	53971528-aabe-4272-80c9-344d9bf6f59f	\N
6c5d0d60-50c4-4e48-90b6-b11ca9736900	\N	idp-create-user-if-unique	eacf1fae-7916-43d5-b7e0-7abf35df7d49	53971528-aabe-4272-80c9-344d9bf6f59f	2	10	f	\N	aeac8419-f83d-4e7d-a3d9-7c5c70311463
d587bdda-f52f-48fd-95a2-80f6419600d1	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	53971528-aabe-4272-80c9-344d9bf6f59f	2	20	t	631f5a5c-9149-449d-a24e-7bac8aea3514	\N
e65bc7e8-ac6e-4a10-9671-75762390ab94	\N	idp-confirm-link	eacf1fae-7916-43d5-b7e0-7abf35df7d49	631f5a5c-9149-449d-a24e-7bac8aea3514	0	10	f	\N	\N
017b3ef3-7b82-4b63-b66e-f253459e7941	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	631f5a5c-9149-449d-a24e-7bac8aea3514	0	20	t	ac092736-5ba9-4a47-9e8f-8c98fb8cd1d5	\N
0bae284d-689b-40b8-a21d-f7eb5886fa71	\N	idp-email-verification	eacf1fae-7916-43d5-b7e0-7abf35df7d49	ac092736-5ba9-4a47-9e8f-8c98fb8cd1d5	2	10	f	\N	\N
6b871079-f775-48d5-b5d2-30f1e680b986	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	ac092736-5ba9-4a47-9e8f-8c98fb8cd1d5	2	20	t	7f1fda17-d8e9-4bee-a22d-46dba30fd941	\N
fc68177e-a934-43a1-8f3a-275a73bc6988	\N	idp-username-password-form	eacf1fae-7916-43d5-b7e0-7abf35df7d49	7f1fda17-d8e9-4bee-a22d-46dba30fd941	0	10	f	\N	\N
ff199b5b-f4ef-43e1-92f4-4676bbf6170d	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	7f1fda17-d8e9-4bee-a22d-46dba30fd941	1	20	t	efc3269d-69fc-4362-85f0-21451cc19c44	\N
f1265f4d-bc4a-4d95-9e66-bebd83d55f35	\N	conditional-user-configured	eacf1fae-7916-43d5-b7e0-7abf35df7d49	efc3269d-69fc-4362-85f0-21451cc19c44	0	10	f	\N	\N
7b087a72-159b-4c18-9b15-0edc52162118	\N	auth-otp-form	eacf1fae-7916-43d5-b7e0-7abf35df7d49	efc3269d-69fc-4362-85f0-21451cc19c44	0	20	f	\N	\N
ea1bd9f4-5e93-4fa8-ac05-127e2db4f4d3	\N	http-basic-authenticator	eacf1fae-7916-43d5-b7e0-7abf35df7d49	b12cb10d-a24b-4164-90e5-c86b3648e9bf	0	10	f	\N	\N
55ac4a55-4d89-445c-9d66-bc0a484411d0	\N	docker-http-basic-authenticator	eacf1fae-7916-43d5-b7e0-7abf35df7d49	90e3ef83-27cb-4aa7-9013-7ef775291230	0	10	f	\N	\N
a8a84663-ce45-4dda-a2ab-8eba1e794007	\N	auth-cookie	2c411af7-e0b7-4547-b08a-27c7c8c1722c	212cfa8d-af30-400e-b7b3-419fb7619a0b	2	10	f	\N	\N
3588adf3-112d-4f58-969c-77024c4d1ae7	\N	auth-spnego	2c411af7-e0b7-4547-b08a-27c7c8c1722c	212cfa8d-af30-400e-b7b3-419fb7619a0b	3	20	f	\N	\N
8adef41a-05a6-4186-b623-8333920dcfe3	\N	identity-provider-redirector	2c411af7-e0b7-4547-b08a-27c7c8c1722c	212cfa8d-af30-400e-b7b3-419fb7619a0b	2	25	f	\N	\N
c1b6fd37-9cda-421b-9e06-fe831c7d44ec	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	212cfa8d-af30-400e-b7b3-419fb7619a0b	2	30	t	aaefff14-35bc-49d7-a0d7-033f5161b9ad	\N
579672ce-2364-48dc-a6e1-c961e39ca7ba	\N	auth-username-password-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	aaefff14-35bc-49d7-a0d7-033f5161b9ad	0	10	f	\N	\N
8e6d06c6-7b5d-4c31-b64e-ff659e45c40b	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	aaefff14-35bc-49d7-a0d7-033f5161b9ad	1	20	t	18bf93fa-915d-4adb-86b2-2319e431d08d	\N
f33981b8-c869-4d66-bc24-dc3e062c5a80	\N	conditional-user-configured	2c411af7-e0b7-4547-b08a-27c7c8c1722c	18bf93fa-915d-4adb-86b2-2319e431d08d	0	10	f	\N	\N
01ba1493-d5f8-461a-9c9a-278e53107c00	\N	auth-otp-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	18bf93fa-915d-4adb-86b2-2319e431d08d	0	20	f	\N	\N
879819f5-0d16-465c-b6d8-84fcad0214dd	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	212cfa8d-af30-400e-b7b3-419fb7619a0b	2	26	t	ee94d00b-4374-4588-a3c3-98fd69a6285e	\N
e723cb3b-364b-4ef5-adeb-bd35b61e3049	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ee94d00b-4374-4588-a3c3-98fd69a6285e	1	10	t	80dae790-9631-4260-8b4b-bdbee2f9b9eb	\N
e14b5687-4e2b-432f-ad05-bb42cd9add5d	\N	conditional-user-configured	2c411af7-e0b7-4547-b08a-27c7c8c1722c	80dae790-9631-4260-8b4b-bdbee2f9b9eb	0	10	f	\N	\N
6c154721-2274-4767-9fc4-0e37ec3a9f04	\N	organization	2c411af7-e0b7-4547-b08a-27c7c8c1722c	80dae790-9631-4260-8b4b-bdbee2f9b9eb	2	20	f	\N	\N
728c1bab-e40e-41f5-9120-38348f9395d4	\N	direct-grant-validate-username	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ffd184f2-d0b3-4c23-a802-0c62fb3dc76b	0	10	f	\N	\N
5e19d0da-2f2d-4aad-ba00-9fcfc51a62ff	\N	direct-grant-validate-password	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ffd184f2-d0b3-4c23-a802-0c62fb3dc76b	0	20	f	\N	\N
85c60c97-e3ce-417f-965d-609b08606a83	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ffd184f2-d0b3-4c23-a802-0c62fb3dc76b	1	30	t	d1f951bc-ef44-49a5-b4d4-52d66933067b	\N
a83a8d3a-4b2d-48ca-9e6b-fe23cb03cdd1	\N	conditional-user-configured	2c411af7-e0b7-4547-b08a-27c7c8c1722c	d1f951bc-ef44-49a5-b4d4-52d66933067b	0	10	f	\N	\N
58e71268-c069-499f-b423-da850dc53403	\N	direct-grant-validate-otp	2c411af7-e0b7-4547-b08a-27c7c8c1722c	d1f951bc-ef44-49a5-b4d4-52d66933067b	0	20	f	\N	\N
01bdedbe-83a7-4f20-8d19-1bb2a086af19	\N	registration-page-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	b67f4795-bf0b-46e8-9d26-9bf816f0c59c	0	10	t	c50355c7-fc6b-4fd7-900b-d444674e93de	\N
4746d2e0-3624-4135-b534-0c0a0d382f09	\N	registration-user-creation	2c411af7-e0b7-4547-b08a-27c7c8c1722c	c50355c7-fc6b-4fd7-900b-d444674e93de	0	20	f	\N	\N
98f0d707-5b8e-43d8-b759-5a39cf7b179e	\N	registration-password-action	2c411af7-e0b7-4547-b08a-27c7c8c1722c	c50355c7-fc6b-4fd7-900b-d444674e93de	0	50	f	\N	\N
e60da4aa-c0ce-4359-b382-e6e66325f4b3	\N	registration-recaptcha-action	2c411af7-e0b7-4547-b08a-27c7c8c1722c	c50355c7-fc6b-4fd7-900b-d444674e93de	3	60	f	\N	\N
150c2fe9-d295-4cdf-847e-eaae6ab80e6f	\N	registration-terms-and-conditions	2c411af7-e0b7-4547-b08a-27c7c8c1722c	c50355c7-fc6b-4fd7-900b-d444674e93de	3	70	f	\N	\N
43951bb6-4dfe-40b9-a993-8cee5b913f41	\N	reset-credentials-choose-user	2c411af7-e0b7-4547-b08a-27c7c8c1722c	a11ceaf5-2b00-4283-aab9-3599df08b5a3	0	10	f	\N	\N
6736eb2e-1d98-4365-ba27-e17bf02fc6c3	\N	reset-credential-email	2c411af7-e0b7-4547-b08a-27c7c8c1722c	a11ceaf5-2b00-4283-aab9-3599df08b5a3	0	20	f	\N	\N
134e66fc-ed74-40a8-a35f-75f86a72f978	\N	reset-password	2c411af7-e0b7-4547-b08a-27c7c8c1722c	a11ceaf5-2b00-4283-aab9-3599df08b5a3	0	30	f	\N	\N
bc7fd5fe-211d-454e-ab21-f46eb2792f49	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	a11ceaf5-2b00-4283-aab9-3599df08b5a3	1	40	t	34c4053d-3c3a-485a-be2d-9dd49b34e6e7	\N
84f6b830-0973-41f9-af34-22fc254f5172	\N	conditional-user-configured	2c411af7-e0b7-4547-b08a-27c7c8c1722c	34c4053d-3c3a-485a-be2d-9dd49b34e6e7	0	10	f	\N	\N
858e471f-a479-41e2-a781-3cfecbbfb171	\N	reset-otp	2c411af7-e0b7-4547-b08a-27c7c8c1722c	34c4053d-3c3a-485a-be2d-9dd49b34e6e7	0	20	f	\N	\N
72c8b20c-a09c-48de-9b4c-e9c619ece416	\N	client-secret	2c411af7-e0b7-4547-b08a-27c7c8c1722c	96f9c24b-2903-4ee1-a32f-a0a1400d56b4	2	10	f	\N	\N
c0dba82b-53f0-4bcd-8117-90fdf52377d3	\N	client-jwt	2c411af7-e0b7-4547-b08a-27c7c8c1722c	96f9c24b-2903-4ee1-a32f-a0a1400d56b4	2	20	f	\N	\N
fc8aed6a-b846-472e-bc62-04a1c6a05f02	\N	client-secret-jwt	2c411af7-e0b7-4547-b08a-27c7c8c1722c	96f9c24b-2903-4ee1-a32f-a0a1400d56b4	2	30	f	\N	\N
f5dfb0cb-422b-44a0-9034-0e1fac90e5c6	\N	client-x509	2c411af7-e0b7-4547-b08a-27c7c8c1722c	96f9c24b-2903-4ee1-a32f-a0a1400d56b4	2	40	f	\N	\N
e12fabea-736e-42d4-a3cb-8d5bde6d7183	\N	idp-review-profile	2c411af7-e0b7-4547-b08a-27c7c8c1722c	83f93401-8fc1-484f-b7f0-8c55381a1943	0	10	f	\N	39c2b203-1d1d-447c-b782-40bff3d56c18
4156a9a7-44ba-4ff3-b3fb-932cf5c0b388	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	83f93401-8fc1-484f-b7f0-8c55381a1943	0	20	t	2e101820-3853-4c50-af18-713590ddb9ed	\N
792170fa-31ae-4326-b704-81217c7647d8	\N	idp-create-user-if-unique	2c411af7-e0b7-4547-b08a-27c7c8c1722c	2e101820-3853-4c50-af18-713590ddb9ed	2	10	f	\N	e05b6714-9747-480f-9c86-4baaf9a00c27
7fb0a044-64ab-4b67-bbd5-aae05f2b4e62	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	2e101820-3853-4c50-af18-713590ddb9ed	2	20	t	c77afc7f-5565-4d12-a86c-cd81d48b7b08	\N
2fb13692-620c-4cce-b22b-8e653927be60	\N	idp-confirm-link	2c411af7-e0b7-4547-b08a-27c7c8c1722c	c77afc7f-5565-4d12-a86c-cd81d48b7b08	0	10	f	\N	\N
9e993641-7c8d-4e2e-affb-b81ff6f0473e	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	c77afc7f-5565-4d12-a86c-cd81d48b7b08	0	20	t	3e41355a-2a71-4e0a-a00b-9ba0d7391f80	\N
66b76945-9061-46d1-a09a-ede1e1b64e5c	\N	idp-email-verification	2c411af7-e0b7-4547-b08a-27c7c8c1722c	3e41355a-2a71-4e0a-a00b-9ba0d7391f80	2	10	f	\N	\N
4f586497-9a43-4f7c-8b2e-9cc9ffc9dbc9	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	3e41355a-2a71-4e0a-a00b-9ba0d7391f80	2	20	t	b5c24054-5b54-447a-a244-86d6230af41c	\N
76fe7079-75ad-480a-bb02-0d56e836dbe6	\N	idp-username-password-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	b5c24054-5b54-447a-a244-86d6230af41c	0	10	f	\N	\N
9f92c475-899b-4488-82b0-8bcad6700245	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	b5c24054-5b54-447a-a244-86d6230af41c	1	20	t	bd986a1c-e639-426b-b69d-8e7e2ae55b58	\N
1d6449b8-d282-47a9-9a7b-f28277216508	\N	conditional-user-configured	2c411af7-e0b7-4547-b08a-27c7c8c1722c	bd986a1c-e639-426b-b69d-8e7e2ae55b58	0	10	f	\N	\N
3440ba05-82d5-4d79-a529-60fe15f57fbc	\N	auth-otp-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	bd986a1c-e639-426b-b69d-8e7e2ae55b58	0	20	f	\N	\N
4b04216f-ad7e-4348-b283-f2e1d83ed2ff	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	83f93401-8fc1-484f-b7f0-8c55381a1943	1	50	t	b44fe27b-9dff-48f0-86c7-a732e6c6b915	\N
8161e834-e4ea-45c1-8a07-8cfe1ad8227f	\N	conditional-user-configured	2c411af7-e0b7-4547-b08a-27c7c8c1722c	b44fe27b-9dff-48f0-86c7-a732e6c6b915	0	10	f	\N	\N
14f21f59-f94d-4788-86fd-d9e63dc72f75	\N	idp-add-organization-member	2c411af7-e0b7-4547-b08a-27c7c8c1722c	b44fe27b-9dff-48f0-86c7-a732e6c6b915	0	20	f	\N	\N
ddd4531c-6d48-404f-a985-a08f05eb44e9	\N	http-basic-authenticator	2c411af7-e0b7-4547-b08a-27c7c8c1722c	cb512f6b-9bac-4efe-b0b6-3fe82404f2f1	0	10	f	\N	\N
c9db8835-f79e-4fe7-a89c-f256b10154d8	\N	docker-http-basic-authenticator	2c411af7-e0b7-4547-b08a-27c7c8c1722c	22aca36c-7be2-4cc1-bf2c-2657d297df1b	0	10	f	\N	\N
4a5cf859-89dd-424a-bb4b-8d93d0a99398	\N	auth-username-password-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	bd37fa0f-ccc6-4ef9-973e-a78f9a96ab73	0	10	f	\N	\N
5776c301-b793-4930-8d89-fbfd19cffee7	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f03cef74-4a64-4777-a27e-70f20d2c2860	2	30	t	bd37fa0f-ccc6-4ef9-973e-a78f9a96ab73	\N
8ff4e83b-d4cb-492f-8aa3-81e7f72da6f7	\N	auth-conditional-otp-form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	bd37fa0f-ccc6-4ef9-973e-a78f9a96ab73	0	11	f	\N	\N
\.


--
-- Data for Name: authentication_flow; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.authentication_flow (id, alias, description, realm_id, provider_id, top_level, built_in) FROM stdin;
0f2d5899-3103-436c-a5bb-2a8ab084c3ef	browser	Browser based authentication	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
3e23af10-8f7c-49c1-8e9f-3024aa8d9aec	forms	Username, password, otp and other auth forms.	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
59cf5f49-82af-4e72-ba6c-63bf2b4331a8	Browser - Conditional OTP	Flow to determine if the OTP is required for the authentication	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
9d8b54ea-18d0-43f6-861d-49dde066e744	direct grant	OpenID Connect Resource Owner Grant	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
5d295af3-d981-45d1-82d0-235e46eccfd5	Direct Grant - Conditional OTP	Flow to determine if the OTP is required for the authentication	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
8403259f-d43a-4f64-be20-385b6b23c6ab	registration	Registration flow	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
62fbe709-6987-44c1-b195-dd1064ffc2f8	registration form	Registration form	eacf1fae-7916-43d5-b7e0-7abf35df7d49	form-flow	f	t
eab126c3-628a-42d3-850e-e685b877712e	reset credentials	Reset credentials for a user if they forgot their password or something	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
a274fdb0-fd55-4e03-97cd-b7a7a0fcfe82	Reset - Conditional OTP	Flow to determine if the OTP should be reset or not. Set to REQUIRED to force.	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
718bda0f-7a85-4b50-a55d-12b6ac640a44	clients	Base authentication for clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	client-flow	t	t
b982b519-a444-4d10-b939-5ccb89cc296b	first broker login	Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
53971528-aabe-4272-80c9-344d9bf6f59f	User creation or linking	Flow for the existing/non-existing user alternatives	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
631f5a5c-9149-449d-a24e-7bac8aea3514	Handle Existing Account	Handle what to do if there is existing account with same email/username like authenticated identity provider	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
ac092736-5ba9-4a47-9e8f-8c98fb8cd1d5	Account verification options	Method with which to verity the existing account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
7f1fda17-d8e9-4bee-a22d-46dba30fd941	Verify Existing Account by Re-authentication	Reauthentication of existing account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
efc3269d-69fc-4362-85f0-21451cc19c44	First broker login - Conditional OTP	Flow to determine if the OTP is required for the authentication	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	f	t
b12cb10d-a24b-4164-90e5-c86b3648e9bf	saml ecp	SAML ECP Profile Authentication Flow	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
90e3ef83-27cb-4aa7-9013-7ef775291230	docker auth	Used by Docker clients to authenticate against the IDP	eacf1fae-7916-43d5-b7e0-7abf35df7d49	basic-flow	t	t
212cfa8d-af30-400e-b7b3-419fb7619a0b	browser	Browser based authentication	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
aaefff14-35bc-49d7-a0d7-033f5161b9ad	forms	Username, password, otp and other auth forms.	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
18bf93fa-915d-4adb-86b2-2319e431d08d	Browser - Conditional OTP	Flow to determine if the OTP is required for the authentication	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
ee94d00b-4374-4588-a3c3-98fd69a6285e	Organization	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
80dae790-9631-4260-8b4b-bdbee2f9b9eb	Browser - Conditional Organization	Flow to determine if the organization identity-first login is to be used	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
ffd184f2-d0b3-4c23-a802-0c62fb3dc76b	direct grant	OpenID Connect Resource Owner Grant	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
d1f951bc-ef44-49a5-b4d4-52d66933067b	Direct Grant - Conditional OTP	Flow to determine if the OTP is required for the authentication	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
b67f4795-bf0b-46e8-9d26-9bf816f0c59c	registration	Registration flow	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
c50355c7-fc6b-4fd7-900b-d444674e93de	registration form	Registration form	2c411af7-e0b7-4547-b08a-27c7c8c1722c	form-flow	f	t
a11ceaf5-2b00-4283-aab9-3599df08b5a3	reset credentials	Reset credentials for a user if they forgot their password or something	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
34c4053d-3c3a-485a-be2d-9dd49b34e6e7	Reset - Conditional OTP	Flow to determine if the OTP should be reset or not. Set to REQUIRED to force.	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
96f9c24b-2903-4ee1-a32f-a0a1400d56b4	clients	Base authentication for clients	2c411af7-e0b7-4547-b08a-27c7c8c1722c	client-flow	t	t
83f93401-8fc1-484f-b7f0-8c55381a1943	first broker login	Actions taken after first broker login with identity provider account, which is not yet linked to any Keycloak account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
2e101820-3853-4c50-af18-713590ddb9ed	User creation or linking	Flow for the existing/non-existing user alternatives	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
c77afc7f-5565-4d12-a86c-cd81d48b7b08	Handle Existing Account	Handle what to do if there is existing account with same email/username like authenticated identity provider	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
3e41355a-2a71-4e0a-a00b-9ba0d7391f80	Account verification options	Method with which to verity the existing account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
b5c24054-5b54-447a-a244-86d6230af41c	Verify Existing Account by Re-authentication	Reauthentication of existing account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
bd986a1c-e639-426b-b69d-8e7e2ae55b58	First broker login - Conditional OTP	Flow to determine if the OTP is required for the authentication	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
b44fe27b-9dff-48f0-86c7-a732e6c6b915	First Broker Login - Conditional Organization	Flow to determine if the authenticator that adds organization members is to be used	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	t
cb512f6b-9bac-4efe-b0b6-3fe82404f2f1	saml ecp	SAML ECP Profile Authentication Flow	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
22aca36c-7be2-4cc1-bf2c-2657d297df1b	docker auth	Used by Docker clients to authenticate against the IDP	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	t
f03cef74-4a64-4777-a27e-70f20d2c2860	testBrowser	Browser based authentication	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	t	f
bd37fa0f-ccc6-4ef9-973e-a78f9a96ab73	testBrowser forms	Username, password, otp and other auth forms.	2c411af7-e0b7-4547-b08a-27c7c8c1722c	basic-flow	f	f
\.


--
-- Data for Name: authenticator_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.authenticator_config (id, alias, realm_id) FROM stdin;
b1f2c658-63ee-4c7a-8d84-6ddf386178d3	review profile config	eacf1fae-7916-43d5-b7e0-7abf35df7d49
aeac8419-f83d-4e7d-a3d9-7c5c70311463	create unique user config	eacf1fae-7916-43d5-b7e0-7abf35df7d49
39c2b203-1d1d-447c-b782-40bff3d56c18	review profile config	2c411af7-e0b7-4547-b08a-27c7c8c1722c
e05b6714-9747-480f-9c86-4baaf9a00c27	create unique user config	2c411af7-e0b7-4547-b08a-27c7c8c1722c
\.


--
-- Data for Name: authenticator_config_entry; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.authenticator_config_entry (authenticator_id, value, name) FROM stdin;
aeac8419-f83d-4e7d-a3d9-7c5c70311463	false	require.password.update.after.registration
b1f2c658-63ee-4c7a-8d84-6ddf386178d3	missing	update.profile.on.first.login
39c2b203-1d1d-447c-b782-40bff3d56c18	missing	update.profile.on.first.login
e05b6714-9747-480f-9c86-4baaf9a00c27	false	require.password.update.after.registration
\.


--
-- Data for Name: broker_link; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.broker_link (identity_provider, storage_provider_id, realm_id, broker_user_id, broker_username, token, user_id) FROM stdin;
\.


--
-- Data for Name: client; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client (id, enabled, full_scope_allowed, client_id, not_before, public_client, secret, base_url, bearer_only, management_url, surrogate_auth_required, realm_id, protocol, node_rereg_timeout, frontchannel_logout, consent_required, name, service_accounts_enabled, client_authenticator_type, root_url, description, registration_token, standard_flow_enabled, implicit_flow_enabled, direct_access_grants_enabled, always_display_in_console) FROM stdin;
44f1605b-be38-4157-ab34-194b13dc41c6	t	f	master-realm	0	f	\N	\N	t	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	0	f	f	master Realm	f	client-secret	\N	\N	\N	t	f	f	f
d7e66ce3-0769-4b3d-9636-4893459eaf54	t	f	account	0	t	\N	/realms/master/account/	f	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	openid-connect	0	f	f	${client_account}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	t	f	account-console	0	t	\N	/realms/master/account/	f	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	openid-connect	0	f	f	${client_account-console}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
cb742081-b162-4207-9130-f1b5f073fd9c	t	f	broker	0	f	\N	\N	t	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	openid-connect	0	f	f	${client_broker}	f	client-secret	\N	\N	\N	t	f	f	f
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	t	t	security-admin-console	0	t	\N	/admin/master/console/	f	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	openid-connect	0	f	f	${client_security-admin-console}	f	client-secret	${authAdminUrl}	\N	\N	t	f	f	f
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	t	t	admin-cli	0	t	\N	\N	f	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	openid-connect	0	f	f	${client_admin-cli}	f	client-secret	\N	\N	\N	f	f	t	f
2970b512-2182-4062-9dfe-7299580cf689	t	f	tskhra-realm	0	f	\N	\N	t	\N	f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	0	f	f	tskhra Realm	f	client-secret	\N	\N	\N	t	f	f	f
de442f71-6200-4f81-918d-da9fdeea6e9b	t	f	realm-management	0	f	\N	\N	t	\N	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	0	f	f	${client_realm-management}	f	client-secret	\N	\N	\N	t	f	f	f
500b5c86-ba2e-4345-8602-4e8576a82347	t	f	account	0	t	\N	/realms/tskhra/account/	f	\N	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	0	f	f	${client_account}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	t	f	account-console	0	t	\N	/realms/tskhra/account/	f	\N	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	0	f	f	${client_account-console}	f	client-secret	${authBaseUrl}	\N	\N	t	f	f	f
3fc86730-d04c-4cc7-af16-13a708999082	t	f	broker	0	f	\N	\N	t	\N	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	0	f	f	${client_broker}	f	client-secret	\N	\N	\N	t	f	f	f
7f207e63-5406-447c-9a3b-97cdddc5e07a	t	t	security-admin-console	0	t	\N	/admin/tskhra/console/	f	\N	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	0	f	f	${client_security-admin-console}	f	client-secret	${authAdminUrl}	\N	\N	t	f	f	f
06f667d2-3e90-4e6f-af50-8e8a833198b4	t	t	admin-cli	0	t	\N	\N	f	\N	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	0	f	f	${client_admin-cli}	f	client-secret	\N	\N	\N	f	f	t	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	t	t	user-service	0	f	hiDfHEHBRbi6VuEPvBDirMecSqINIXit		f		f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	-1	t	f	User Service	t	client-secret			\N	t	f	t	f
b4b39689-8818-4208-b102-ee758dad2268	t	t	react-client	0	t	\N		f		f	eacf1fae-7916-43d5-b7e0-7abf35df7d49	openid-connect	-1	t	f		f	client-secret			\N	t	f	t	f
15735a86-4946-440b-9251-0e8487f6eb01	t	t	react-client	0	t	\N		f		f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	openid-connect	-1	t	f		f	client-secret			\N	t	f	t	f
\.


--
-- Data for Name: client_attributes; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_attributes (client_id, name, value) FROM stdin;
d7e66ce3-0769-4b3d-9636-4893459eaf54	post.logout.redirect.uris	+
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	post.logout.redirect.uris	+
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	pkce.code.challenge.method	S256
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	post.logout.redirect.uris	+
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	pkce.code.challenge.method	S256
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	client.use.lightweight.access.token.enabled	true
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	client.use.lightweight.access.token.enabled	true
500b5c86-ba2e-4345-8602-4e8576a82347	post.logout.redirect.uris	+
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	post.logout.redirect.uris	+
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	pkce.code.challenge.method	S256
7f207e63-5406-447c-9a3b-97cdddc5e07a	post.logout.redirect.uris	+
7f207e63-5406-447c-9a3b-97cdddc5e07a	pkce.code.challenge.method	S256
7f207e63-5406-447c-9a3b-97cdddc5e07a	client.use.lightweight.access.token.enabled	true
06f667d2-3e90-4e6f-af50-8e8a833198b4	client.use.lightweight.access.token.enabled	true
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	client.secret.creation.time	1770585862
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	oauth2.device.authorization.grant.enabled	false
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	oidc.ciba.grant.enabled	false
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	backchannel.logout.session.required	true
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	backchannel.logout.revoke.offline.tokens	false
b4b39689-8818-4208-b102-ee758dad2268	oauth2.device.authorization.grant.enabled	false
b4b39689-8818-4208-b102-ee758dad2268	oidc.ciba.grant.enabled	false
b4b39689-8818-4208-b102-ee758dad2268	backchannel.logout.session.required	true
b4b39689-8818-4208-b102-ee758dad2268	backchannel.logout.revoke.offline.tokens	false
b4b39689-8818-4208-b102-ee758dad2268	realm_client	false
b4b39689-8818-4208-b102-ee758dad2268	display.on.consent.screen	false
b4b39689-8818-4208-b102-ee758dad2268	frontchannel.logout.session.required	true
15735a86-4946-440b-9251-0e8487f6eb01	oauth2.device.authorization.grant.enabled	false
15735a86-4946-440b-9251-0e8487f6eb01	oidc.ciba.grant.enabled	false
15735a86-4946-440b-9251-0e8487f6eb01	backchannel.logout.session.required	true
15735a86-4946-440b-9251-0e8487f6eb01	backchannel.logout.revoke.offline.tokens	false
15735a86-4946-440b-9251-0e8487f6eb01	realm_client	false
15735a86-4946-440b-9251-0e8487f6eb01	display.on.consent.screen	false
15735a86-4946-440b-9251-0e8487f6eb01	frontchannel.logout.session.required	true
\.


--
-- Data for Name: client_auth_flow_bindings; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_auth_flow_bindings (client_id, flow_id, binding_name) FROM stdin;
\.


--
-- Data for Name: client_initial_access; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_initial_access (id, realm_id, "timestamp", expiration, count, remaining_count) FROM stdin;
\.


--
-- Data for Name: client_node_registrations; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_node_registrations (client_id, value, name) FROM stdin;
\.


--
-- Data for Name: client_scope; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_scope (id, name, realm_id, description, protocol) FROM stdin;
9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	offline_access	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect built-in scope: offline_access	openid-connect
f992b9ed-1c4b-47fd-83e1-c26c3e795a4b	role_list	eacf1fae-7916-43d5-b7e0-7abf35df7d49	SAML role list	saml
d8720c55-a547-4bdc-9b07-06404c8c1a30	saml_organization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	Organization Membership	saml
eab4d0d4-3184-468f-bb10-5b82c5762e97	profile	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect built-in scope: profile	openid-connect
264770a9-8682-4235-83cf-2e12d59fd9ac	email	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect built-in scope: email	openid-connect
dc32533a-1e41-47f9-b737-3b644b5713fa	address	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect built-in scope: address	openid-connect
b0f472dd-8acb-45cc-9e6b-97efe9536cb0	phone	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect built-in scope: phone	openid-connect
5af152b0-b6d4-47eb-91d6-bd8589de25b8	roles	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect scope for add user roles to the access token	openid-connect
42cc9b6b-5715-4721-bd05-47c7507840f1	web-origins	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect scope for add allowed web origins to the access token	openid-connect
e3c878a1-9bec-4f37-a5e0-84f3561e9d65	microprofile-jwt	eacf1fae-7916-43d5-b7e0-7abf35df7d49	Microprofile - JWT built-in scope	openid-connect
e7f9379d-5bc0-481c-abc5-f1f8026fdd34	acr	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect scope for add acr (authentication context class reference) to the token	openid-connect
a3b9f256-1ff5-4108-be26-5da60bfc3877	basic	eacf1fae-7916-43d5-b7e0-7abf35df7d49	OpenID Connect scope for add all basic claims to the token	openid-connect
9f0556fd-b362-47de-a330-b4219cf3c2a3	service_account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	Specific scope for a client enabled for service accounts	openid-connect
75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	organization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	Additional claims about the organization a subject belongs to	openid-connect
cdcec106-3ff3-4861-b009-d792877b713c	offline_access	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect built-in scope: offline_access	openid-connect
617e9e7c-c22d-468e-a3ae-86385181237d	role_list	2c411af7-e0b7-4547-b08a-27c7c8c1722c	SAML role list	saml
e2261f11-2475-4538-bc0e-f663a4131459	saml_organization	2c411af7-e0b7-4547-b08a-27c7c8c1722c	Organization Membership	saml
a3d9b5bb-e717-4518-adbc-07bc0f692d64	profile	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect built-in scope: profile	openid-connect
cd5bc29d-1eae-4363-b403-3cd338a2653f	email	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect built-in scope: email	openid-connect
1aa1a3d0-d37d-4043-9c61-219994890dbe	address	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect built-in scope: address	openid-connect
3471014d-13bf-4c91-82fe-e145e45ce62c	phone	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect built-in scope: phone	openid-connect
0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	roles	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect scope for add user roles to the access token	openid-connect
44d90b70-00c8-485c-a91a-f77e616baf36	web-origins	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect scope for add allowed web origins to the access token	openid-connect
3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	microprofile-jwt	2c411af7-e0b7-4547-b08a-27c7c8c1722c	Microprofile - JWT built-in scope	openid-connect
74f581d3-8e6c-4ffc-aa96-5780938ff437	acr	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect scope for add acr (authentication context class reference) to the token	openid-connect
30a49f27-9f43-47ee-8a2a-91143cd0a6c4	basic	2c411af7-e0b7-4547-b08a-27c7c8c1722c	OpenID Connect scope for add all basic claims to the token	openid-connect
c46725a6-3bab-4231-afdb-b5d8ad4d9302	service_account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	Specific scope for a client enabled for service accounts	openid-connect
b8df8620-7249-4102-a288-c70ca38e4eac	organization	2c411af7-e0b7-4547-b08a-27c7c8c1722c	Additional claims about the organization a subject belongs to	openid-connect
\.


--
-- Data for Name: client_scope_attributes; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_scope_attributes (scope_id, value, name) FROM stdin;
9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	true	display.on.consent.screen
9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	${offlineAccessScopeConsentText}	consent.screen.text
f992b9ed-1c4b-47fd-83e1-c26c3e795a4b	true	display.on.consent.screen
f992b9ed-1c4b-47fd-83e1-c26c3e795a4b	${samlRoleListScopeConsentText}	consent.screen.text
d8720c55-a547-4bdc-9b07-06404c8c1a30	false	display.on.consent.screen
eab4d0d4-3184-468f-bb10-5b82c5762e97	true	display.on.consent.screen
eab4d0d4-3184-468f-bb10-5b82c5762e97	${profileScopeConsentText}	consent.screen.text
eab4d0d4-3184-468f-bb10-5b82c5762e97	true	include.in.token.scope
264770a9-8682-4235-83cf-2e12d59fd9ac	true	display.on.consent.screen
264770a9-8682-4235-83cf-2e12d59fd9ac	${emailScopeConsentText}	consent.screen.text
264770a9-8682-4235-83cf-2e12d59fd9ac	true	include.in.token.scope
dc32533a-1e41-47f9-b737-3b644b5713fa	true	display.on.consent.screen
dc32533a-1e41-47f9-b737-3b644b5713fa	${addressScopeConsentText}	consent.screen.text
dc32533a-1e41-47f9-b737-3b644b5713fa	true	include.in.token.scope
b0f472dd-8acb-45cc-9e6b-97efe9536cb0	true	display.on.consent.screen
b0f472dd-8acb-45cc-9e6b-97efe9536cb0	${phoneScopeConsentText}	consent.screen.text
b0f472dd-8acb-45cc-9e6b-97efe9536cb0	true	include.in.token.scope
5af152b0-b6d4-47eb-91d6-bd8589de25b8	true	display.on.consent.screen
5af152b0-b6d4-47eb-91d6-bd8589de25b8	${rolesScopeConsentText}	consent.screen.text
5af152b0-b6d4-47eb-91d6-bd8589de25b8	false	include.in.token.scope
42cc9b6b-5715-4721-bd05-47c7507840f1	false	display.on.consent.screen
42cc9b6b-5715-4721-bd05-47c7507840f1		consent.screen.text
42cc9b6b-5715-4721-bd05-47c7507840f1	false	include.in.token.scope
e3c878a1-9bec-4f37-a5e0-84f3561e9d65	false	display.on.consent.screen
e3c878a1-9bec-4f37-a5e0-84f3561e9d65	true	include.in.token.scope
e7f9379d-5bc0-481c-abc5-f1f8026fdd34	false	display.on.consent.screen
e7f9379d-5bc0-481c-abc5-f1f8026fdd34	false	include.in.token.scope
a3b9f256-1ff5-4108-be26-5da60bfc3877	false	display.on.consent.screen
a3b9f256-1ff5-4108-be26-5da60bfc3877	false	include.in.token.scope
9f0556fd-b362-47de-a330-b4219cf3c2a3	false	display.on.consent.screen
9f0556fd-b362-47de-a330-b4219cf3c2a3	false	include.in.token.scope
75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	true	display.on.consent.screen
75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	${organizationScopeConsentText}	consent.screen.text
75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	true	include.in.token.scope
cdcec106-3ff3-4861-b009-d792877b713c	true	display.on.consent.screen
cdcec106-3ff3-4861-b009-d792877b713c	${offlineAccessScopeConsentText}	consent.screen.text
617e9e7c-c22d-468e-a3ae-86385181237d	true	display.on.consent.screen
617e9e7c-c22d-468e-a3ae-86385181237d	${samlRoleListScopeConsentText}	consent.screen.text
e2261f11-2475-4538-bc0e-f663a4131459	false	display.on.consent.screen
a3d9b5bb-e717-4518-adbc-07bc0f692d64	true	display.on.consent.screen
a3d9b5bb-e717-4518-adbc-07bc0f692d64	${profileScopeConsentText}	consent.screen.text
a3d9b5bb-e717-4518-adbc-07bc0f692d64	true	include.in.token.scope
cd5bc29d-1eae-4363-b403-3cd338a2653f	true	display.on.consent.screen
cd5bc29d-1eae-4363-b403-3cd338a2653f	${emailScopeConsentText}	consent.screen.text
cd5bc29d-1eae-4363-b403-3cd338a2653f	true	include.in.token.scope
1aa1a3d0-d37d-4043-9c61-219994890dbe	true	display.on.consent.screen
1aa1a3d0-d37d-4043-9c61-219994890dbe	${addressScopeConsentText}	consent.screen.text
1aa1a3d0-d37d-4043-9c61-219994890dbe	true	include.in.token.scope
3471014d-13bf-4c91-82fe-e145e45ce62c	true	display.on.consent.screen
3471014d-13bf-4c91-82fe-e145e45ce62c	${phoneScopeConsentText}	consent.screen.text
3471014d-13bf-4c91-82fe-e145e45ce62c	true	include.in.token.scope
0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	true	display.on.consent.screen
0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	${rolesScopeConsentText}	consent.screen.text
0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	false	include.in.token.scope
44d90b70-00c8-485c-a91a-f77e616baf36	false	display.on.consent.screen
44d90b70-00c8-485c-a91a-f77e616baf36		consent.screen.text
44d90b70-00c8-485c-a91a-f77e616baf36	false	include.in.token.scope
3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	false	display.on.consent.screen
3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	true	include.in.token.scope
74f581d3-8e6c-4ffc-aa96-5780938ff437	false	display.on.consent.screen
74f581d3-8e6c-4ffc-aa96-5780938ff437	false	include.in.token.scope
30a49f27-9f43-47ee-8a2a-91143cd0a6c4	false	display.on.consent.screen
30a49f27-9f43-47ee-8a2a-91143cd0a6c4	false	include.in.token.scope
c46725a6-3bab-4231-afdb-b5d8ad4d9302	false	display.on.consent.screen
c46725a6-3bab-4231-afdb-b5d8ad4d9302	false	include.in.token.scope
b8df8620-7249-4102-a288-c70ca38e4eac	true	display.on.consent.screen
b8df8620-7249-4102-a288-c70ca38e4eac	${organizationScopeConsentText}	consent.screen.text
b8df8620-7249-4102-a288-c70ca38e4eac	true	include.in.token.scope
\.


--
-- Data for Name: client_scope_client; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_scope_client (client_id, scope_id, default_scope) FROM stdin;
d7e66ce3-0769-4b3d-9636-4893459eaf54	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
d7e66ce3-0769-4b3d-9636-4893459eaf54	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
d7e66ce3-0769-4b3d-9636-4893459eaf54	42cc9b6b-5715-4721-bd05-47c7507840f1	t
d7e66ce3-0769-4b3d-9636-4893459eaf54	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
d7e66ce3-0769-4b3d-9636-4893459eaf54	264770a9-8682-4235-83cf-2e12d59fd9ac	t
d7e66ce3-0769-4b3d-9636-4893459eaf54	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
d7e66ce3-0769-4b3d-9636-4893459eaf54	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
d7e66ce3-0769-4b3d-9636-4893459eaf54	dc32533a-1e41-47f9-b737-3b644b5713fa	f
d7e66ce3-0769-4b3d-9636-4893459eaf54	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
d7e66ce3-0769-4b3d-9636-4893459eaf54	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
d7e66ce3-0769-4b3d-9636-4893459eaf54	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	42cc9b6b-5715-4721-bd05-47c7507840f1	t
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	264770a9-8682-4235-83cf-2e12d59fd9ac	t
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	dc32533a-1e41-47f9-b737-3b644b5713fa	f
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	42cc9b6b-5715-4721-bd05-47c7507840f1	t
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	264770a9-8682-4235-83cf-2e12d59fd9ac	t
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	dc32533a-1e41-47f9-b737-3b644b5713fa	f
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
ad59be04-8aba-4bf8-9fb3-681aabc1e4a5	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
cb742081-b162-4207-9130-f1b5f073fd9c	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
cb742081-b162-4207-9130-f1b5f073fd9c	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
cb742081-b162-4207-9130-f1b5f073fd9c	42cc9b6b-5715-4721-bd05-47c7507840f1	t
cb742081-b162-4207-9130-f1b5f073fd9c	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
cb742081-b162-4207-9130-f1b5f073fd9c	264770a9-8682-4235-83cf-2e12d59fd9ac	t
cb742081-b162-4207-9130-f1b5f073fd9c	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
cb742081-b162-4207-9130-f1b5f073fd9c	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
cb742081-b162-4207-9130-f1b5f073fd9c	dc32533a-1e41-47f9-b737-3b644b5713fa	f
cb742081-b162-4207-9130-f1b5f073fd9c	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
cb742081-b162-4207-9130-f1b5f073fd9c	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
cb742081-b162-4207-9130-f1b5f073fd9c	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
44f1605b-be38-4157-ab34-194b13dc41c6	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
44f1605b-be38-4157-ab34-194b13dc41c6	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
44f1605b-be38-4157-ab34-194b13dc41c6	42cc9b6b-5715-4721-bd05-47c7507840f1	t
44f1605b-be38-4157-ab34-194b13dc41c6	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
44f1605b-be38-4157-ab34-194b13dc41c6	264770a9-8682-4235-83cf-2e12d59fd9ac	t
44f1605b-be38-4157-ab34-194b13dc41c6	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
44f1605b-be38-4157-ab34-194b13dc41c6	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
44f1605b-be38-4157-ab34-194b13dc41c6	dc32533a-1e41-47f9-b737-3b644b5713fa	f
44f1605b-be38-4157-ab34-194b13dc41c6	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
44f1605b-be38-4157-ab34-194b13dc41c6	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
44f1605b-be38-4157-ab34-194b13dc41c6	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	42cc9b6b-5715-4721-bd05-47c7507840f1	t
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	264770a9-8682-4235-83cf-2e12d59fd9ac	t
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	dc32533a-1e41-47f9-b737-3b644b5713fa	f
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
500b5c86-ba2e-4345-8602-4e8576a82347	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
500b5c86-ba2e-4345-8602-4e8576a82347	44d90b70-00c8-485c-a91a-f77e616baf36	t
500b5c86-ba2e-4345-8602-4e8576a82347	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
500b5c86-ba2e-4345-8602-4e8576a82347	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
500b5c86-ba2e-4345-8602-4e8576a82347	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
500b5c86-ba2e-4345-8602-4e8576a82347	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
500b5c86-ba2e-4345-8602-4e8576a82347	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
500b5c86-ba2e-4345-8602-4e8576a82347	cdcec106-3ff3-4861-b009-d792877b713c	f
500b5c86-ba2e-4345-8602-4e8576a82347	3471014d-13bf-4c91-82fe-e145e45ce62c	f
500b5c86-ba2e-4345-8602-4e8576a82347	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
500b5c86-ba2e-4345-8602-4e8576a82347	b8df8620-7249-4102-a288-c70ca38e4eac	f
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	44d90b70-00c8-485c-a91a-f77e616baf36	t
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	cdcec106-3ff3-4861-b009-d792877b713c	f
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	3471014d-13bf-4c91-82fe-e145e45ce62c	f
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	b8df8620-7249-4102-a288-c70ca38e4eac	f
06f667d2-3e90-4e6f-af50-8e8a833198b4	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
06f667d2-3e90-4e6f-af50-8e8a833198b4	44d90b70-00c8-485c-a91a-f77e616baf36	t
06f667d2-3e90-4e6f-af50-8e8a833198b4	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
06f667d2-3e90-4e6f-af50-8e8a833198b4	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
06f667d2-3e90-4e6f-af50-8e8a833198b4	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
06f667d2-3e90-4e6f-af50-8e8a833198b4	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
06f667d2-3e90-4e6f-af50-8e8a833198b4	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
06f667d2-3e90-4e6f-af50-8e8a833198b4	cdcec106-3ff3-4861-b009-d792877b713c	f
06f667d2-3e90-4e6f-af50-8e8a833198b4	3471014d-13bf-4c91-82fe-e145e45ce62c	f
06f667d2-3e90-4e6f-af50-8e8a833198b4	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
06f667d2-3e90-4e6f-af50-8e8a833198b4	b8df8620-7249-4102-a288-c70ca38e4eac	f
3fc86730-d04c-4cc7-af16-13a708999082	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
3fc86730-d04c-4cc7-af16-13a708999082	44d90b70-00c8-485c-a91a-f77e616baf36	t
3fc86730-d04c-4cc7-af16-13a708999082	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
3fc86730-d04c-4cc7-af16-13a708999082	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
3fc86730-d04c-4cc7-af16-13a708999082	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
3fc86730-d04c-4cc7-af16-13a708999082	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
3fc86730-d04c-4cc7-af16-13a708999082	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
3fc86730-d04c-4cc7-af16-13a708999082	cdcec106-3ff3-4861-b009-d792877b713c	f
3fc86730-d04c-4cc7-af16-13a708999082	3471014d-13bf-4c91-82fe-e145e45ce62c	f
3fc86730-d04c-4cc7-af16-13a708999082	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
3fc86730-d04c-4cc7-af16-13a708999082	b8df8620-7249-4102-a288-c70ca38e4eac	f
de442f71-6200-4f81-918d-da9fdeea6e9b	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
de442f71-6200-4f81-918d-da9fdeea6e9b	44d90b70-00c8-485c-a91a-f77e616baf36	t
de442f71-6200-4f81-918d-da9fdeea6e9b	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
de442f71-6200-4f81-918d-da9fdeea6e9b	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
de442f71-6200-4f81-918d-da9fdeea6e9b	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
de442f71-6200-4f81-918d-da9fdeea6e9b	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
de442f71-6200-4f81-918d-da9fdeea6e9b	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
de442f71-6200-4f81-918d-da9fdeea6e9b	cdcec106-3ff3-4861-b009-d792877b713c	f
de442f71-6200-4f81-918d-da9fdeea6e9b	3471014d-13bf-4c91-82fe-e145e45ce62c	f
de442f71-6200-4f81-918d-da9fdeea6e9b	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
de442f71-6200-4f81-918d-da9fdeea6e9b	b8df8620-7249-4102-a288-c70ca38e4eac	f
7f207e63-5406-447c-9a3b-97cdddc5e07a	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
7f207e63-5406-447c-9a3b-97cdddc5e07a	44d90b70-00c8-485c-a91a-f77e616baf36	t
7f207e63-5406-447c-9a3b-97cdddc5e07a	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
7f207e63-5406-447c-9a3b-97cdddc5e07a	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
7f207e63-5406-447c-9a3b-97cdddc5e07a	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
7f207e63-5406-447c-9a3b-97cdddc5e07a	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
7f207e63-5406-447c-9a3b-97cdddc5e07a	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
7f207e63-5406-447c-9a3b-97cdddc5e07a	cdcec106-3ff3-4861-b009-d792877b713c	f
7f207e63-5406-447c-9a3b-97cdddc5e07a	3471014d-13bf-4c91-82fe-e145e45ce62c	f
7f207e63-5406-447c-9a3b-97cdddc5e07a	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
7f207e63-5406-447c-9a3b-97cdddc5e07a	b8df8620-7249-4102-a288-c70ca38e4eac	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	44d90b70-00c8-485c-a91a-f77e616baf36	t
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	cdcec106-3ff3-4861-b009-d792877b713c	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	3471014d-13bf-4c91-82fe-e145e45ce62c	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	b8df8620-7249-4102-a288-c70ca38e4eac	f
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	c46725a6-3bab-4231-afdb-b5d8ad4d9302	t
b4b39689-8818-4208-b102-ee758dad2268	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
b4b39689-8818-4208-b102-ee758dad2268	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
b4b39689-8818-4208-b102-ee758dad2268	42cc9b6b-5715-4721-bd05-47c7507840f1	t
b4b39689-8818-4208-b102-ee758dad2268	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
b4b39689-8818-4208-b102-ee758dad2268	264770a9-8682-4235-83cf-2e12d59fd9ac	t
b4b39689-8818-4208-b102-ee758dad2268	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
b4b39689-8818-4208-b102-ee758dad2268	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
b4b39689-8818-4208-b102-ee758dad2268	dc32533a-1e41-47f9-b737-3b644b5713fa	f
b4b39689-8818-4208-b102-ee758dad2268	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
b4b39689-8818-4208-b102-ee758dad2268	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
b4b39689-8818-4208-b102-ee758dad2268	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
15735a86-4946-440b-9251-0e8487f6eb01	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
15735a86-4946-440b-9251-0e8487f6eb01	44d90b70-00c8-485c-a91a-f77e616baf36	t
15735a86-4946-440b-9251-0e8487f6eb01	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
15735a86-4946-440b-9251-0e8487f6eb01	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
15735a86-4946-440b-9251-0e8487f6eb01	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
15735a86-4946-440b-9251-0e8487f6eb01	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
15735a86-4946-440b-9251-0e8487f6eb01	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
15735a86-4946-440b-9251-0e8487f6eb01	cdcec106-3ff3-4861-b009-d792877b713c	f
15735a86-4946-440b-9251-0e8487f6eb01	3471014d-13bf-4c91-82fe-e145e45ce62c	f
15735a86-4946-440b-9251-0e8487f6eb01	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
15735a86-4946-440b-9251-0e8487f6eb01	b8df8620-7249-4102-a288-c70ca38e4eac	f
\.


--
-- Data for Name: client_scope_role_mapping; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.client_scope_role_mapping (scope_id, role_id) FROM stdin;
9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	973da7a0-958d-44bf-9eb4-434cbb674f8d
cdcec106-3ff3-4861-b009-d792877b713c	6c041705-4c82-43a4-b844-5cd1b40ce642
\.


--
-- Data for Name: component; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.component (id, name, parent_id, provider_id, provider_type, realm_id, sub_type) FROM stdin;
cc6666bf-619d-4042-9cc2-01c00dcd0bf7	Trusted Hosts	eacf1fae-7916-43d5-b7e0-7abf35df7d49	trusted-hosts	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	anonymous
004ee8f3-24cb-42b8-9a7f-7b6bdb1f8238	Consent Required	eacf1fae-7916-43d5-b7e0-7abf35df7d49	consent-required	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	anonymous
7451306c-d69a-47c2-bef8-d400e814a022	Full Scope Disabled	eacf1fae-7916-43d5-b7e0-7abf35df7d49	scope	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	anonymous
c49e8c59-6d59-4ddc-93ce-80b6bd2e9a36	Max Clients Limit	eacf1fae-7916-43d5-b7e0-7abf35df7d49	max-clients	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	anonymous
986e17c9-7b65-4c59-a3ae-a036f503d6fe	Allowed Protocol Mapper Types	eacf1fae-7916-43d5-b7e0-7abf35df7d49	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	anonymous
b536867e-46a5-4724-a728-255b53800fb5	Allowed Client Scopes	eacf1fae-7916-43d5-b7e0-7abf35df7d49	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	anonymous
e25985fe-a8fc-4324-8b09-2610802dfedf	Allowed Protocol Mapper Types	eacf1fae-7916-43d5-b7e0-7abf35df7d49	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	authenticated
3fc732f8-497d-48f3-a9c8-07063900d0ba	Allowed Client Scopes	eacf1fae-7916-43d5-b7e0-7abf35df7d49	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	authenticated
2754d8ba-3ffe-4198-bd19-d0b63738bc71	rsa-generated	eacf1fae-7916-43d5-b7e0-7abf35df7d49	rsa-generated	org.keycloak.keys.KeyProvider	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N
46f8c388-7d46-48db-976f-7255556eb2ef	rsa-enc-generated	eacf1fae-7916-43d5-b7e0-7abf35df7d49	rsa-enc-generated	org.keycloak.keys.KeyProvider	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N
20e18d54-c003-4e66-b8fd-2853f840aebc	hmac-generated-hs512	eacf1fae-7916-43d5-b7e0-7abf35df7d49	hmac-generated	org.keycloak.keys.KeyProvider	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N
59b63ce0-a580-420b-8560-a799a7c3939e	aes-generated	eacf1fae-7916-43d5-b7e0-7abf35df7d49	aes-generated	org.keycloak.keys.KeyProvider	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N
57f8fe46-013e-460e-917f-4db57429e9b7	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	declarative-user-profile	org.keycloak.userprofile.UserProfileProvider	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N
9414449d-8ef8-4ea1-b7cd-2aa20f90b873	rsa-generated	2c411af7-e0b7-4547-b08a-27c7c8c1722c	rsa-generated	org.keycloak.keys.KeyProvider	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N
9c4d8ab8-cf78-4dca-955d-72b8a42c5b6d	rsa-enc-generated	2c411af7-e0b7-4547-b08a-27c7c8c1722c	rsa-enc-generated	org.keycloak.keys.KeyProvider	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N
7c7f7c14-e904-4418-99a2-fcdccc69ef11	hmac-generated-hs512	2c411af7-e0b7-4547-b08a-27c7c8c1722c	hmac-generated	org.keycloak.keys.KeyProvider	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N
1e2cd82f-3ea1-4e0a-86fb-d2e36a87c888	aes-generated	2c411af7-e0b7-4547-b08a-27c7c8c1722c	aes-generated	org.keycloak.keys.KeyProvider	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N
a6ab499b-5931-4b4d-9635-05e1f60e3020	Trusted Hosts	2c411af7-e0b7-4547-b08a-27c7c8c1722c	trusted-hosts	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anonymous
410a1950-f9fe-4993-bd45-fae0ad915a25	Consent Required	2c411af7-e0b7-4547-b08a-27c7c8c1722c	consent-required	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anonymous
ba594c35-6d77-4970-a9df-6655781ec748	Full Scope Disabled	2c411af7-e0b7-4547-b08a-27c7c8c1722c	scope	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anonymous
70cc69a8-713d-4bef-8bed-d2507d0d732f	Max Clients Limit	2c411af7-e0b7-4547-b08a-27c7c8c1722c	max-clients	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anonymous
d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	Allowed Protocol Mapper Types	2c411af7-e0b7-4547-b08a-27c7c8c1722c	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anonymous
10389cd5-0d51-4f36-bbc9-430364552af2	Allowed Client Scopes	2c411af7-e0b7-4547-b08a-27c7c8c1722c	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anonymous
663da0ca-2ffc-4f05-a10a-92fca2d5801c	Allowed Protocol Mapper Types	2c411af7-e0b7-4547-b08a-27c7c8c1722c	allowed-protocol-mappers	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	authenticated
30906581-3857-437a-a7bd-e427d886322e	Allowed Client Scopes	2c411af7-e0b7-4547-b08a-27c7c8c1722c	allowed-client-templates	org.keycloak.services.clientregistration.policy.ClientRegistrationPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	authenticated
f7e93b87-32a8-4ebc-b8fc-912d402a9436	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	declarative-user-profile	org.keycloak.userprofile.UserProfileProvider	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N
\.


--
-- Data for Name: component_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.component_config (id, component_id, name, value) FROM stdin;
e17bee30-e698-4f97-806b-5958d90cb161	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	saml-user-attribute-mapper
af0fe80f-601a-4adb-bffd-18010493116d	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	saml-role-list-mapper
1a40f160-9bf8-42cf-bcc2-445c20f4027d	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
6a663ef0-e0a2-4a24-8d2a-43bac1c4e7d2	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	oidc-full-name-mapper
f4b50183-dbd2-40dd-a234-f9598dfe3f6e	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	oidc-address-mapper
5f18579b-ea6a-43b9-8e6d-00871359a0c2	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	saml-user-property-mapper
a589b910-108d-40e2-a04b-5a2927e1b4d6	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
c44530d9-d310-422c-bc3c-3761fb661aa4	e25985fe-a8fc-4324-8b09-2610802dfedf	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
58270a92-e7ed-43e2-9713-15f488cd7d87	c49e8c59-6d59-4ddc-93ce-80b6bd2e9a36	max-clients	200
54084800-96ad-4e4a-a64c-d5caccdf6a96	3fc732f8-497d-48f3-a9c8-07063900d0ba	allow-default-scopes	true
dadf436b-31e2-40fa-909d-af678a2ca621	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	oidc-address-mapper
c63c70d4-2a04-437b-a005-b5e10ce217c6	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
bcd77e4a-bd02-4310-bc62-f2201d065253	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	oidc-full-name-mapper
b70b3917-524f-43fa-8faf-80a8648f2ec1	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
a4cb7f69-103f-430c-8a85-01b27b6cdd56	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	saml-user-attribute-mapper
277d93c3-86d5-46cf-8d02-f74ffb425ceb	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	saml-user-property-mapper
d4180959-73b2-4da7-a5c5-ab4a89c729c0	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
012f6623-5d1d-470a-8be6-7b25ddd42c76	986e17c9-7b65-4c59-a3ae-a036f503d6fe	allowed-protocol-mapper-types	saml-role-list-mapper
9364c183-31f5-4d0b-aa68-84b34a1858f4	cc6666bf-619d-4042-9cc2-01c00dcd0bf7	host-sending-registration-request-must-match	true
c9edf7ff-33f8-4b13-ae45-74f890f7679c	cc6666bf-619d-4042-9cc2-01c00dcd0bf7	client-uris-must-match	true
66697914-b04c-4933-93da-088e80829a85	b536867e-46a5-4724-a728-255b53800fb5	allow-default-scopes	true
e75540b5-028d-454c-bcd7-c17c2420f656	46f8c388-7d46-48db-976f-7255556eb2ef	algorithm	RSA-OAEP
c9cf9fc8-9017-49be-8da5-59dd7a496e85	46f8c388-7d46-48db-976f-7255556eb2ef	certificate	MIICmzCCAYMCBgGcPxAB5jANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjYwMjA4MjEwMDM5WhcNMzYwMjA4MjEwMjE5WjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCf5cN6dOqZBj3jFne6IbgFuLA2gz7o225isgek228YU+QOswwY8ggnt1WXNcvm+l8LQ6yKLtVhfVryWyl7cg0nnt5Hp3auMmjgyZwA0a0AYIKtREjC7UmE0JgRbpeAPE6vJoS/fAs8fayigcNOtT8ygbP8WIMtV9T+9yChsZtSi35pI5udn9hjkyaz6oPWdprXa8C37gETC7bt2ESsUtLOhJvbX2yZvTVE+A8rLod3+IiDy99elt1uA9OTQXUBz3pdw78pWd2mzz6TGRcX6vlrfBSQBFrmqj8S85VM2VMLx/HgpzbyftA1o26nLVNS6actyWy2TExhQBP5HHyGHRpPAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAJ9obAnxE1I/o7p61aIGcqBq/XWLo52j30ddScYpC9Ry+rPAunrqizhqZONgASNhjsIzZjXsRM0reJCw22LYsOBhuVBqrxam8I1lT7rYdgFnO2zdixpDG3WpzK40scsS6vmqgRH0dybhkmNdWrERQ9MAYAQhz5dKGDezQLYH30Grn0HUYMU4+AAS8Kn3/3U1f857nUR9AzQ36bLN+gps+3vXUDtvOmlqTDVbv4Ee1tV5yhDWopUaX1wyuuykmXNKlwrgkODduq1aUWM0rwJVOzoLS72IMpK0HImFrYWpqFPMHOaknj7V29gethqVKsnAdxTa4hVehK7//ycbT2vnGEs=
a8cd54ef-2ed7-4c9e-ac1f-3bab30140fcd	46f8c388-7d46-48db-976f-7255556eb2ef	privateKey	MIIEogIBAAKCAQEAn+XDenTqmQY94xZ3uiG4BbiwNoM+6NtuYrIHpNtvGFPkDrMMGPIIJ7dVlzXL5vpfC0Osii7VYX1a8lspe3INJ57eR6d2rjJo4MmcANGtAGCCrURIwu1JhNCYEW6XgDxOryaEv3wLPH2sooHDTrU/MoGz/FiDLVfU/vcgobGbUot+aSObnZ/YY5Mms+qD1naa12vAt+4BEwu27dhErFLSzoSb219smb01RPgPKy6Hd/iIg8vfXpbdbgPTk0F1Ac96XcO/KVndps8+kxkXF+r5a3wUkARa5qo/EvOVTNlTC8fx4Kc28n7QNaNupy1TUumnLclstkxMYUAT+Rx8hh0aTwIDAQABAoIBAEaM9enPsX1QZDkQ/kXJv+0CVvnOghDzVOrGO5oxWfzlcwBLXwCYtiF0Apdj3LJu8UXCl9wmmu7XhSvfLlfx9Dzxm4kJKlPlGSJpwmQYH9nFO5NgyCv9z80Czr4OSlmCAoPEnpjwjfKkTuorEDZnwVkzImuq0EJO+UOAXc0KVQqfn5odyPYrGOhqQv9H5aKieoQxvP9TdpxFSual7W4WQshMULg7f9OAvI3VUwa5EFZxTnVwOxVfztEQ1rZ15G0Qof7OgSq5XBMBqYEuqmc6Fb2//i4GNbW+tC0hF3gsVTGt3gf7muvlstREt2iiYUXBoRXn7eHCJNwT4kyNInmM3+0CgYEA3fPW5D1aUQggbaUpantr7hATOqd4q0F2Z1Apse9JNMg1g0VA8QL0QurepT0ssx3fc0feMAj6Ixt1ahqjMxgHKtCrpXqypgqlGE8NSljyFKezGsweSL+Ea5PwLo0Rvj5HXdii0TfG1GqSFQpqRARPW/Br3ZnvmIqNyhoUxZh2ubsCgYEAuG0AO+BE1CPM9WnBibtctw0Y0LQ6Mn4qfiBItqM0/57VVchqd9yheGZzTOHhzrC6fjz/fP2Pe1+xYRJFccTWiqH4PiVi0NKS1SRa4Q9xQGC9O4+nO+93k3+sxev6+FnfJj2/7bQpc5I8K7ppq806qPHdxWsXoTbY+SG4kDrZnn0CgYBuAKkTi7jUimOQFBh3tt3iKkNtgY0Ty6kEQT24+3Bb4ZJsEgnCqYUoGUHpwW0DBR43A3qCciCO/8/sm3EhJJqAxNUdebdLBeGXL67Vl0m7pPXmpR2pTooxyytx1ubhU/qI75KagLthkcP++595QG2YkorTVLTj9F+bt9ttp0fIewKBgF2eV2QNsGLP2ZcqnChCiAoUB+jJ1FEVYpSr5r1vk9O+2SS2m/VEdmMb/qOkdm/pnoG+jSLxxAgox24zTDU4an/tQIqrh8HhYs/3qHpe0GqRsP2vKoFuShEB2r6Nz9SKKpDK/8a2keQs84ZvFn0zrPdd7+nrNw+LPBEbYQk2FooxAoGATbb2lWJOHbHLura/ktYIS9dfBv60KEOByVG4SWkCPoWjbrkk/9p24/h1ECb5xaEvXuF9cJisQvn5kavUImXSMdByLvOTZ91Km26WQKYj4L9CQPThUSEOYgsRbFUbvEnAnFhA2Y+wjrln9kEFfoPLgbwurgYPw2OnJ5juDhN6lxY=
b20acf6f-54d0-4ce4-9139-f589170ad1db	46f8c388-7d46-48db-976f-7255556eb2ef	keyUse	ENC
95952fd2-c220-4514-9718-2f54cf6da10e	46f8c388-7d46-48db-976f-7255556eb2ef	priority	100
ebebd001-4798-4b57-bca8-f03f42974214	57f8fe46-013e-460e-917f-4db57429e9b7	kc.user.profile.config	{"attributes":[{"name":"username","displayName":"${username}","validations":{"length":{"min":3,"max":255},"username-prohibited-characters":{},"up-username-not-idn-homograph":{}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"email","displayName":"${email}","validations":{"email":{},"length":{"max":255}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"firstName","displayName":"${firstName}","validations":{"length":{"max":255},"person-name-prohibited-characters":{}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"lastName","displayName":"${lastName}","validations":{"length":{"max":255},"person-name-prohibited-characters":{}},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false}],"groups":[{"name":"user-metadata","displayHeader":"User metadata","displayDescription":"Attributes, which refer to user metadata"}]}
8ed9336d-c164-4e73-a2e7-0191663914be	20e18d54-c003-4e66-b8fd-2853f840aebc	kid	17109e59-9d3e-4315-bde7-3e93c8fae6b7
4658d5e8-8b55-40a2-92ac-9a716b36578f	20e18d54-c003-4e66-b8fd-2853f840aebc	secret	u4-W96cl-Ik-FqtQPgUY6dZ75HMkpnSsEUBFw3qdjMh-xYseiJPi8F3BvhPofpuicrjH4r9c5INn_vY3sjOjsqjQwrzAimR3eqAwKwW_ZLfwZYz2dQbLCf7ABo4-qZCJPcIpObqSZY4VT1PKNk_aLDZENkiMuAdFSHVh4vdIbGc
f41628fa-a379-4efc-aaa7-db110080dcc5	20e18d54-c003-4e66-b8fd-2853f840aebc	priority	100
fadb986d-0228-4439-86f7-04b09d20575d	20e18d54-c003-4e66-b8fd-2853f840aebc	algorithm	HS512
c231ac56-c60b-4b3f-9c50-2dfaffc15fa9	59b63ce0-a580-420b-8560-a799a7c3939e	kid	16a8a36c-21e2-475d-a316-79d8872a0406
e74dd72c-18c4-4d59-9d7b-15e049cd64ee	59b63ce0-a580-420b-8560-a799a7c3939e	priority	100
0127e6ef-a78d-4f61-b214-45ccb539a09e	59b63ce0-a580-420b-8560-a799a7c3939e	secret	Prlc-zzvGnwNvKv61l90xw
a22eeb1b-5393-4404-b45a-eb464768cea0	2754d8ba-3ffe-4198-bd19-d0b63738bc71	privateKey	MIIEoQIBAAKCAQEAojs3aCPqVycMHZEdzP/hpDvlkSckkAXbRSBUwdYxde8VQghdDonxnfc1byjQN+zhdPog2p0z65rUxO4pSMjI40/8j7sJSeRnF9nQkbAQZwK0hc6OAUi2Ebn+cyXXT6Q4oXSykzZsf7pjukY9XN23FRMgVEkCqPZ8OJavocNhTI5IZ/pJ+S23IPV1VX5Ft5cT/ElNTvTm6KXqbMbtMqSwmymf9avq9LEFhDe6b40FzZK5lyOxcfZirZN5RVyZkG1RBpgnyNlGVyFBFZFswj6zuKGglcNwCDpPBa3YkTmsnwzHHMMIoXL+71hSZ0BBv7KZMHJun3yw40i928JBAtCuFwIDAQABAoH/fdksLcALz6cpViN218piHRDlhQX7S2E/rCX/yIz3i6f3ssHKKKAITur2fPNPHp7GpAOTvr00T4UGt49O676nusW6j2fxBuFKuvulxKRQFQ0+WgLWPVdNWlu0Kp8kod2gELbfFlP+1uhAXXo2wsf2BFeXyFYgrn1v9wGoDrG8MbF9plhLBJzyCnifiwUcfLUJGiqdSIks17VJzFZxcET/CMVZHalKT+DKRnwQiIrX7tLOiWVNv29hzojq7zDccul3YFyZxqSr3yN5RcxltWIfB+K9QgYQBXuiNNtKhx3hlu1NB9O1Kr4I+R0kzPzyPrjY7AQUME69qk0I++XbYNQlAoGBANL4M5HICOChnJO+fb+FJtAaOLkJF+jOvkfdkHg8ZTJvE/s/p1qNYQPmyTP/HSv9KYegYivdaKfVIv48G11EtUs0XB6J3amz62xD1QlOS42/Y5kbl1rajHZZrokJnPpK5pRyE4CDefevkIUBbL9KbQHVLlf1SgoQcmtVnMRQupETAoGBAMTb3FslBMZreU6Ouz3/z/rErsxppY6TlJ0LGGE2BJJ26slciBzjqu5Bun6Qd697aMTdeZj3RVC2NcW5uBhBdtuN5oR4CFYSBfuqL2zRsOvmXax4bUusAlDW9bRJJtzlPhHokpJhAsmfcwqBQR1f9fWRHWo//rXb3ZBxX4ZrAZNtAoGBAKqSuz9XOLZGdM6P6iP7iFIhoVMaIxa8ceSxI6nTSw7n+IPgB3OTc6kv4+YCkpeKbRWXe0h0D7YDAfQErStP7jUL9J9MYMhhDCvQ/GI1x6in4eNdB5cRtRfLku6Bs0Y7YQsM4O+7XdYBQRwI9uADUPd2Ya4ESQSyH5Dg+4tOqkm5AoGAcBwyCyoy5PlR9V4t3mowPMUEM1+7LE555VHrSXlk8zCMF679yU4TC2sdVXTa5HIowWzMEkRIEmYii39wC0hE81aFwE1HmhTbmW5bYeKtmjrwgAd5Xw4Pp5A0D79VRZm8VqCX0Is09jQ7ZPElbyA2R+qj0N2vJkyXiuo2F6wbEqUCgYB4MiKi3r7+H6fgLOO/DFmvoSCteC8yzzHfst/pGiRZKSAgNMyxSAQlg31/ZImZxkWEgQqY+oGJeO0DieWg4/ZNpCUVPeig22rsHP5/j++uoFuU+LC0TuDlSxeyxNjB1TJnuZdtrmsxJ44SvUHNXYYO3dluKmuhPUM1g7QkiQZfHg==
1de57a14-e67e-400e-8fd7-9d471d59daa9	2754d8ba-3ffe-4198-bd19-d0b63738bc71	priority	100
677dad97-6814-4c54-9267-13615329698b	2754d8ba-3ffe-4198-bd19-d0b63738bc71	certificate	MIICmzCCAYMCBgGcPw/+/DANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZtYXN0ZXIwHhcNMjYwMjA4MjEwMDM4WhcNMzYwMjA4MjEwMjE4WjARMQ8wDQYDVQQDDAZtYXN0ZXIwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQCiOzdoI+pXJwwdkR3M/+GkO+WRJySQBdtFIFTB1jF17xVCCF0OifGd9zVvKNA37OF0+iDanTPrmtTE7ilIyMjjT/yPuwlJ5GcX2dCRsBBnArSFzo4BSLYRuf5zJddPpDihdLKTNmx/umO6Rj1c3bcVEyBUSQKo9nw4lq+hw2FMjkhn+kn5Lbcg9XVVfkW3lxP8SU1O9Obopepsxu0ypLCbKZ/1q+r0sQWEN7pvjQXNkrmXI7Fx9mKtk3lFXJmQbVEGmCfI2UZXIUEVkWzCPrO4oaCVw3AIOk8FrdiROayfDMccwwihcv7vWFJnQEG/spkwcm6ffLDjSL3bwkEC0K4XAgMBAAEwDQYJKoZIhvcNAQELBQADggEBADN1pxRuc4e64VYYw7uCi+iJ5RZvlgG2MKfWw1BcdhqYp3sPcQZwzqc2j9msS3ZSEsf+moatyuarHxyI9q9goAJmL27jeT97b4GfYwdFcFs8NuFSpnsKqPx/JcXRUH5wZbZykLVcbbkvdKak1kZxCBlpX0IPYHXBDhWsMN9r4dSp2cvrTJYAEHfIpTqxRyEBDDfWR0qzyCk/GJK/Er7FcatYp3PRf9yAkfQYn673iOb3UqvQ9f1LPnacgcef+DS7J4QtCFviIypS9aL/+axf0B5tMGkn83/+wRJDxDfMvl4YYRU+b1d8GwOuGApCEaEax/L6f2C7hybasO/4YzCR2So=
e83835af-b059-4c6c-b060-4c0cb58730ff	2754d8ba-3ffe-4198-bd19-d0b63738bc71	keyUse	SIG
18322427-b580-44fd-aaac-831693d5362d	7c7f7c14-e904-4418-99a2-fcdccc69ef11	priority	100
05d7b933-a126-43c8-a360-96ccef2f7e67	7c7f7c14-e904-4418-99a2-fcdccc69ef11	secret	wHUKIutJynb1UKpB1bEzpLzO3eyOqjmCSv3lxGIVIHR0Cuazc-AeyYvl9jdqyD8-wZ581JaD8HAMv3iAE724mOVoYC88z1v8vIlacqM-GKcD93D35kUmQQnldHNYweIZyZU3hoUcpIJTIS7V71l-kWqZ2Og784P0uNc-vbiJkoc
491e0fc7-954e-42d7-b68c-639974dcfcad	7c7f7c14-e904-4418-99a2-fcdccc69ef11	algorithm	HS512
666e1bc6-cd2c-49fb-8a84-d93cbfd1c769	7c7f7c14-e904-4418-99a2-fcdccc69ef11	kid	19021244-a9ba-40fd-9aaf-d318d9a5cc8f
907a21dc-31ce-4635-990d-030afeadcd9d	9414449d-8ef8-4ea1-b7cd-2aa20f90b873	certificate	MIICmzCCAYMCBgGcPxjx3DANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZ0c2tocmEwHhcNMjYwMjA4MjExMDI1WhcNMzYwMjA4MjExMjA1WjARMQ8wDQYDVQQDDAZ0c2tocmEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQC0Jr+tTOixHi55D1gmtb+Bfhp2dmn1brkFf0WKfMOCO4ie85qM9NPqWjpayMvJ0ouhUwot/g5KFiPQQAwY/cQ15bBFv2q5Lg1E77enjdCWQvRuVhI0K8mOUY1csLty857KlgosdhzvK1ApUhERq+IpX6/GDhLZtptvOdv1Z/YhW8wsp/huZTq1787CYdehfKU5Lt/HBQNaecJhphsTEnGqnImmIFukJb2PIPFs7bTLl5cSp/K5dhnX/8zis1ilZj9ezopvky6A6ZfgP0rtSqzG3Wgk5Zu0odq4QTxquxikMQF/ahJgSlakiOqHTPNPKJnzJDs4SH8wEngLap7QP6wtAgMBAAEwDQYJKoZIhvcNAQELBQADggEBAHE1fIF7RGSXBuXMg6lZsTv0Afj43j2ijRZmrV6YHgfPQLjRXLN3dhiXovzlihfRSRp/9zggDpg0szf7+gkT+n/r9Dhlp0XZI6Or1ayPldi42faoxlaLFdyMRsKSUcevSXke6W9fr9LS+i7R7f6JVUoKjQWLdcFGNmJhg2L+OY2tz6r1D6tb+ap5Px6f54IXue9Y9Abnavtp5gh++W8d8agNxT6/78O4u1NWJOmHrsOD3c28XO/mJo+HNSvFwDDGbGIr3jx4PtloI6pjNsqW6vw9sYa8fr2D/DFFXqUqCD7hJ3R/19NyNMgGL7jEweXTnbiHA2C8Cu1+W8Rt7Ic/gNY=
380b551f-13aa-4722-8560-b55e0aa30aec	9414449d-8ef8-4ea1-b7cd-2aa20f90b873	keyUse	SIG
ad77f18e-31be-49da-a532-ed74bbe9e482	9414449d-8ef8-4ea1-b7cd-2aa20f90b873	privateKey	MIIEpAIBAAKCAQEAtCa/rUzosR4ueQ9YJrW/gX4adnZp9W65BX9FinzDgjuInvOajPTT6lo6WsjLydKLoVMKLf4OShYj0EAMGP3ENeWwRb9quS4NRO+3p43QlkL0blYSNCvJjlGNXLC7cvOeypYKLHYc7ytQKVIREaviKV+vxg4S2babbznb9Wf2IVvMLKf4bmU6te/OwmHXoXylOS7fxwUDWnnCYaYbExJxqpyJpiBbpCW9jyDxbO20y5eXEqfyuXYZ1//M4rNYpWY/Xs6Kb5MugOmX4D9K7Uqsxt1oJOWbtKHauEE8arsYpDEBf2oSYEpWpIjqh0zzTyiZ8yQ7OEh/MBJ4C2qe0D+sLQIDAQABAoIBAAtwLWSNDkuBSX1CvzuqoleQCzvryKOpGCLJof+ebHxrmBZS4cR4NASnHhmPB7oPU0cW173eqbIZsJmY7hu1GxI6p0Pvw3sxTxg01IyVKWys9h+To/FqOVB/DD0ZyeENJ6R1vSd1srXFzSppIpp5txueOXHCCX+Hblw0HdY5olabmvslnPAZxeVYIBCwSGUcjVRVW/yXrGtJxPQZgpmP5FhgHjR3MJOO+OEU31J1opWvC9hJk++P5V/fQC9rMKZUXK6M9Xrrh9ZeBH3vFMZ+SiQoR/3AoXmJV+RbI0AzG8/Ib26ADNe7DI5U5I96pudMgi+7cehbaSX+jY2sEHUb0RECgYEA+mv+kYqiyZtk3N0ARcjsvSR0fXjpt++lp1PMBpLmdr4HIXBYtwLujQZhN3FDPvp+iwNrxTiLh/O/b0Oo7KFvmJb9PNC4NxlV7zapk8WwPpUCDiejTDdkwd+Jk74nPVhbVE3rK6rGt2rPm77fWtDE3Duqm27RWRhefriyP6OYKN0CgYEAuCoLO5XSwXcculerHVl1xK6NpdLl6GTn2Ypv4pydvamAM9geULvXcFmjVa5a9INMvqTNBhMQHNwD3XhHbB83mmTunzOcXewyhLiPoJJGJtzc/PR9XPpcYWe22O7ga6zxYmLSi6YYFBg+UM4/2chEodO8j+52OxKMYuw8sYWWs5ECgYAy//l5ZJWgn4AcJvoePDxSjPEYeJ6Iskq3WC6ODC7Zcfv7yGiY5QT2PZ1g8DU0x0ksQIcbRFfOWUrcexgVEQ+sMNvkHdHWjtdcf3JrwPAS3r/raBEuvX1MqpzXNPvC15LKCZBidUZBJoSfgHD2itv8yj4Fp70E+xyLjEvpAAVGFQKBgQCKUVmaaQ6fq5xyAEJOitA+5nMQpnNytcbExor+Am8e8d2OErXCITLP+SMJySgbGTpcvV4XP94MLtrgTeQmutOCLGhkPdklWa8fq5aEHRh/O8bmXaKCYK9doQ3dpJv9gyjQojRMGnVfMk4rVpzyLs4NVP/8gjdearHx4kg7dIAZYQKBgQCsDox1+W4n7GE2sklTqBV+towZrEM0Kpdhvrc23OzfO5wbEXVmjy3jdCuyEScY1/+x6IfpbEVNjO67mEhC+JUIRXll4vv0+vXU8iTKvMGex9b1Kj47NsE0ZqmNz9BkzcZK9Zz7sf8UdT55OawexbUDEQ3bD1weWFQXDLid+K/SYA==
aa902ebc-091c-4345-bfe8-ac68ac2c66d0	9414449d-8ef8-4ea1-b7cd-2aa20f90b873	priority	100
68cc6631-d196-4040-8a92-9d643976e69c	1e2cd82f-3ea1-4e0a-86fb-d2e36a87c888	priority	100
92cb9a54-2a48-4e7b-955f-cffefaae51d2	1e2cd82f-3ea1-4e0a-86fb-d2e36a87c888	secret	PDEjShQjvHrvpsuj19SAsg
62b245c4-44ad-45a9-bff3-672eb84cdd4e	1e2cd82f-3ea1-4e0a-86fb-d2e36a87c888	kid	9d00ed5f-b6d8-4650-b728-7bc96475c60f
7f789c88-3967-4db5-9c89-cb7e84dd81f1	9c4d8ab8-cf78-4dca-955d-72b8a42c5b6d	algorithm	RSA-OAEP
d7c8bb03-5388-4a2a-a63f-ab656bed8f1b	9c4d8ab8-cf78-4dca-955d-72b8a42c5b6d	certificate	MIICmzCCAYMCBgGcPxjz4zANBgkqhkiG9w0BAQsFADARMQ8wDQYDVQQDDAZ0c2tocmEwHhcNMjYwMjA4MjExMDI1WhcNMzYwMjA4MjExMjA1WjARMQ8wDQYDVQQDDAZ0c2tocmEwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDA0F28or9FZJFCaABaYvzcFd0LRhEJzVS6om10TfFPBukMG9h921iF4aFAPUPux9sg9iz2fzE9OhGOs6hrKbdB2rOBBwbRR3JgVVJOo2O0CbHpqCfqtKOT5IeZOvUXykzcC4wk52RLBDcHKrjAucXweMUPsaOGrNTE8yXduZkd+tnUmUyX9If50uJiJ0Ll3uaFW4Tok6Sfi2DeBInydenl9R8zZUJL+FL6F/03LyrlUou5sprk+nDBegj8fw3peQbtv2GmfHQyvar/mojJRIRZAg/DVtcbWm6vYFTjK4mpONFid/clzzcfQpmqJn4xOAHDs1AxQhsKeLVEVJbD2gJHAgMBAAEwDQYJKoZIhvcNAQELBQADggEBADWIKiH+bwhHRLTsymhuvURxAJzF2FDVI8kaKE0W0dUfnICt/ZMfA/ONeXMXbFFwIw+HGnL3jIF867olnTrlvNufDrxSsjPD7hJqiowcjMb7ZdwXypiolh4zPeH0ZXwpXhlZO8kkRsU2TpMjyFbkXj7KXiIB4tXtdH0my59DnaXdWXBhNWM73kse3J41EvySQEDGwC45AUyBzkzPTZ5jfcu5WYwbluGZf4KIqz5KX2qis30VdoKvGgl9wfP+f9Or0dMe/KJdtlKuxvsnw5ccixYH19q3jTkNbQmKpRkkDZwl18gJpXnqgTqkYbdMNM3wo6B7ajoDQNzKA8eU/tk46R8=
c92d009e-ed5a-4630-92d4-37f64cb33182	9c4d8ab8-cf78-4dca-955d-72b8a42c5b6d	priority	100
f32b78e3-2021-4f3f-a469-6e9cf33493a2	9c4d8ab8-cf78-4dca-955d-72b8a42c5b6d	privateKey	MIIEowIBAAKCAQEAwNBdvKK/RWSRQmgAWmL83BXdC0YRCc1UuqJtdE3xTwbpDBvYfdtYheGhQD1D7sfbIPYs9n8xPToRjrOoaym3QdqzgQcG0UdyYFVSTqNjtAmx6agn6rSjk+SHmTr1F8pM3AuMJOdkSwQ3Byq4wLnF8HjFD7GjhqzUxPMl3bmZHfrZ1JlMl/SH+dLiYidC5d7mhVuE6JOkn4tg3gSJ8nXp5fUfM2VCS/hS+hf9Ny8q5VKLubKa5PpwwXoI/H8N6XkG7b9hpnx0Mr2q/5qIyUSEWQIPw1bXG1pur2BU4yuJqTjRYnf3Jc83H0KZqiZ+MTgBw7NQMUIbCni1RFSWw9oCRwIDAQABAoIBAD6WhI76fz8NxY86Rj8Q2caxPCbwMBCv+7x3hDMYJ+gAtL5u/YfhHyuaUacSHA6TBmD9OBwtrnSS+GcLj3R1vpxcWx9bgg2F9S0rFQQcyn0DFqLjqE1qJJ0ZtiB5wFxgGTHmd6/1ApvNOvWTGxTIWOXVthYBkjThvlFOIjEGkZrmpPgAfuDOK0I4brdxt2veZDmVcmwi43ta2xivYSr5wapL4C8VN7Z9sC3CTq0Tqe01E3U9lz19DwFL32T/mnKiagbVOG2q4ZrOnYb2R3NKzewzbOr6QnhDB+pmwrP0kzfDmpK9n0wVe4vkuVg0QmWoq1i7WxX6yR6uihLyncvdjv0CgYEA+fyeD9J4kWUFblZQaiq7kRP6eVPDhDYG36dKktbCZxxEAAED1HF0XGekAXwbRNQS39MAbE8YKLs5pXGNpKkfWQ0c0EE4pVds96flSHzM7wtw8fhmadMS1FSaS/p9epPuF8LW5FZ7l3AUaNTjCHGF1ulvky2xo5JeLnf7DbQ+ZKUCgYEAxXOvwEjfydXIUlji2hVykyuZbFybCc3I5i62VTU2s35rl1F1fF6qUZcJwAnrNN835tayUhJym7PuGxO5g9fVNCcyrlaMxXrqjdanhY7fT8KH3fRxAhXezIMXLVgxftexeivkafSwJlNONa77n44XkE9yY61l8C4bLeezPntlW3sCgYAnt0a1ZM7a6p3ORdBIzbk292GX3QL3Ak5dQgrLAWupTghPp9mf6tZ9x8l6oukCKl9FSBSNIJPKBNTHwB6sxmHAmCC3xWTmf9lED1ySA6HbaIntJ3W94lbffQF2iLlevBnblIznggXorVnQveHD+aU126hqTZwnTJ3B7DXqm3Q+MQKBgAVodMDcfhymGVWAD76PZdL4F7yrEKgFFeKQFvhge74Q0VuUpJYidaHEdETpQKLzFjHhYYLz9GWlWPku4h7lU3aZOD8kKbji8/eskGwNDLq/hj8jCdFXzgFl+cWJK9ngiIDjIN9yDz0NfQ/lWgj1uFmAg46NWkRozt/D/9nPQWhvAoGBALGXrAPKfultEDT5vnJ3dkCmJh/z53kC/+dDxu2Ou67H+xbY6EUMHoqhFrZ5vobZqzmkQ+YFLSQmZe6VbS9KsO+UucvGMPzH5AGTh+JVyj5/TZ10QP77F4pw1eqqeSro8KirSDdaMG4jmpFo7Nj25tWLf4blKfRXgiKqlR+7iE1m
e7e4c4cd-1bd3-4021-9ec9-63849e3a87d7	9c4d8ab8-cf78-4dca-955d-72b8a42c5b6d	keyUse	ENC
ed006fda-b47d-4224-9cae-6ad54b2bd01d	30906581-3857-437a-a7bd-e427d886322e	allow-default-scopes	true
ae7fa4b5-cca0-4dfb-a60e-a8678c0e7e9c	a6ab499b-5931-4b4d-9635-05e1f60e3020	host-sending-registration-request-must-match	true
6659a0db-1673-411b-9edf-9bf2440a972d	a6ab499b-5931-4b4d-9635-05e1f60e3020	client-uris-must-match	true
fed14eca-dada-40b6-8acb-16a7fd45704d	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	saml-user-property-mapper
ed713872-0b38-44f1-b90d-fa5eebd72db6	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	oidc-full-name-mapper
3e249b1e-78f8-4176-9cf4-61bf63f300d5	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
47e651e6-632f-4618-9e65-e58fdf58f387	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
a9e83195-b61c-434a-8958-0fc040e3f710	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	saml-role-list-mapper
de4b9380-9f8e-4897-b2a1-6fce5f920a8a	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	saml-user-attribute-mapper
7a5b6d23-7d68-4d2a-9780-14ec062ed84f	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
fbf57efb-cc34-466e-b90a-ae19a094bda6	663da0ca-2ffc-4f05-a10a-92fca2d5801c	allowed-protocol-mapper-types	oidc-address-mapper
fa6e905e-6839-4d39-8f53-7fdb7d240cb4	70cc69a8-713d-4bef-8bed-d2507d0d732f	max-clients	200
ef075f24-9d0b-400e-a291-5f9a374ae24c	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	oidc-usermodel-attribute-mapper
7d4afe4e-b3a5-4bd5-8989-584112d241dc	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	oidc-usermodel-property-mapper
d70eed25-2e4c-432e-8b57-2ad4a13f57fc	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	saml-role-list-mapper
5dbafe58-b0cc-40d2-83e4-a10ea04e497d	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	oidc-address-mapper
bb2a3d5e-863b-404f-8314-9757c0127119	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	saml-user-attribute-mapper
17d4d507-3577-44d7-83d3-d77911e57826	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	oidc-full-name-mapper
8823fcd1-843f-4117-8cd2-9c8145605d31	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	saml-user-property-mapper
84ecea59-c524-4e01-ad29-5549f372f54e	d4c6e865-1618-4ae8-b3bf-3c88e2bbed18	allowed-protocol-mapper-types	oidc-sha256-pairwise-sub-mapper
6a938c7f-25b6-4100-bb0e-5997053268f5	10389cd5-0d51-4f36-bbc9-430364552af2	allow-default-scopes	true
a67a56d8-6448-494c-8800-dcf57b68f261	f7e93b87-32a8-4ebc-b8fc-912d402a9436	kc.user.profile.config	{"attributes":[{"name":"username","displayName":"${username}","validations":{"username-prohibited-characters":{},"up-username-not-idn-homograph":{},"length":{"min":"3","max":"50"}},"annotations":{},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false},{"name":"email","displayName":"${email}","validations":{"email":{},"length":{"max":255}},"required":{"roles":["user"]},"permissions":{"view":["admin","user"],"edit":["admin","user"]},"multivalued":false}],"groups":[{"name":"user-metadata","displayHeader":"User metadata","displayDescription":"Attributes, which refer to user metadata"}]}
\.


--
-- Data for Name: composite_role; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.composite_role (composite, child_role) FROM stdin;
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	427cf14a-20c3-4677-bc14-66ae3ab4b7ef
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	ba9641b7-1284-4d3f-967f-5a3c907d059b
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	15a45b51-74fd-4769-afed-e70c6c217964
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	0c60bbad-957f-4347-8723-bfe69ce4ccdd
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	dd7ac4c9-3f74-42e5-95ef-0a83977578cf
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	c4a1283e-e170-44b3-bd1e-eeb5365b3bbd
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	c38f62ea-0985-457a-bc02-f0679ac4cdce
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	7d1d053e-0477-46fa-9300-09c0792d384d
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	174f3124-b0c6-4d41-884c-6128651028dd
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	e327373d-49f1-451c-8424-c48fc567b438
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	bdef878f-76fe-4c3f-a76c-d77e61b01d29
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	e6d78f65-1098-478c-a611-f23e5bb58a01
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	d63858d6-f962-433d-b3b1-ce24ef8fc707
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	a8dfd3e6-c4b4-4035-8361-864bc23869ba
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	38b6a046-483c-4859-844d-b517d47f5760
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	6b348828-05d4-41c3-a22a-aad668e5f602
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	023d628d-fac0-4ea8-8113-126aa95e421c
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	99fb241b-b784-448c-b22d-8e9bd3147275
0c60bbad-957f-4347-8723-bfe69ce4ccdd	99fb241b-b784-448c-b22d-8e9bd3147275
0c60bbad-957f-4347-8723-bfe69ce4ccdd	38b6a046-483c-4859-844d-b517d47f5760
b4450810-c34f-4a44-8e5c-dd185fdbef3a	8915e9c0-bd83-4bca-bf1b-b1c1a4541230
dd7ac4c9-3f74-42e5-95ef-0a83977578cf	6b348828-05d4-41c3-a22a-aad668e5f602
b4450810-c34f-4a44-8e5c-dd185fdbef3a	057fcb24-70d4-43df-8c5f-6d26d91a0b77
057fcb24-70d4-43df-8c5f-6d26d91a0b77	5a3a984b-603d-4d38-8a5b-26dd99741850
71a0d1cd-c06b-4368-97cb-c680f8905d7f	df377c6a-6cc5-4f50-b9e6-ec61ae76a0f9
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	44e2329b-36d5-4aa9-8418-e51a942a8012
b4450810-c34f-4a44-8e5c-dd185fdbef3a	973da7a0-958d-44bf-9eb4-434cbb674f8d
b4450810-c34f-4a44-8e5c-dd185fdbef3a	1331af7f-96ee-4be6-8327-174d11a76462
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	c3e11b21-9738-4a36-bfc6-fceb29a9ed38
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	a782e775-7916-4809-b19c-b11eeecf9abe
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	1821e665-8e49-4022-ba20-a02b63b52d8c
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	d899df67-7201-46b5-8a84-e7beee8d516c
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	ea87aef2-2c8b-4ef0-856e-15ebd184d07a
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	8367301d-d8f6-4147-98f6-be21fc338de5
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	3989b164-aae5-4fe2-8ba4-e3b47f274d93
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	53aeedf4-9e15-47b2-b3fa-baa1953702ae
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	d2d79a5f-6693-4080-ba4a-893972e23a10
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	2415a4ce-cd09-4edd-bc77-a87815f7c647
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	2b1e8855-c23c-4c80-8fba-5b41ceae5748
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	601df922-dfd9-4a1f-996c-a353b5f0b25c
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	a5951dd5-a5d1-49a3-9e18-3609d496cd13
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	e7ef5559-f74c-45a4-a327-7e56b190c00e
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	2092d9c7-6da7-4d09-8c6c-78e63e536578
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	bf241197-8577-4608-87ba-b92778ac17d9
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	036bfab2-b22f-4e71-8364-3a5c495f88ab
1821e665-8e49-4022-ba20-a02b63b52d8c	036bfab2-b22f-4e71-8364-3a5c495f88ab
1821e665-8e49-4022-ba20-a02b63b52d8c	e7ef5559-f74c-45a4-a327-7e56b190c00e
d899df67-7201-46b5-8a84-e7beee8d516c	2092d9c7-6da7-4d09-8c6c-78e63e536578
777c64ef-50fc-4156-adc6-b99383506db9	e2e8e8f2-2a3e-480c-ac58-8ebd51f8af57
777c64ef-50fc-4156-adc6-b99383506db9	cb268d6b-b701-4927-a530-f89cbbf47215
777c64ef-50fc-4156-adc6-b99383506db9	e1c9a6b8-d11f-4436-be68-365bdfdd957b
777c64ef-50fc-4156-adc6-b99383506db9	27f5d82d-3dab-4d7a-ab08-d8ed85c30824
777c64ef-50fc-4156-adc6-b99383506db9	41ebacff-73be-4670-ae85-78ced8b6afd8
777c64ef-50fc-4156-adc6-b99383506db9	4c2bf928-da58-49d5-90a6-58474666cb08
777c64ef-50fc-4156-adc6-b99383506db9	5563c20d-400a-4cc3-a45d-ce27f195dd30
777c64ef-50fc-4156-adc6-b99383506db9	49adb33d-1e98-4a3f-9b6a-d5b257a5daa7
777c64ef-50fc-4156-adc6-b99383506db9	058b3d84-3c8c-4fa3-b61c-f571cb56e4b7
777c64ef-50fc-4156-adc6-b99383506db9	04ab9a03-661b-4c41-bd1c-5cced6df7500
777c64ef-50fc-4156-adc6-b99383506db9	6961e028-828b-49ea-891e-c6e9f75a0297
777c64ef-50fc-4156-adc6-b99383506db9	8bdfab18-5e8c-4b68-9339-d320096bdd56
777c64ef-50fc-4156-adc6-b99383506db9	4dbdfe9b-3425-4ed8-a4f4-96b0fb9289bc
777c64ef-50fc-4156-adc6-b99383506db9	ca2e1570-3934-4aff-9a97-d1c48a923a61
777c64ef-50fc-4156-adc6-b99383506db9	0de47d04-74c1-48c6-a85a-19ccce0f1a6a
777c64ef-50fc-4156-adc6-b99383506db9	ba74d9fe-3f82-4f80-a873-42abf8a40744
777c64ef-50fc-4156-adc6-b99383506db9	aad16b27-5c6a-4247-bdbd-1100d1fface4
27f5d82d-3dab-4d7a-ab08-d8ed85c30824	0de47d04-74c1-48c6-a85a-19ccce0f1a6a
a6fb666e-17a0-4cf9-95c2-820ed013c95b	117ab336-0aa0-4fdb-8db2-15c0b67d3bbc
e1c9a6b8-d11f-4436-be68-365bdfdd957b	ca2e1570-3934-4aff-9a97-d1c48a923a61
e1c9a6b8-d11f-4436-be68-365bdfdd957b	aad16b27-5c6a-4247-bdbd-1100d1fface4
a6fb666e-17a0-4cf9-95c2-820ed013c95b	27e136f9-a685-4177-b79e-807e18b2492f
27e136f9-a685-4177-b79e-807e18b2492f	a3f03a99-f589-4913-b158-8a801467bafb
6dcaff71-88ae-4bbc-8bd9-5cf176441193	ec604650-af44-4bd8-a32c-339d6763730c
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	385b53da-c3ee-4547-ae25-46c6e8164ba9
777c64ef-50fc-4156-adc6-b99383506db9	95ca83ff-244f-4a20-922f-d095d9a88c59
a6fb666e-17a0-4cf9-95c2-820ed013c95b	6c041705-4c82-43a4-b844-5cd1b40ce642
a6fb666e-17a0-4cf9-95c2-820ed013c95b	ac5788ea-c550-4a03-acdb-21993c60ee2d
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	2357d745-9305-48cf-ac68-a18454b2631d
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	e9e29590-cf74-4652-bb95-304bdb502090
777c64ef-50fc-4156-adc6-b99383506db9	6a297c21-af87-43ec-8a28-86f9215439aa
\.


--
-- Data for Name: credential; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.credential (id, salt, type, user_id, created_date, user_label, secret_data, credential_data, priority) FROM stdin;
f36a4038-1bcc-4985-a1d8-4e85ed52e0a7	\N	password	021c2681-cf67-48bf-905d-c9f04db47c15	1770584539950	\N	{"value":"fvEInscw1uZVNUU8RrPlILSrxwG46V/83QMcwRNPDj0=","salt":"39PtvVeDB7IMIYE3a9Lu6w==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
1db52933-0dae-41d6-b2e6-f9ce7fad84ad	\N	password	db8b7221-7ad2-4daa-80a1-663fdc3a5049	1771244703691	\N	{"value":"Rqr3RD2CPimFphI2AP++JQh0ME9pGYe3Q2jVP44Jh3Q=","salt":"e9NZGS3P3BBQxNishlHVtw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
2ae06a1e-7f3c-4dad-9688-e82c109136b7	\N	password	13b381de-f825-4f42-8075-1cb5fc968420	1771248430430	\N	{"value":"Y92pLeeN9jjlwkxddAOpKkFlGbCE13ZJlwifto+R7l4=","salt":"KVRpicqK+aGW5+EtA+kgEQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
80641ea4-efee-43f7-8ba0-bbaa27cc3f80	\N	password	2f63ed80-ccf2-441b-a133-039c8e23451c	1771252255948	\N	{"value":"hIrOXIA1rctGahuOZwg9xV8JdAQcSGpm+GDRp0nFhIk=","salt":"UnxoMi7PnB+f20aChJHWPA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
85f3f848-4b2d-4e12-b1ba-c261e8bc42bc	\N	password	f3501123-3a28-4069-91f9-c5cd37cae847	1771256101674	\N	{"value":"8p8TxD5AD+08aojXvhnsZl0V4m7BSOqbnbIAUV6CR5g=","salt":"tk39Z7VXZTE4eylW7ZMdEw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
d9295dc8-ef9e-47bc-a544-1e27dd98cd3c	\N	password	c49a2488-fec3-41a4-b045-64523f61a72c	1771312897609	\N	{"value":"fHHJY9rB1sEMtKbNOOWIv9QJ9hKeK9JTMZD98qlEy5g=","salt":"mi5pyRjVXiCULTONaT0A1Q==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
8c9c4681-2687-4720-96c2-3e8077843158	\N	password	622a15dd-1b68-4359-9b83-749167855ddf	1771322378767	\N	{"value":"/tuZhIEgtr9dDVpRNGABSSxBgvYnbYAwctI5AFy2zmQ=","salt":"kYxxYMhJC44cdwsaMzLVtQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
01681f42-f9af-459c-96e9-defb5bef4f55	\N	password	c4ddb6a8-262f-4fac-a56b-cc9aec5395d1	1771322547549	\N	{"value":"qIqzT470bOU+sQo8gNv1S2aFxOxiEYL+B8P+TtbO1t0=","salt":"ma/c/4F+rtNbd7TPEix9tQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
818405d9-d520-4bb0-b257-f5f69885b809	\N	password	a0216fcd-713f-4ede-aa6e-0c9a183bf5fc	1771325323029	\N	{"value":"jayFRJ1xgLLSWLeQ1aekSEOIHuIjG7phpZ/jmsJsWuw=","salt":"H23fyn5WYZGhYRQPguVdYw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
de27376b-2d57-471d-ad36-86a7109c0adb	\N	password	16aa7fe9-754b-44f4-bc6e-dd9ad46ac548	1771326123359	\N	{"value":"bLCV8flHX7xDnzweLKZh8EdEyIc7uDAYDNStJKfPX2s=","salt":"ivfpQIAinYv88/XMODmuCA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
f3f0c577-f47b-4c70-88b5-555fbcbb9e82	\N	password	87d8e1bf-4026-4e60-ae30-a7e17a8e97a8	1771400815048	\N	{"value":"RfHlvyLqS+O4jVvw3DJ1b12d1gPa3p/M0o/UpQgyR8Q=","salt":"yY0/c6KQdIIyIC77i/mVRA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
8f22707a-cbd5-4dd3-9cea-5e486a3e05fa	\N	password	cf0282bc-09f2-4bd2-a51b-eaae07dddb32	1771503136234	\N	{"value":"qDogW292vueHkwp6YIQgHBbdRDmZ1u1NPcPwOu7tXIM=","salt":"+YmcF0KyJ6lKOSUv2gxGPA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
339493fd-ef9d-423b-a8a6-d4365e964dc8	\N	password	f2bd8ba3-7d1b-4884-987a-53f58ffb903c	1771511120593	\N	{"value":"Bj7mTzrVHqUvY0PyTWDwP8f3I7icRGCPunXHC41g06w=","salt":"r0Dzq2wvliBQbzVplAEcKw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
d637a636-34fa-42dd-b50f-5108024772da	\N	password	70e74a1d-5e8c-4349-9f14-0272f44464f8	1771573026225	\N	{"value":"nZ/GkIp3ZTf4UjesvkbkjHybKfJcX5M6+5Fa/hu34e0=","salt":"VKf9crTVdt4vLDwuVcESAw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
9a89e198-d494-40db-ba55-1bcd78af5631	\N	password	5955cb99-825e-4510-97e1-ed7b260922f4	1771830220734	\N	{"value":"fnSuc3chJeeNBsUXYOaUw2scC7KCAAJ1iJgebG8vDi0=","salt":"REEZBOJrO6CVLpnyLiYHcw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
f7a393b2-aa9b-4984-a412-492e4281e423	\N	password	5b0c5b26-6648-4e6e-b324-be8b36ee4982	1771247513319	\N	{"value":"j4X6UtSGcMvElhK00wBrGVHPhgcFsMpDhN2ljNekxwY=","salt":"eMNX8FvVPnMBRcPpEP7s9Q==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
72c19b7f-0e60-4fae-aa10-6e3d4a209454	\N	password	a508ba28-813f-4e1a-9054-8d3296d45f68	1771253156291	\N	{"value":"Dowa4yGiUtoYxibsEQAL9PeKXoj3Fw6iyxmp9vVbpJc=","salt":"NyMLwTEn/waeS4kHy3DF7Q==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
af57081a-4f0e-48b7-b0d5-434eeee07d50	\N	password	c1b9eb69-f809-4926-90c8-74cdd61c49dd	1771253334158	\N	{"value":"MVQPd/gPNjTV6v6SSY95hrkIeke7K62W9mfuGmmyIYw=","salt":"l1hFaG52b27pJnnqSvDAhQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
96357a36-bbcb-4625-93ac-af3f51594dc1	\N	password	2bf9e0a5-4ff9-4a1c-9656-af1deaf9a360	1771253369496	\N	{"value":"bKeQyn8m4rT7DjktvAIvRgiITMljKvSsunZtqezGfs0=","salt":"Cy2gRI11lMhL+CiSLyzbBA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
67aaeb26-f4f7-4ead-8b80-913b0c846395	\N	password	f2e705f1-22bf-462d-96bd-f28e4f3e5dd4	1771253664955	\N	{"value":"1+NvyMW5imbqgfskhkiUs9rvuZzwE6l3Ql6C+mKcCXs=","salt":"B2zB8JjSuFoKBJXXWhTIpA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
6cd4cb22-5d59-48d1-8e31-cb45e554cad9	\N	password	11410dc4-aaf5-4d12-ba7e-98faa22dad4e	1771253717896	\N	{"value":"g8VGSk8f66xfYA/mexQsupa6h8eEki8a1r0mdn0nsAk=","salt":"d7b1dq6PHPn1bQnJZCW1Mw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
17eff0de-9900-403c-8434-d66b2d989085	\N	password	4cffe999-c408-47d8-b373-a135c33c584b	1771253732651	\N	{"value":"M9kcTP6XBbEInWI9h+CzOu8WYFif2SJxg2t343Emxg4=","salt":"Ueal1Uvq4YQr5t5r6NsBOA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
d139f33f-ede0-4ec5-a4db-8f37a0226e01	\N	password	9c59c419-de93-4c22-90f8-0acc8441258c	1771253818220	\N	{"value":"o07u9WqIW5V/bXeEAuxtVqmz9L65UdUhKhW+zIEi7Q0=","salt":"blyRj5Gz5QFtY7awxzAufQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
61e7272c-2c24-4c3f-9792-b129ecea171e	\N	password	0a6def52-8847-4d71-99e6-f05ea861e89f	1771255044316	\N	{"value":"385/nnYEhhDlXrT25J1Bvi+aQ+/j0mbijjddXTMDQME=","salt":"lEPIzq/UodGBphL4f+1m4Q==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
1a4c27fb-3351-4611-ba1c-4070d3e3a316	\N	password	54fa4a2f-1a44-4839-afb9-273cbb76b6c5	1771255093232	\N	{"value":"3IUVbZAzjNQg+YtAil9PaDgpqAuf7Q6vp75d9TPBBs4=","salt":"RTlvhW9nXsyhVE8qAfr4cA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
65905193-0669-4748-99a9-0d5445d3dcf8	\N	password	6dc077ea-1aed-45a3-864f-d9e9192ab3b4	1771318788588	\N	{"value":"dDKDE0LthSm7/kuWNk5HCSCjdNLm0ULm3xV7G3lYOI4=","salt":"EKIWBavsO8F9pmGOc9Lg9w==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
3374186f-7005-49a0-9dac-4145982d40a5	\N	password	93655b56-7b7a-4ba3-8839-1ad920809cf2	1771336148351	\N	{"value":"U6c/9jPz0Hce1hs7Oe1SDGykGNoq1Mjbxrhuj5RH7fk=","salt":"4BXFPBfU2XW7UeV4B8b5NA==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
974d3772-a303-4a23-b089-db39df23a435	\N	password	0ac233ac-ec8e-4a37-9183-af309a5bbc2c	1771336424750	\N	{"value":"b4vJRXesW1olV2VyC0bm/+oYK3j0A19klahD1TWQtZ8=","salt":"6JZuXD5gyOyjUVJogPgxjQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
f6f15e3c-257d-4b30-9fc7-a3e0285075c7	\N	password	bf32ef13-193f-4cb4-8f94-1d8944e92036	1771509811816	\N	{"value":"NdCNdPqARe9U/mxSM6IaxdLWUxUE4bTlEyQm3Nkr1YY=","salt":"aBgHWmxx4t/2nk8kXUDnKQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
260a3916-616e-491b-9585-5fc2ee06f4a9	\N	password	82717555-0804-479f-b099-1e797e52ef26	1770973890112	\N	{"value":"M1/c4YI38RBJJOmrKk1dKHHNCLz6u/EHYC0+tQN+Nxg=","salt":"aO82290DOnbLOMcNh5hAXg==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
09d7b29d-52f0-48bc-a192-2aa0804eb144	\N	password	9512c9ac-fb14-44b3-a6bb-80fde34f6f9d	1771229664073	\N	{"value":"YqlJCGHK7tuSEi5/BndtEpNXvfe/GpaXcsh3qAocKGA=","salt":"fVEsP9CqK4m4HCKtpYKzeg==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
56490ddd-e720-4807-8fe1-7a10e33ddbb5	\N	password	0cc2b18a-72d2-4c3a-b073-8608ac0a4d3d	1771233442417	\N	{"value":"UEYmPij9bKD5x9eauHivRsEUSmuEBjZaZz4NECx7QCM=","salt":"Bj2YgL7SGbB7lOdpKHsCJw==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
4ba5b766-0277-445d-9971-cb2a720ca430	\N	password	040af51b-8763-4bef-933d-15ede5142995	1771234231362	\N	{"value":"NR03rBBQQpxqNYpHjIdMUDcQ3btiJcOrIHUMylzcBLI=","salt":"KiIOEEPPrXCADLUMZUE6nQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
b4dba0cc-d48d-495b-844d-fdca05204327	\N	password	5fe53f87-d1cf-4673-8a1f-561b8f31c740	1771234334350	\N	{"value":"4CZMc8hMkWX7ZhBOqe/c8g+yZie2JWyxXp9KKwKgUmQ=","salt":"jBPd8Zqhfj0TgssfAXhxOQ==","additionalParameters":{}}	{"hashIterations":5,"algorithm":"argon2","additionalParameters":{"hashLength":["32"],"memory":["7168"],"type":["id"],"version":["1.3"],"parallelism":["1"]}}	10
\.


--
-- Data for Name: databasechangelog; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.databasechangelog (id, author, filename, dateexecuted, orderexecuted, exectype, md5sum, description, comments, tag, liquibase, contexts, labels, deployment_id) FROM stdin;
1.0.0.Final-KEYCLOAK-5461	sthorger@redhat.com	META-INF/jpa-changelog-1.0.0.Final.xml	2026-02-08 21:02:06.529048	1	EXECUTED	9:6f1016664e21e16d26517a4418f5e3df	createTable tableName=APPLICATION_DEFAULT_ROLES; createTable tableName=CLIENT; createTable tableName=CLIENT_SESSION; createTable tableName=CLIENT_SESSION_ROLE; createTable tableName=COMPOSITE_ROLE; createTable tableName=CREDENTIAL; createTable tab...		\N	4.29.1	\N	\N	0584525751
1.0.0.Final-KEYCLOAK-5461	sthorger@redhat.com	META-INF/db2-jpa-changelog-1.0.0.Final.xml	2026-02-08 21:02:06.553671	2	MARK_RAN	9:828775b1596a07d1200ba1d49e5e3941	createTable tableName=APPLICATION_DEFAULT_ROLES; createTable tableName=CLIENT; createTable tableName=CLIENT_SESSION; createTable tableName=CLIENT_SESSION_ROLE; createTable tableName=COMPOSITE_ROLE; createTable tableName=CREDENTIAL; createTable tab...		\N	4.29.1	\N	\N	0584525751
1.1.0.Beta1	sthorger@redhat.com	META-INF/jpa-changelog-1.1.0.Beta1.xml	2026-02-08 21:02:06.637603	3	EXECUTED	9:5f090e44a7d595883c1fb61f4b41fd38	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION; createTable tableName=CLIENT_ATTRIBUTES; createTable tableName=CLIENT_SESSION_NOTE; createTable tableName=APP_NODE_REGISTRATIONS; addColumn table...		\N	4.29.1	\N	\N	0584525751
1.1.0.Final	sthorger@redhat.com	META-INF/jpa-changelog-1.1.0.Final.xml	2026-02-08 21:02:06.645776	4	EXECUTED	9:c07e577387a3d2c04d1adc9aaad8730e	renameColumn newColumnName=EVENT_TIME, oldColumnName=TIME, tableName=EVENT_ENTITY		\N	4.29.1	\N	\N	0584525751
1.2.0.Beta1	psilva@redhat.com	META-INF/jpa-changelog-1.2.0.Beta1.xml	2026-02-08 21:02:06.849945	5	EXECUTED	9:b68ce996c655922dbcd2fe6b6ae72686	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION; createTable tableName=PROTOCOL_MAPPER; createTable tableName=PROTOCOL_MAPPER_CONFIG; createTable tableName=...		\N	4.29.1	\N	\N	0584525751
1.2.0.Beta1	psilva@redhat.com	META-INF/db2-jpa-changelog-1.2.0.Beta1.xml	2026-02-08 21:02:06.861963	6	MARK_RAN	9:543b5c9989f024fe35c6f6c5a97de88e	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION; createTable tableName=PROTOCOL_MAPPER; createTable tableName=PROTOCOL_MAPPER_CONFIG; createTable tableName=...		\N	4.29.1	\N	\N	0584525751
1.2.0.RC1	bburke@redhat.com	META-INF/jpa-changelog-1.2.0.CR1.xml	2026-02-08 21:02:07.077979	7	EXECUTED	9:765afebbe21cf5bbca048e632df38336	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete tableName=USER_SESSION; createTable tableName=MIGRATION_MODEL; createTable tableName=IDENTITY_P...		\N	4.29.1	\N	\N	0584525751
1.2.0.RC1	bburke@redhat.com	META-INF/db2-jpa-changelog-1.2.0.CR1.xml	2026-02-08 21:02:07.100847	8	MARK_RAN	9:db4a145ba11a6fdaefb397f6dbf829a1	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete tableName=USER_SESSION; createTable tableName=MIGRATION_MODEL; createTable tableName=IDENTITY_P...		\N	4.29.1	\N	\N	0584525751
1.2.0.Final	keycloak	META-INF/jpa-changelog-1.2.0.Final.xml	2026-02-08 21:02:07.129573	9	EXECUTED	9:9d05c7be10cdb873f8bcb41bc3a8ab23	update tableName=CLIENT; update tableName=CLIENT; update tableName=CLIENT		\N	4.29.1	\N	\N	0584525751
1.3.0	bburke@redhat.com	META-INF/jpa-changelog-1.3.0.xml	2026-02-08 21:02:07.529036	10	EXECUTED	9:18593702353128d53111f9b1ff0b82b8	delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete tableName=USER_SESSION; createTable tableName=ADMI...		\N	4.29.1	\N	\N	0584525751
1.4.0	bburke@redhat.com	META-INF/jpa-changelog-1.4.0.xml	2026-02-08 21:02:07.677738	11	EXECUTED	9:6122efe5f090e41a85c0f1c9e52cbb62	delete tableName=CLIENT_SESSION_AUTH_STATUS; delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete table...		\N	4.29.1	\N	\N	0584525751
1.4.0	bburke@redhat.com	META-INF/db2-jpa-changelog-1.4.0.xml	2026-02-08 21:02:07.687117	12	MARK_RAN	9:e1ff28bf7568451453f844c5d54bb0b5	delete tableName=CLIENT_SESSION_AUTH_STATUS; delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete table...		\N	4.29.1	\N	\N	0584525751
1.5.0	bburke@redhat.com	META-INF/jpa-changelog-1.5.0.xml	2026-02-08 21:02:07.732718	13	EXECUTED	9:7af32cd8957fbc069f796b61217483fd	delete tableName=CLIENT_SESSION_AUTH_STATUS; delete tableName=CLIENT_SESSION_ROLE; delete tableName=CLIENT_SESSION_PROT_MAPPER; delete tableName=CLIENT_SESSION_NOTE; delete tableName=CLIENT_SESSION; delete tableName=USER_SESSION_NOTE; delete table...		\N	4.29.1	\N	\N	0584525751
1.6.1_from15	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-02-08 21:02:07.769826	14	EXECUTED	9:6005e15e84714cd83226bf7879f54190	addColumn tableName=REALM; addColumn tableName=KEYCLOAK_ROLE; addColumn tableName=CLIENT; createTable tableName=OFFLINE_USER_SESSION; createTable tableName=OFFLINE_CLIENT_SESSION; addPrimaryKey constraintName=CONSTRAINT_OFFL_US_SES_PK2, tableName=...		\N	4.29.1	\N	\N	0584525751
1.6.1_from16-pre	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-02-08 21:02:07.772606	15	MARK_RAN	9:bf656f5a2b055d07f314431cae76f06c	delete tableName=OFFLINE_CLIENT_SESSION; delete tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
1.6.1_from16	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-02-08 21:02:07.776879	16	MARK_RAN	9:f8dadc9284440469dcf71e25ca6ab99b	dropPrimaryKey constraintName=CONSTRAINT_OFFLINE_US_SES_PK, tableName=OFFLINE_USER_SESSION; dropPrimaryKey constraintName=CONSTRAINT_OFFLINE_CL_SES_PK, tableName=OFFLINE_CLIENT_SESSION; addColumn tableName=OFFLINE_USER_SESSION; update tableName=OF...		\N	4.29.1	\N	\N	0584525751
1.6.1	mposolda@redhat.com	META-INF/jpa-changelog-1.6.1.xml	2026-02-08 21:02:07.782418	17	EXECUTED	9:d41d8cd98f00b204e9800998ecf8427e	empty		\N	4.29.1	\N	\N	0584525751
1.7.0	bburke@redhat.com	META-INF/jpa-changelog-1.7.0.xml	2026-02-08 21:02:07.928963	18	EXECUTED	9:3368ff0be4c2855ee2dd9ca813b38d8e	createTable tableName=KEYCLOAK_GROUP; createTable tableName=GROUP_ROLE_MAPPING; createTable tableName=GROUP_ATTRIBUTE; createTable tableName=USER_GROUP_MEMBERSHIP; createTable tableName=REALM_DEFAULT_GROUPS; addColumn tableName=IDENTITY_PROVIDER; ...		\N	4.29.1	\N	\N	0584525751
1.8.0	mposolda@redhat.com	META-INF/jpa-changelog-1.8.0.xml	2026-02-08 21:02:08.020309	19	EXECUTED	9:8ac2fb5dd030b24c0570a763ed75ed20	addColumn tableName=IDENTITY_PROVIDER; createTable tableName=CLIENT_TEMPLATE; createTable tableName=CLIENT_TEMPLATE_ATTRIBUTES; createTable tableName=TEMPLATE_SCOPE_MAPPING; dropNotNullConstraint columnName=CLIENT_ID, tableName=PROTOCOL_MAPPER; ad...		\N	4.29.1	\N	\N	0584525751
1.8.0-2	keycloak	META-INF/jpa-changelog-1.8.0.xml	2026-02-08 21:02:08.028007	20	EXECUTED	9:f91ddca9b19743db60e3057679810e6c	dropDefaultValue columnName=ALGORITHM, tableName=CREDENTIAL; update tableName=CREDENTIAL		\N	4.29.1	\N	\N	0584525751
1.8.0	mposolda@redhat.com	META-INF/db2-jpa-changelog-1.8.0.xml	2026-02-08 21:02:08.032656	21	MARK_RAN	9:831e82914316dc8a57dc09d755f23c51	addColumn tableName=IDENTITY_PROVIDER; createTable tableName=CLIENT_TEMPLATE; createTable tableName=CLIENT_TEMPLATE_ATTRIBUTES; createTable tableName=TEMPLATE_SCOPE_MAPPING; dropNotNullConstraint columnName=CLIENT_ID, tableName=PROTOCOL_MAPPER; ad...		\N	4.29.1	\N	\N	0584525751
1.8.0-2	keycloak	META-INF/db2-jpa-changelog-1.8.0.xml	2026-02-08 21:02:08.037121	22	MARK_RAN	9:f91ddca9b19743db60e3057679810e6c	dropDefaultValue columnName=ALGORITHM, tableName=CREDENTIAL; update tableName=CREDENTIAL		\N	4.29.1	\N	\N	0584525751
1.9.0	mposolda@redhat.com	META-INF/jpa-changelog-1.9.0.xml	2026-02-08 21:02:08.165881	23	EXECUTED	9:bc3d0f9e823a69dc21e23e94c7a94bb1	update tableName=REALM; update tableName=REALM; update tableName=REALM; update tableName=REALM; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=REALM; update tableName=REALM; customChange; dr...		\N	4.29.1	\N	\N	0584525751
1.9.1	keycloak	META-INF/jpa-changelog-1.9.1.xml	2026-02-08 21:02:08.175579	24	EXECUTED	9:c9999da42f543575ab790e76439a2679	modifyDataType columnName=PRIVATE_KEY, tableName=REALM; modifyDataType columnName=PUBLIC_KEY, tableName=REALM; modifyDataType columnName=CERTIFICATE, tableName=REALM		\N	4.29.1	\N	\N	0584525751
1.9.1	keycloak	META-INF/db2-jpa-changelog-1.9.1.xml	2026-02-08 21:02:08.178234	25	MARK_RAN	9:0d6c65c6f58732d81569e77b10ba301d	modifyDataType columnName=PRIVATE_KEY, tableName=REALM; modifyDataType columnName=CERTIFICATE, tableName=REALM		\N	4.29.1	\N	\N	0584525751
1.9.2	keycloak	META-INF/jpa-changelog-1.9.2.xml	2026-02-08 21:02:08.815757	26	EXECUTED	9:fc576660fc016ae53d2d4778d84d86d0	createIndex indexName=IDX_USER_EMAIL, tableName=USER_ENTITY; createIndex indexName=IDX_USER_ROLE_MAPPING, tableName=USER_ROLE_MAPPING; createIndex indexName=IDX_USER_GROUP_MAPPING, tableName=USER_GROUP_MEMBERSHIP; createIndex indexName=IDX_USER_CO...		\N	4.29.1	\N	\N	0584525751
authz-2.0.0	psilva@redhat.com	META-INF/jpa-changelog-authz-2.0.0.xml	2026-02-08 21:02:08.941911	27	EXECUTED	9:43ed6b0da89ff77206289e87eaa9c024	createTable tableName=RESOURCE_SERVER; addPrimaryKey constraintName=CONSTRAINT_FARS, tableName=RESOURCE_SERVER; addUniqueConstraint constraintName=UK_AU8TT6T700S9V50BU18WS5HA6, tableName=RESOURCE_SERVER; createTable tableName=RESOURCE_SERVER_RESOU...		\N	4.29.1	\N	\N	0584525751
authz-2.5.1	psilva@redhat.com	META-INF/jpa-changelog-authz-2.5.1.xml	2026-02-08 21:02:08.947896	28	EXECUTED	9:44bae577f551b3738740281eceb4ea70	update tableName=RESOURCE_SERVER_POLICY		\N	4.29.1	\N	\N	0584525751
2.1.0-KEYCLOAK-5461	bburke@redhat.com	META-INF/jpa-changelog-2.1.0.xml	2026-02-08 21:02:09.064748	29	EXECUTED	9:bd88e1f833df0420b01e114533aee5e8	createTable tableName=BROKER_LINK; createTable tableName=FED_USER_ATTRIBUTE; createTable tableName=FED_USER_CONSENT; createTable tableName=FED_USER_CONSENT_ROLE; createTable tableName=FED_USER_CONSENT_PROT_MAPPER; createTable tableName=FED_USER_CR...		\N	4.29.1	\N	\N	0584525751
2.2.0	bburke@redhat.com	META-INF/jpa-changelog-2.2.0.xml	2026-02-08 21:02:09.090745	30	EXECUTED	9:a7022af5267f019d020edfe316ef4371	addColumn tableName=ADMIN_EVENT_ENTITY; createTable tableName=CREDENTIAL_ATTRIBUTE; createTable tableName=FED_CREDENTIAL_ATTRIBUTE; modifyDataType columnName=VALUE, tableName=CREDENTIAL; addForeignKeyConstraint baseTableName=FED_CREDENTIAL_ATTRIBU...		\N	4.29.1	\N	\N	0584525751
2.3.0	bburke@redhat.com	META-INF/jpa-changelog-2.3.0.xml	2026-02-08 21:02:09.137595	31	EXECUTED	9:fc155c394040654d6a79227e56f5e25a	createTable tableName=FEDERATED_USER; addPrimaryKey constraintName=CONSTR_FEDERATED_USER, tableName=FEDERATED_USER; dropDefaultValue columnName=TOTP, tableName=USER_ENTITY; dropColumn columnName=TOTP, tableName=USER_ENTITY; addColumn tableName=IDE...		\N	4.29.1	\N	\N	0584525751
2.4.0	bburke@redhat.com	META-INF/jpa-changelog-2.4.0.xml	2026-02-08 21:02:09.151753	32	EXECUTED	9:eac4ffb2a14795e5dc7b426063e54d88	customChange		\N	4.29.1	\N	\N	0584525751
2.5.0	bburke@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-02-08 21:02:09.166177	33	EXECUTED	9:54937c05672568c4c64fc9524c1e9462	customChange; modifyDataType columnName=USER_ID, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
2.5.0-unicode-oracle	hmlnarik@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-02-08 21:02:09.172242	34	MARK_RAN	9:3a32bace77c84d7678d035a7f5a8084e	modifyDataType columnName=DESCRIPTION, tableName=AUTHENTICATION_FLOW; modifyDataType columnName=DESCRIPTION, tableName=CLIENT_TEMPLATE; modifyDataType columnName=DESCRIPTION, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=DESCRIPTION,...		\N	4.29.1	\N	\N	0584525751
2.5.0-unicode-other-dbs	hmlnarik@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-02-08 21:02:09.25527	35	EXECUTED	9:33d72168746f81f98ae3a1e8e0ca3554	modifyDataType columnName=DESCRIPTION, tableName=AUTHENTICATION_FLOW; modifyDataType columnName=DESCRIPTION, tableName=CLIENT_TEMPLATE; modifyDataType columnName=DESCRIPTION, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=DESCRIPTION,...		\N	4.29.1	\N	\N	0584525751
2.5.0-duplicate-email-support	slawomir@dabek.name	META-INF/jpa-changelog-2.5.0.xml	2026-02-08 21:02:09.267597	36	EXECUTED	9:61b6d3d7a4c0e0024b0c839da283da0c	addColumn tableName=REALM		\N	4.29.1	\N	\N	0584525751
2.5.0-unique-group-names	hmlnarik@redhat.com	META-INF/jpa-changelog-2.5.0.xml	2026-02-08 21:02:09.278419	37	EXECUTED	9:8dcac7bdf7378e7d823cdfddebf72fda	addUniqueConstraint constraintName=SIBLING_NAMES, tableName=KEYCLOAK_GROUP		\N	4.29.1	\N	\N	0584525751
2.5.1	bburke@redhat.com	META-INF/jpa-changelog-2.5.1.xml	2026-02-08 21:02:09.286042	38	EXECUTED	9:a2b870802540cb3faa72098db5388af3	addColumn tableName=FED_USER_CONSENT		\N	4.29.1	\N	\N	0584525751
3.0.0	bburke@redhat.com	META-INF/jpa-changelog-3.0.0.xml	2026-02-08 21:02:09.292301	39	EXECUTED	9:132a67499ba24bcc54fb5cbdcfe7e4c0	addColumn tableName=IDENTITY_PROVIDER		\N	4.29.1	\N	\N	0584525751
3.2.0-fix	keycloak	META-INF/jpa-changelog-3.2.0.xml	2026-02-08 21:02:09.294331	40	MARK_RAN	9:938f894c032f5430f2b0fafb1a243462	addNotNullConstraint columnName=REALM_ID, tableName=CLIENT_INITIAL_ACCESS		\N	4.29.1	\N	\N	0584525751
3.2.0-fix-with-keycloak-5416	keycloak	META-INF/jpa-changelog-3.2.0.xml	2026-02-08 21:02:09.29717	41	MARK_RAN	9:845c332ff1874dc5d35974b0babf3006	dropIndex indexName=IDX_CLIENT_INIT_ACC_REALM, tableName=CLIENT_INITIAL_ACCESS; addNotNullConstraint columnName=REALM_ID, tableName=CLIENT_INITIAL_ACCESS; createIndex indexName=IDX_CLIENT_INIT_ACC_REALM, tableName=CLIENT_INITIAL_ACCESS		\N	4.29.1	\N	\N	0584525751
3.2.0-fix-offline-sessions	hmlnarik	META-INF/jpa-changelog-3.2.0.xml	2026-02-08 21:02:09.30945	42	EXECUTED	9:fc86359c079781adc577c5a217e4d04c	customChange		\N	4.29.1	\N	\N	0584525751
3.2.0-fixed	keycloak	META-INF/jpa-changelog-3.2.0.xml	2026-02-08 21:02:11.641833	43	EXECUTED	9:59a64800e3c0d09b825f8a3b444fa8f4	addColumn tableName=REALM; dropPrimaryKey constraintName=CONSTRAINT_OFFL_CL_SES_PK2, tableName=OFFLINE_CLIENT_SESSION; dropColumn columnName=CLIENT_SESSION_ID, tableName=OFFLINE_CLIENT_SESSION; addPrimaryKey constraintName=CONSTRAINT_OFFL_CL_SES_P...		\N	4.29.1	\N	\N	0584525751
3.3.0	keycloak	META-INF/jpa-changelog-3.3.0.xml	2026-02-08 21:02:11.649226	44	EXECUTED	9:d48d6da5c6ccf667807f633fe489ce88	addColumn tableName=USER_ENTITY		\N	4.29.1	\N	\N	0584525751
authz-3.4.0.CR1-resource-server-pk-change-part1	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-02-08 21:02:11.654845	45	EXECUTED	9:dde36f7973e80d71fceee683bc5d2951	addColumn tableName=RESOURCE_SERVER_POLICY; addColumn tableName=RESOURCE_SERVER_RESOURCE; addColumn tableName=RESOURCE_SERVER_SCOPE		\N	4.29.1	\N	\N	0584525751
authz-3.4.0.CR1-resource-server-pk-change-part2-KEYCLOAK-6095	hmlnarik@redhat.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-02-08 21:02:11.660388	46	EXECUTED	9:b855e9b0a406b34fa323235a0cf4f640	customChange		\N	4.29.1	\N	\N	0584525751
authz-3.4.0.CR1-resource-server-pk-change-part3-fixed	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-02-08 21:02:11.661841	47	MARK_RAN	9:51abbacd7b416c50c4421a8cabf7927e	dropIndex indexName=IDX_RES_SERV_POL_RES_SERV, tableName=RESOURCE_SERVER_POLICY; dropIndex indexName=IDX_RES_SRV_RES_RES_SRV, tableName=RESOURCE_SERVER_RESOURCE; dropIndex indexName=IDX_RES_SRV_SCOPE_RES_SRV, tableName=RESOURCE_SERVER_SCOPE		\N	4.29.1	\N	\N	0584525751
authz-3.4.0.CR1-resource-server-pk-change-part3-fixed-nodropindex	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-02-08 21:02:11.833232	48	EXECUTED	9:bdc99e567b3398bac83263d375aad143	addNotNullConstraint columnName=RESOURCE_SERVER_CLIENT_ID, tableName=RESOURCE_SERVER_POLICY; addNotNullConstraint columnName=RESOURCE_SERVER_CLIENT_ID, tableName=RESOURCE_SERVER_RESOURCE; addNotNullConstraint columnName=RESOURCE_SERVER_CLIENT_ID, ...		\N	4.29.1	\N	\N	0584525751
authn-3.4.0.CR1-refresh-token-max-reuse	glavoie@gmail.com	META-INF/jpa-changelog-authz-3.4.0.CR1.xml	2026-02-08 21:02:11.83832	49	EXECUTED	9:d198654156881c46bfba39abd7769e69	addColumn tableName=REALM		\N	4.29.1	\N	\N	0584525751
3.4.0	keycloak	META-INF/jpa-changelog-3.4.0.xml	2026-02-08 21:02:11.911295	50	EXECUTED	9:cfdd8736332ccdd72c5256ccb42335db	addPrimaryKey constraintName=CONSTRAINT_REALM_DEFAULT_ROLES, tableName=REALM_DEFAULT_ROLES; addPrimaryKey constraintName=CONSTRAINT_COMPOSITE_ROLE, tableName=COMPOSITE_ROLE; addPrimaryKey constraintName=CONSTR_REALM_DEFAULT_GROUPS, tableName=REALM...		\N	4.29.1	\N	\N	0584525751
3.4.0-KEYCLOAK-5230	hmlnarik@redhat.com	META-INF/jpa-changelog-3.4.0.xml	2026-02-08 21:02:12.452745	51	EXECUTED	9:7c84de3d9bd84d7f077607c1a4dcb714	createIndex indexName=IDX_FU_ATTRIBUTE, tableName=FED_USER_ATTRIBUTE; createIndex indexName=IDX_FU_CONSENT, tableName=FED_USER_CONSENT; createIndex indexName=IDX_FU_CONSENT_RU, tableName=FED_USER_CONSENT; createIndex indexName=IDX_FU_CREDENTIAL, t...		\N	4.29.1	\N	\N	0584525751
3.4.1	psilva@redhat.com	META-INF/jpa-changelog-3.4.1.xml	2026-02-08 21:02:12.459193	52	EXECUTED	9:5a6bb36cbefb6a9d6928452c0852af2d	modifyDataType columnName=VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
3.4.2	keycloak	META-INF/jpa-changelog-3.4.2.xml	2026-02-08 21:02:12.464114	53	EXECUTED	9:8f23e334dbc59f82e0a328373ca6ced0	update tableName=REALM		\N	4.29.1	\N	\N	0584525751
3.4.2-KEYCLOAK-5172	mkanis@redhat.com	META-INF/jpa-changelog-3.4.2.xml	2026-02-08 21:02:12.467501	54	EXECUTED	9:9156214268f09d970cdf0e1564d866af	update tableName=CLIENT		\N	4.29.1	\N	\N	0584525751
4.0.0-KEYCLOAK-6335	bburke@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-02-08 21:02:12.475944	55	EXECUTED	9:db806613b1ed154826c02610b7dbdf74	createTable tableName=CLIENT_AUTH_FLOW_BINDINGS; addPrimaryKey constraintName=C_CLI_FLOW_BIND, tableName=CLIENT_AUTH_FLOW_BINDINGS		\N	4.29.1	\N	\N	0584525751
4.0.0-CLEANUP-UNUSED-TABLE	bburke@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-02-08 21:02:12.484371	56	EXECUTED	9:229a041fb72d5beac76bb94a5fa709de	dropTable tableName=CLIENT_IDENTITY_PROV_MAPPING		\N	4.29.1	\N	\N	0584525751
4.0.0-KEYCLOAK-6228	bburke@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-02-08 21:02:12.562396	57	EXECUTED	9:079899dade9c1e683f26b2aa9ca6ff04	dropUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHOGM8UEWRT, tableName=USER_CONSENT; dropNotNullConstraint columnName=CLIENT_ID, tableName=USER_CONSENT; addColumn tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHO...		\N	4.29.1	\N	\N	0584525751
4.0.0-KEYCLOAK-5579-fixed	mposolda@redhat.com	META-INF/jpa-changelog-4.0.0.xml	2026-02-08 21:02:13.181299	58	EXECUTED	9:139b79bcbbfe903bb1c2d2a4dbf001d9	dropForeignKeyConstraint baseTableName=CLIENT_TEMPLATE_ATTRIBUTES, constraintName=FK_CL_TEMPL_ATTR_TEMPL; renameTable newTableName=CLIENT_SCOPE_ATTRIBUTES, oldTableName=CLIENT_TEMPLATE_ATTRIBUTES; renameColumn newColumnName=SCOPE_ID, oldColumnName...		\N	4.29.1	\N	\N	0584525751
authz-4.0.0.CR1	psilva@redhat.com	META-INF/jpa-changelog-authz-4.0.0.CR1.xml	2026-02-08 21:02:13.227905	59	EXECUTED	9:b55738ad889860c625ba2bf483495a04	createTable tableName=RESOURCE_SERVER_PERM_TICKET; addPrimaryKey constraintName=CONSTRAINT_FAPMT, tableName=RESOURCE_SERVER_PERM_TICKET; addForeignKeyConstraint baseTableName=RESOURCE_SERVER_PERM_TICKET, constraintName=FK_FRSRHO213XCX4WNKOG82SSPMT...		\N	4.29.1	\N	\N	0584525751
authz-4.0.0.Beta3	psilva@redhat.com	META-INF/jpa-changelog-authz-4.0.0.Beta3.xml	2026-02-08 21:02:13.241234	60	EXECUTED	9:e0057eac39aa8fc8e09ac6cfa4ae15fe	addColumn tableName=RESOURCE_SERVER_POLICY; addColumn tableName=RESOURCE_SERVER_PERM_TICKET; addForeignKeyConstraint baseTableName=RESOURCE_SERVER_PERM_TICKET, constraintName=FK_FRSRPO2128CX4WNKOG82SSRFY, referencedTableName=RESOURCE_SERVER_POLICY		\N	4.29.1	\N	\N	0584525751
authz-4.2.0.Final	mhajas@redhat.com	META-INF/jpa-changelog-authz-4.2.0.Final.xml	2026-02-08 21:02:13.259911	61	EXECUTED	9:42a33806f3a0443fe0e7feeec821326c	createTable tableName=RESOURCE_URIS; addForeignKeyConstraint baseTableName=RESOURCE_URIS, constraintName=FK_RESOURCE_SERVER_URIS, referencedTableName=RESOURCE_SERVER_RESOURCE; customChange; dropColumn columnName=URI, tableName=RESOURCE_SERVER_RESO...		\N	4.29.1	\N	\N	0584525751
authz-4.2.0.Final-KEYCLOAK-9944	hmlnarik@redhat.com	META-INF/jpa-changelog-authz-4.2.0.Final.xml	2026-02-08 21:02:13.270586	62	EXECUTED	9:9968206fca46eecc1f51db9c024bfe56	addPrimaryKey constraintName=CONSTRAINT_RESOUR_URIS_PK, tableName=RESOURCE_URIS		\N	4.29.1	\N	\N	0584525751
4.2.0-KEYCLOAK-6313	wadahiro@gmail.com	META-INF/jpa-changelog-4.2.0.xml	2026-02-08 21:02:13.276647	63	EXECUTED	9:92143a6daea0a3f3b8f598c97ce55c3d	addColumn tableName=REQUIRED_ACTION_PROVIDER		\N	4.29.1	\N	\N	0584525751
4.3.0-KEYCLOAK-7984	wadahiro@gmail.com	META-INF/jpa-changelog-4.3.0.xml	2026-02-08 21:02:13.281408	64	EXECUTED	9:82bab26a27195d889fb0429003b18f40	update tableName=REQUIRED_ACTION_PROVIDER		\N	4.29.1	\N	\N	0584525751
4.6.0-KEYCLOAK-7950	psilva@redhat.com	META-INF/jpa-changelog-4.6.0.xml	2026-02-08 21:02:13.285699	65	EXECUTED	9:e590c88ddc0b38b0ae4249bbfcb5abc3	update tableName=RESOURCE_SERVER_RESOURCE		\N	4.29.1	\N	\N	0584525751
4.6.0-KEYCLOAK-8377	keycloak	META-INF/jpa-changelog-4.6.0.xml	2026-02-08 21:02:13.387048	66	EXECUTED	9:5c1f475536118dbdc38d5d7977950cc0	createTable tableName=ROLE_ATTRIBUTE; addPrimaryKey constraintName=CONSTRAINT_ROLE_ATTRIBUTE_PK, tableName=ROLE_ATTRIBUTE; addForeignKeyConstraint baseTableName=ROLE_ATTRIBUTE, constraintName=FK_ROLE_ATTRIBUTE_ID, referencedTableName=KEYCLOAK_ROLE...		\N	4.29.1	\N	\N	0584525751
4.6.0-KEYCLOAK-8555	gideonray@gmail.com	META-INF/jpa-changelog-4.6.0.xml	2026-02-08 21:02:13.478538	67	EXECUTED	9:e7c9f5f9c4d67ccbbcc215440c718a17	createIndex indexName=IDX_COMPONENT_PROVIDER_TYPE, tableName=COMPONENT		\N	4.29.1	\N	\N	0584525751
4.7.0-KEYCLOAK-1267	sguilhen@redhat.com	META-INF/jpa-changelog-4.7.0.xml	2026-02-08 21:02:13.491259	68	EXECUTED	9:88e0bfdda924690d6f4e430c53447dd5	addColumn tableName=REALM		\N	4.29.1	\N	\N	0584525751
4.7.0-KEYCLOAK-7275	keycloak	META-INF/jpa-changelog-4.7.0.xml	2026-02-08 21:02:13.571183	69	EXECUTED	9:f53177f137e1c46b6a88c59ec1cb5218	renameColumn newColumnName=CREATED_ON, oldColumnName=LAST_SESSION_REFRESH, tableName=OFFLINE_USER_SESSION; addNotNullConstraint columnName=CREATED_ON, tableName=OFFLINE_USER_SESSION; addColumn tableName=OFFLINE_USER_SESSION; customChange; createIn...		\N	4.29.1	\N	\N	0584525751
4.8.0-KEYCLOAK-8835	sguilhen@redhat.com	META-INF/jpa-changelog-4.8.0.xml	2026-02-08 21:02:13.58255	70	EXECUTED	9:a74d33da4dc42a37ec27121580d1459f	addNotNullConstraint columnName=SSO_MAX_LIFESPAN_REMEMBER_ME, tableName=REALM; addNotNullConstraint columnName=SSO_IDLE_TIMEOUT_REMEMBER_ME, tableName=REALM		\N	4.29.1	\N	\N	0584525751
authz-7.0.0-KEYCLOAK-10443	psilva@redhat.com	META-INF/jpa-changelog-authz-7.0.0.xml	2026-02-08 21:02:13.58937	71	EXECUTED	9:fd4ade7b90c3b67fae0bfcfcb42dfb5f	addColumn tableName=RESOURCE_SERVER		\N	4.29.1	\N	\N	0584525751
8.0.0-adding-credential-columns	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-02-08 21:02:13.600124	72	EXECUTED	9:aa072ad090bbba210d8f18781b8cebf4	addColumn tableName=CREDENTIAL; addColumn tableName=FED_USER_CREDENTIAL		\N	4.29.1	\N	\N	0584525751
8.0.0-updating-credential-data-not-oracle-fixed	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-02-08 21:02:13.616777	73	EXECUTED	9:1ae6be29bab7c2aa376f6983b932be37	update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL		\N	4.29.1	\N	\N	0584525751
8.0.0-updating-credential-data-oracle-fixed	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-02-08 21:02:13.621763	74	MARK_RAN	9:14706f286953fc9a25286dbd8fb30d97	update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL; update tableName=FED_USER_CREDENTIAL		\N	4.29.1	\N	\N	0584525751
8.0.0-credential-cleanup-fixed	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-02-08 21:02:13.656177	75	EXECUTED	9:2b9cc12779be32c5b40e2e67711a218b	dropDefaultValue columnName=COUNTER, tableName=CREDENTIAL; dropDefaultValue columnName=DIGITS, tableName=CREDENTIAL; dropDefaultValue columnName=PERIOD, tableName=CREDENTIAL; dropDefaultValue columnName=ALGORITHM, tableName=CREDENTIAL; dropColumn ...		\N	4.29.1	\N	\N	0584525751
8.0.0-resource-tag-support	keycloak	META-INF/jpa-changelog-8.0.0.xml	2026-02-08 21:02:13.71131	76	EXECUTED	9:91fa186ce7a5af127a2d7a91ee083cc5	addColumn tableName=MIGRATION_MODEL; createIndex indexName=IDX_UPDATE_TIME, tableName=MIGRATION_MODEL		\N	4.29.1	\N	\N	0584525751
9.0.0-always-display-client	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-02-08 21:02:13.718673	77	EXECUTED	9:6335e5c94e83a2639ccd68dd24e2e5ad	addColumn tableName=CLIENT		\N	4.29.1	\N	\N	0584525751
9.0.0-drop-constraints-for-column-increase	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-02-08 21:02:13.72158	78	MARK_RAN	9:6bdb5658951e028bfe16fa0a8228b530	dropUniqueConstraint constraintName=UK_FRSR6T700S9V50BU18WS5PMT, tableName=RESOURCE_SERVER_PERM_TICKET; dropUniqueConstraint constraintName=UK_FRSR6T700S9V50BU18WS5HA6, tableName=RESOURCE_SERVER_RESOURCE; dropPrimaryKey constraintName=CONSTRAINT_O...		\N	4.29.1	\N	\N	0584525751
9.0.0-increase-column-size-federated-fk	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-02-08 21:02:13.76058	79	EXECUTED	9:d5bc15a64117ccad481ce8792d4c608f	modifyDataType columnName=CLIENT_ID, tableName=FED_USER_CONSENT; modifyDataType columnName=CLIENT_REALM_CONSTRAINT, tableName=KEYCLOAK_ROLE; modifyDataType columnName=OWNER, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=CLIENT_ID, ta...		\N	4.29.1	\N	\N	0584525751
9.0.0-recreate-constraints-after-column-increase	keycloak	META-INF/jpa-changelog-9.0.0.xml	2026-02-08 21:02:13.764077	80	MARK_RAN	9:077cba51999515f4d3e7ad5619ab592c	addNotNullConstraint columnName=CLIENT_ID, tableName=OFFLINE_CLIENT_SESSION; addNotNullConstraint columnName=OWNER, tableName=RESOURCE_SERVER_PERM_TICKET; addNotNullConstraint columnName=REQUESTER, tableName=RESOURCE_SERVER_PERM_TICKET; addNotNull...		\N	4.29.1	\N	\N	0584525751
9.0.1-add-index-to-client.client_id	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-02-08 21:02:13.84079	81	EXECUTED	9:be969f08a163bf47c6b9e9ead8ac2afb	createIndex indexName=IDX_CLIENT_ID, tableName=CLIENT		\N	4.29.1	\N	\N	0584525751
9.0.1-KEYCLOAK-12579-drop-constraints	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-02-08 21:02:13.843614	82	MARK_RAN	9:6d3bb4408ba5a72f39bd8a0b301ec6e3	dropUniqueConstraint constraintName=SIBLING_NAMES, tableName=KEYCLOAK_GROUP		\N	4.29.1	\N	\N	0584525751
9.0.1-KEYCLOAK-12579-add-not-null-constraint	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-02-08 21:02:13.853149	83	EXECUTED	9:966bda61e46bebf3cc39518fbed52fa7	addNotNullConstraint columnName=PARENT_GROUP, tableName=KEYCLOAK_GROUP		\N	4.29.1	\N	\N	0584525751
9.0.1-KEYCLOAK-12579-recreate-constraints	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-02-08 21:02:13.855942	84	MARK_RAN	9:8dcac7bdf7378e7d823cdfddebf72fda	addUniqueConstraint constraintName=SIBLING_NAMES, tableName=KEYCLOAK_GROUP		\N	4.29.1	\N	\N	0584525751
9.0.1-add-index-to-events	keycloak	META-INF/jpa-changelog-9.0.1.xml	2026-02-08 21:02:13.938315	85	EXECUTED	9:7d93d602352a30c0c317e6a609b56599	createIndex indexName=IDX_EVENT_TIME, tableName=EVENT_ENTITY		\N	4.29.1	\N	\N	0584525751
map-remove-ri	keycloak	META-INF/jpa-changelog-11.0.0.xml	2026-02-08 21:02:13.948776	86	EXECUTED	9:71c5969e6cdd8d7b6f47cebc86d37627	dropForeignKeyConstraint baseTableName=REALM, constraintName=FK_TRAF444KK6QRKMS7N56AIWQ5Y; dropForeignKeyConstraint baseTableName=KEYCLOAK_ROLE, constraintName=FK_KJHO5LE2C0RAL09FL8CM9WFW9		\N	4.29.1	\N	\N	0584525751
map-remove-ri	keycloak	META-INF/jpa-changelog-12.0.0.xml	2026-02-08 21:02:13.963868	87	EXECUTED	9:a9ba7d47f065f041b7da856a81762021	dropForeignKeyConstraint baseTableName=REALM_DEFAULT_GROUPS, constraintName=FK_DEF_GROUPS_GROUP; dropForeignKeyConstraint baseTableName=REALM_DEFAULT_ROLES, constraintName=FK_H4WPD7W4HSOOLNI3H0SW7BTJE; dropForeignKeyConstraint baseTableName=CLIENT...		\N	4.29.1	\N	\N	0584525751
12.1.0-add-realm-localization-table	keycloak	META-INF/jpa-changelog-12.0.0.xml	2026-02-08 21:02:13.980141	88	EXECUTED	9:fffabce2bc01e1a8f5110d5278500065	createTable tableName=REALM_LOCALIZATIONS; addPrimaryKey tableName=REALM_LOCALIZATIONS		\N	4.29.1	\N	\N	0584525751
default-roles	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:13.991632	89	EXECUTED	9:fa8a5b5445e3857f4b010bafb5009957	addColumn tableName=REALM; customChange		\N	4.29.1	\N	\N	0584525751
default-roles-cleanup	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.006312	90	EXECUTED	9:67ac3241df9a8582d591c5ed87125f39	dropTable tableName=REALM_DEFAULT_ROLES; dropTable tableName=CLIENT_DEFAULT_ROLES		\N	4.29.1	\N	\N	0584525751
13.0.0-KEYCLOAK-16844	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.073751	91	EXECUTED	9:ad1194d66c937e3ffc82386c050ba089	createIndex indexName=IDX_OFFLINE_USS_PRELOAD, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
map-remove-ri-13.0.0	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.09168	92	EXECUTED	9:d9be619d94af5a2f5d07b9f003543b91	dropForeignKeyConstraint baseTableName=DEFAULT_CLIENT_SCOPE, constraintName=FK_R_DEF_CLI_SCOPE_SCOPE; dropForeignKeyConstraint baseTableName=CLIENT_SCOPE_CLIENT, constraintName=FK_C_CLI_SCOPE_SCOPE; dropForeignKeyConstraint baseTableName=CLIENT_SC...		\N	4.29.1	\N	\N	0584525751
13.0.0-KEYCLOAK-17992-drop-constraints	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.094004	93	MARK_RAN	9:544d201116a0fcc5a5da0925fbbc3bde	dropPrimaryKey constraintName=C_CLI_SCOPE_BIND, tableName=CLIENT_SCOPE_CLIENT; dropIndex indexName=IDX_CLSCOPE_CL, tableName=CLIENT_SCOPE_CLIENT; dropIndex indexName=IDX_CL_CLSCOPE, tableName=CLIENT_SCOPE_CLIENT		\N	4.29.1	\N	\N	0584525751
13.0.0-increase-column-size-federated	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.109883	94	EXECUTED	9:43c0c1055b6761b4b3e89de76d612ccf	modifyDataType columnName=CLIENT_ID, tableName=CLIENT_SCOPE_CLIENT; modifyDataType columnName=SCOPE_ID, tableName=CLIENT_SCOPE_CLIENT		\N	4.29.1	\N	\N	0584525751
13.0.0-KEYCLOAK-17992-recreate-constraints	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.112638	95	MARK_RAN	9:8bd711fd0330f4fe980494ca43ab1139	addNotNullConstraint columnName=CLIENT_ID, tableName=CLIENT_SCOPE_CLIENT; addNotNullConstraint columnName=SCOPE_ID, tableName=CLIENT_SCOPE_CLIENT; addPrimaryKey constraintName=C_CLI_SCOPE_BIND, tableName=CLIENT_SCOPE_CLIENT; createIndex indexName=...		\N	4.29.1	\N	\N	0584525751
json-string-accomodation-fixed	keycloak	META-INF/jpa-changelog-13.0.0.xml	2026-02-08 21:02:14.121721	96	EXECUTED	9:e07d2bc0970c348bb06fb63b1f82ddbf	addColumn tableName=REALM_ATTRIBUTE; update tableName=REALM_ATTRIBUTE; dropColumn columnName=VALUE, tableName=REALM_ATTRIBUTE; renameColumn newColumnName=VALUE, oldColumnName=VALUE_NEW, tableName=REALM_ATTRIBUTE		\N	4.29.1	\N	\N	0584525751
14.0.0-KEYCLOAK-11019	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.25671	97	EXECUTED	9:24fb8611e97f29989bea412aa38d12b7	createIndex indexName=IDX_OFFLINE_CSS_PRELOAD, tableName=OFFLINE_CLIENT_SESSION; createIndex indexName=IDX_OFFLINE_USS_BY_USER, tableName=OFFLINE_USER_SESSION; createIndex indexName=IDX_OFFLINE_USS_BY_USERSESS, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
14.0.0-KEYCLOAK-18286	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.259118	98	MARK_RAN	9:259f89014ce2506ee84740cbf7163aa7	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
14.0.0-KEYCLOAK-18286-revert	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.274605	99	MARK_RAN	9:04baaf56c116ed19951cbc2cca584022	dropIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
14.0.0-KEYCLOAK-18286-supported-dbs	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.332822	100	EXECUTED	9:60ca84a0f8c94ec8c3504a5a3bc88ee8	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
14.0.0-KEYCLOAK-18286-unsupported-dbs	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.335726	101	MARK_RAN	9:d3d977031d431db16e2c181ce49d73e9	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
KEYCLOAK-17267-add-index-to-user-attributes	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.396554	102	EXECUTED	9:0b305d8d1277f3a89a0a53a659ad274c	createIndex indexName=IDX_USER_ATTRIBUTE_NAME, tableName=USER_ATTRIBUTE		\N	4.29.1	\N	\N	0584525751
KEYCLOAK-18146-add-saml-art-binding-identifier	keycloak	META-INF/jpa-changelog-14.0.0.xml	2026-02-08 21:02:14.402864	103	EXECUTED	9:2c374ad2cdfe20e2905a84c8fac48460	customChange		\N	4.29.1	\N	\N	0584525751
15.0.0-KEYCLOAK-18467	keycloak	META-INF/jpa-changelog-15.0.0.xml	2026-02-08 21:02:14.410542	104	EXECUTED	9:47a760639ac597360a8219f5b768b4de	addColumn tableName=REALM_LOCALIZATIONS; update tableName=REALM_LOCALIZATIONS; dropColumn columnName=TEXTS, tableName=REALM_LOCALIZATIONS; renameColumn newColumnName=TEXTS, oldColumnName=TEXTS_NEW, tableName=REALM_LOCALIZATIONS; addNotNullConstrai...		\N	4.29.1	\N	\N	0584525751
17.0.0-9562	keycloak	META-INF/jpa-changelog-17.0.0.xml	2026-02-08 21:02:14.468861	105	EXECUTED	9:a6272f0576727dd8cad2522335f5d99e	createIndex indexName=IDX_USER_SERVICE_ACCOUNT, tableName=USER_ENTITY		\N	4.29.1	\N	\N	0584525751
18.0.0-10625-IDX_ADMIN_EVENT_TIME	keycloak	META-INF/jpa-changelog-18.0.0.xml	2026-02-08 21:02:14.523633	106	EXECUTED	9:015479dbd691d9cc8669282f4828c41d	createIndex indexName=IDX_ADMIN_EVENT_TIME, tableName=ADMIN_EVENT_ENTITY		\N	4.29.1	\N	\N	0584525751
18.0.15-30992-index-consent	keycloak	META-INF/jpa-changelog-18.0.15.xml	2026-02-08 21:02:14.581416	107	EXECUTED	9:80071ede7a05604b1f4906f3bf3b00f0	createIndex indexName=IDX_USCONSENT_SCOPE_ID, tableName=USER_CONSENT_CLIENT_SCOPE		\N	4.29.1	\N	\N	0584525751
19.0.0-10135	keycloak	META-INF/jpa-changelog-19.0.0.xml	2026-02-08 21:02:14.586013	108	EXECUTED	9:9518e495fdd22f78ad6425cc30630221	customChange		\N	4.29.1	\N	\N	0584525751
20.0.0-12964-supported-dbs	keycloak	META-INF/jpa-changelog-20.0.0.xml	2026-02-08 21:02:14.639169	109	EXECUTED	9:e5f243877199fd96bcc842f27a1656ac	createIndex indexName=IDX_GROUP_ATT_BY_NAME_VALUE, tableName=GROUP_ATTRIBUTE		\N	4.29.1	\N	\N	0584525751
20.0.0-12964-unsupported-dbs	keycloak	META-INF/jpa-changelog-20.0.0.xml	2026-02-08 21:02:14.641467	110	MARK_RAN	9:1a6fcaa85e20bdeae0a9ce49b41946a5	createIndex indexName=IDX_GROUP_ATT_BY_NAME_VALUE, tableName=GROUP_ATTRIBUTE		\N	4.29.1	\N	\N	0584525751
client-attributes-string-accomodation-fixed	keycloak	META-INF/jpa-changelog-20.0.0.xml	2026-02-08 21:02:14.651793	111	EXECUTED	9:3f332e13e90739ed0c35b0b25b7822ca	addColumn tableName=CLIENT_ATTRIBUTES; update tableName=CLIENT_ATTRIBUTES; dropColumn columnName=VALUE, tableName=CLIENT_ATTRIBUTES; renameColumn newColumnName=VALUE, oldColumnName=VALUE_NEW, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
21.0.2-17277	keycloak	META-INF/jpa-changelog-21.0.2.xml	2026-02-08 21:02:14.659134	112	EXECUTED	9:7ee1f7a3fb8f5588f171fb9a6ab623c0	customChange		\N	4.29.1	\N	\N	0584525751
21.1.0-19404	keycloak	META-INF/jpa-changelog-21.1.0.xml	2026-02-08 21:02:14.707346	113	EXECUTED	9:3d7e830b52f33676b9d64f7f2b2ea634	modifyDataType columnName=DECISION_STRATEGY, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=LOGIC, tableName=RESOURCE_SERVER_POLICY; modifyDataType columnName=POLICY_ENFORCE_MODE, tableName=RESOURCE_SERVER		\N	4.29.1	\N	\N	0584525751
21.1.0-19404-2	keycloak	META-INF/jpa-changelog-21.1.0.xml	2026-02-08 21:02:14.711057	114	MARK_RAN	9:627d032e3ef2c06c0e1f73d2ae25c26c	addColumn tableName=RESOURCE_SERVER_POLICY; update tableName=RESOURCE_SERVER_POLICY; dropColumn columnName=DECISION_STRATEGY, tableName=RESOURCE_SERVER_POLICY; renameColumn newColumnName=DECISION_STRATEGY, oldColumnName=DECISION_STRATEGY_NEW, tabl...		\N	4.29.1	\N	\N	0584525751
22.0.0-17484-updated	keycloak	META-INF/jpa-changelog-22.0.0.xml	2026-02-08 21:02:14.717638	115	EXECUTED	9:90af0bfd30cafc17b9f4d6eccd92b8b3	customChange		\N	4.29.1	\N	\N	0584525751
22.0.5-24031	keycloak	META-INF/jpa-changelog-22.0.0.xml	2026-02-08 21:02:14.719368	116	MARK_RAN	9:a60d2d7b315ec2d3eba9e2f145f9df28	customChange		\N	4.29.1	\N	\N	0584525751
23.0.0-12062	keycloak	META-INF/jpa-changelog-23.0.0.xml	2026-02-08 21:02:14.72647	117	EXECUTED	9:2168fbe728fec46ae9baf15bf80927b8	addColumn tableName=COMPONENT_CONFIG; update tableName=COMPONENT_CONFIG; dropColumn columnName=VALUE, tableName=COMPONENT_CONFIG; renameColumn newColumnName=VALUE, oldColumnName=VALUE_NEW, tableName=COMPONENT_CONFIG		\N	4.29.1	\N	\N	0584525751
23.0.0-17258	keycloak	META-INF/jpa-changelog-23.0.0.xml	2026-02-08 21:02:14.730798	118	EXECUTED	9:36506d679a83bbfda85a27ea1864dca8	addColumn tableName=EVENT_ENTITY		\N	4.29.1	\N	\N	0584525751
24.0.0-9758	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-02-08 21:02:14.956384	119	EXECUTED	9:502c557a5189f600f0f445a9b49ebbce	addColumn tableName=USER_ATTRIBUTE; addColumn tableName=FED_USER_ATTRIBUTE; createIndex indexName=USER_ATTR_LONG_VALUES, tableName=USER_ATTRIBUTE; createIndex indexName=FED_USER_ATTR_LONG_VALUES, tableName=FED_USER_ATTRIBUTE; createIndex indexName...		\N	4.29.1	\N	\N	0584525751
24.0.0-9758-2	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-02-08 21:02:14.962048	120	EXECUTED	9:bf0fdee10afdf597a987adbf291db7b2	customChange		\N	4.29.1	\N	\N	0584525751
24.0.0-26618-drop-index-if-present	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-02-08 21:02:14.968661	121	MARK_RAN	9:04baaf56c116ed19951cbc2cca584022	dropIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
24.0.0-26618-reindex	keycloak	META-INF/jpa-changelog-24.0.0.xml	2026-02-08 21:02:15.020735	122	EXECUTED	9:08707c0f0db1cef6b352db03a60edc7f	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
24.0.2-27228	keycloak	META-INF/jpa-changelog-24.0.2.xml	2026-02-08 21:02:15.025337	123	EXECUTED	9:eaee11f6b8aa25d2cc6a84fb86fc6238	customChange		\N	4.29.1	\N	\N	0584525751
24.0.2-27967-drop-index-if-present	keycloak	META-INF/jpa-changelog-24.0.2.xml	2026-02-08 21:02:15.026869	124	MARK_RAN	9:04baaf56c116ed19951cbc2cca584022	dropIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
24.0.2-27967-reindex	keycloak	META-INF/jpa-changelog-24.0.2.xml	2026-02-08 21:02:15.029113	125	MARK_RAN	9:d3d977031d431db16e2c181ce49d73e9	createIndex indexName=IDX_CLIENT_ATT_BY_NAME_VALUE, tableName=CLIENT_ATTRIBUTES		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-tables	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.034954	126	EXECUTED	9:deda2df035df23388af95bbd36c17cef	addColumn tableName=OFFLINE_USER_SESSION; addColumn tableName=OFFLINE_CLIENT_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-creation	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.085311	127	EXECUTED	9:3e96709818458ae49f3c679ae58d263a	createIndex indexName=IDX_OFFLINE_USS_BY_LAST_SESSION_REFRESH, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-cleanup-uss-createdon	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.21617	128	EXECUTED	9:78ab4fc129ed5e8265dbcc3485fba92f	dropIndex indexName=IDX_OFFLINE_USS_CREATEDON, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-cleanup-uss-preload	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.34293	129	EXECUTED	9:de5f7c1f7e10994ed8b62e621d20eaab	dropIndex indexName=IDX_OFFLINE_USS_PRELOAD, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-cleanup-uss-by-usersess	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.457511	130	EXECUTED	9:6eee220d024e38e89c799417ec33667f	dropIndex indexName=IDX_OFFLINE_USS_BY_USERSESS, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-cleanup-css-preload	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.551766	131	EXECUTED	9:5411d2fb2891d3e8d63ddb55dfa3c0c9	dropIndex indexName=IDX_OFFLINE_CSS_PRELOAD, tableName=OFFLINE_CLIENT_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-2-mysql	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.554916	132	MARK_RAN	9:b7ef76036d3126bb83c2423bf4d449d6	createIndex indexName=IDX_OFFLINE_USS_BY_BROKER_SESSION_ID, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-28265-index-2-not-mysql	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.617369	133	EXECUTED	9:23396cf51ab8bc1ae6f0cac7f9f6fcf7	createIndex indexName=IDX_OFFLINE_USS_BY_BROKER_SESSION_ID, tableName=OFFLINE_USER_SESSION		\N	4.29.1	\N	\N	0584525751
25.0.0-org	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.650127	134	EXECUTED	9:5c859965c2c9b9c72136c360649af157	createTable tableName=ORG; addUniqueConstraint constraintName=UK_ORG_NAME, tableName=ORG; addUniqueConstraint constraintName=UK_ORG_GROUP, tableName=ORG; createTable tableName=ORG_DOMAIN		\N	4.29.1	\N	\N	0584525751
unique-consentuser	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.665679	135	EXECUTED	9:5857626a2ea8767e9a6c66bf3a2cb32f	customChange; dropUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHOGM8UEWRT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_LOCAL_CONSENT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_EXTERNAL_CONSENT, tableName=...		\N	4.29.1	\N	\N	0584525751
unique-consentuser-mysql	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.668367	136	MARK_RAN	9:b79478aad5adaa1bc428e31563f55e8e	customChange; dropUniqueConstraint constraintName=UK_JKUWUVD56ONTGSUHOGM8UEWRT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_LOCAL_CONSENT, tableName=USER_CONSENT; addUniqueConstraint constraintName=UK_EXTERNAL_CONSENT, tableName=...		\N	4.29.1	\N	\N	0584525751
25.0.0-28861-index-creation	keycloak	META-INF/jpa-changelog-25.0.0.xml	2026-02-08 21:02:15.775333	137	EXECUTED	9:b9acb58ac958d9ada0fe12a5d4794ab1	createIndex indexName=IDX_PERM_TICKET_REQUESTER, tableName=RESOURCE_SERVER_PERM_TICKET; createIndex indexName=IDX_PERM_TICKET_OWNER, tableName=RESOURCE_SERVER_PERM_TICKET		\N	4.29.1	\N	\N	0584525751
26.0.0-org-alias	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:15.791119	138	EXECUTED	9:6ef7d63e4412b3c2d66ed179159886a4	addColumn tableName=ORG; update tableName=ORG; addNotNullConstraint columnName=ALIAS, tableName=ORG; addUniqueConstraint constraintName=UK_ORG_ALIAS, tableName=ORG		\N	4.29.1	\N	\N	0584525751
26.0.0-org-group	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:15.804073	139	EXECUTED	9:da8e8087d80ef2ace4f89d8c5b9ca223	addColumn tableName=KEYCLOAK_GROUP; update tableName=KEYCLOAK_GROUP; addNotNullConstraint columnName=TYPE, tableName=KEYCLOAK_GROUP; customChange		\N	4.29.1	\N	\N	0584525751
26.0.0-org-indexes	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:15.869857	140	EXECUTED	9:79b05dcd610a8c7f25ec05135eec0857	createIndex indexName=IDX_ORG_DOMAIN_ORG_ID, tableName=ORG_DOMAIN		\N	4.29.1	\N	\N	0584525751
26.0.0-org-group-membership	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:15.879054	141	EXECUTED	9:a6ace2ce583a421d89b01ba2a28dc2d4	addColumn tableName=USER_GROUP_MEMBERSHIP; update tableName=USER_GROUP_MEMBERSHIP; addNotNullConstraint columnName=MEMBERSHIP_TYPE, tableName=USER_GROUP_MEMBERSHIP		\N	4.29.1	\N	\N	0584525751
31296-persist-revoked-access-tokens	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:15.890937	142	EXECUTED	9:64ef94489d42a358e8304b0e245f0ed4	createTable tableName=REVOKED_TOKEN; addPrimaryKey constraintName=CONSTRAINT_RT, tableName=REVOKED_TOKEN		\N	4.29.1	\N	\N	0584525751
31725-index-persist-revoked-access-tokens	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:15.954657	143	EXECUTED	9:b994246ec2bf7c94da881e1d28782c7b	createIndex indexName=IDX_REV_TOKEN_ON_EXPIRE, tableName=REVOKED_TOKEN		\N	4.29.1	\N	\N	0584525751
26.0.0-idps-for-login	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:16.078372	144	EXECUTED	9:51f5fffadf986983d4bd59582c6c1604	addColumn tableName=IDENTITY_PROVIDER; createIndex indexName=IDX_IDP_REALM_ORG, tableName=IDENTITY_PROVIDER; createIndex indexName=IDX_IDP_FOR_LOGIN, tableName=IDENTITY_PROVIDER; customChange		\N	4.29.1	\N	\N	0584525751
26.0.0-32583-drop-redundant-index-on-client-session	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:16.170656	145	EXECUTED	9:24972d83bf27317a055d234187bb4af9	dropIndex indexName=IDX_US_SESS_ID_ON_CL_SESS, tableName=OFFLINE_CLIENT_SESSION		\N	4.29.1	\N	\N	0584525751
26.0.0.32582-remove-tables-user-session-user-session-note-and-client-session	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:16.21205	146	EXECUTED	9:febdc0f47f2ed241c59e60f58c3ceea5	dropTable tableName=CLIENT_SESSION_ROLE; dropTable tableName=CLIENT_SESSION_NOTE; dropTable tableName=CLIENT_SESSION_PROT_MAPPER; dropTable tableName=CLIENT_SESSION_AUTH_STATUS; dropTable tableName=CLIENT_USER_SESSION_NOTE; dropTable tableName=CLI...		\N	4.29.1	\N	\N	0584525751
26.0.0-33201-org-redirect-url	keycloak	META-INF/jpa-changelog-26.0.0.xml	2026-02-08 21:02:16.218562	147	EXECUTED	9:4d0e22b0ac68ebe9794fa9cb752ea660	addColumn tableName=ORG		\N	4.29.1	\N	\N	0584525751
29399-jdbc-ping-default	keycloak	META-INF/jpa-changelog-26.1.0.xml	2026-02-08 21:02:16.23402	148	EXECUTED	9:007dbe99d7203fca403b89d4edfdf21e	createTable tableName=JGROUPS_PING; addPrimaryKey constraintName=CONSTRAINT_JGROUPS_PING, tableName=JGROUPS_PING		\N	4.29.1	\N	\N	0584525751
26.1.0-34013	keycloak	META-INF/jpa-changelog-26.1.0.xml	2026-02-08 21:02:16.245906	149	EXECUTED	9:e6b686a15759aef99a6d758a5c4c6a26	addColumn tableName=ADMIN_EVENT_ENTITY		\N	4.29.1	\N	\N	0584525751
26.1.0-34380	keycloak	META-INF/jpa-changelog-26.1.0.xml	2026-02-08 21:02:16.256394	150	EXECUTED	9:ac8b9edb7c2b6c17a1c7a11fcf5ccf01	dropTable tableName=USERNAME_LOGIN_FAILURE		\N	4.29.1	\N	\N	0584525751
\.


--
-- Data for Name: databasechangelog_ext_entity; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.databasechangelog_ext_entity (id, author, filename, dateexecuted, orderexecuted, exectype, md5sum, description, comments, tag, liquibase, contexts, labels, deployment_id) FROM stdin;
202203111522-1	garth (generated)	META-INF/jpa-changelog-events-20220311.xml	2026-02-13 06:55:45.680245	1	EXECUTED	9:4be49121671f6f633afc3f184cae4a2f	createTable tableName=WEBHOOK; addPrimaryKey constraintName=WEBHOOKPK, tableName=WEBHOOK; createTable tableName=WEBHOOK_EVENT_TYPES; addForeignKeyConstraint baseTableName=WEBHOOK_EVENT_TYPES, constraintName=FK_H84RSK1GFRPJGWMN21UPW149J, referenced...		\N	4.29.1	\N	\N	0965745619
202211131938-1	garth	META-INF/jpa-changelog-events-20221113.xml	2026-02-13 06:55:45.688002	2	EXECUTED	9:93daf2128954ff63d0235867c17a3555	addColumn tableName=WEBHOOK		\N	4.29.1	\N	\N	0965745619
202501121734-1	xgp	META-INF/jpa-changelog-events-20250112.xml	2026-02-13 06:55:45.709735	3	EXECUTED	9:9b31476ddbb7b5280a77efa98aae58fd	createTable tableName=WEBHOOK_EVENT; addPrimaryKey constraintName=WEBHOOK_EVENTPK, tableName=WEBHOOK_EVENT; addForeignKeyConstraint baseTableName=WEBHOOK_EVENT, constraintName=FK_PKCQEW0VY67VP2RB4T8CO7NWJ, referencedTableName=EVENT_ENTITY; addFore...		\N	4.29.1	\N	\N	0965745619
202501121734-2	xgp	META-INF/jpa-changelog-events-20250112.xml	2026-02-13 06:55:45.716769	4	EXECUTED	9:3e2e09af9128a720018c227878e9eff6	addColumn tableName=WEBHOOK_EVENT		\N	4.29.1	\N	\N	0965745619
202501121734-3	xgp	META-INF/jpa-changelog-events-20250112.xml	2026-02-13 06:55:45.719678	5	MARK_RAN	9:a6b7ddf73716fd349f798fccaf8e470c	addColumn tableName=WEBHOOK_EVENT		\N	4.29.1	\N	\N	0965745619
\.


--
-- Data for Name: databasechangeloglock; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.databasechangeloglock (id, locked, lockgranted, lockedby) FROM stdin;
1	f	\N	\N
1000	f	\N	\N
\.


--
-- Data for Name: default_client_scope; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.default_client_scope (realm_id, scope_id, default_scope) FROM stdin;
eacf1fae-7916-43d5-b7e0-7abf35df7d49	9fdd8c0f-eaa0-4d93-bcf5-25abd93ccca5	f
eacf1fae-7916-43d5-b7e0-7abf35df7d49	f992b9ed-1c4b-47fd-83e1-c26c3e795a4b	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	d8720c55-a547-4bdc-9b07-06404c8c1a30	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	eab4d0d4-3184-468f-bb10-5b82c5762e97	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	264770a9-8682-4235-83cf-2e12d59fd9ac	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	dc32533a-1e41-47f9-b737-3b644b5713fa	f
eacf1fae-7916-43d5-b7e0-7abf35df7d49	b0f472dd-8acb-45cc-9e6b-97efe9536cb0	f
eacf1fae-7916-43d5-b7e0-7abf35df7d49	5af152b0-b6d4-47eb-91d6-bd8589de25b8	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	42cc9b6b-5715-4721-bd05-47c7507840f1	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	e3c878a1-9bec-4f37-a5e0-84f3561e9d65	f
eacf1fae-7916-43d5-b7e0-7abf35df7d49	e7f9379d-5bc0-481c-abc5-f1f8026fdd34	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	a3b9f256-1ff5-4108-be26-5da60bfc3877	t
eacf1fae-7916-43d5-b7e0-7abf35df7d49	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948	f
2c411af7-e0b7-4547-b08a-27c7c8c1722c	cdcec106-3ff3-4861-b009-d792877b713c	f
2c411af7-e0b7-4547-b08a-27c7c8c1722c	617e9e7c-c22d-468e-a3ae-86385181237d	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	e2261f11-2475-4538-bc0e-f663a4131459	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	a3d9b5bb-e717-4518-adbc-07bc0f692d64	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	cd5bc29d-1eae-4363-b403-3cd338a2653f	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	1aa1a3d0-d37d-4043-9c61-219994890dbe	f
2c411af7-e0b7-4547-b08a-27c7c8c1722c	3471014d-13bf-4c91-82fe-e145e45ce62c	f
2c411af7-e0b7-4547-b08a-27c7c8c1722c	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	44d90b70-00c8-485c-a91a-f77e616baf36	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912	f
2c411af7-e0b7-4547-b08a-27c7c8c1722c	74f581d3-8e6c-4ffc-aa96-5780938ff437	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	30a49f27-9f43-47ee-8a2a-91143cd0a6c4	t
2c411af7-e0b7-4547-b08a-27c7c8c1722c	b8df8620-7249-4102-a288-c70ca38e4eac	f
\.


--
-- Data for Name: event_entity; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.event_entity (id, client_id, details_json, error, ip_address, realm_id, session_id, event_time, type, user_id, details_json_long_value) FROM stdin;
\.


--
-- Data for Name: fed_user_attribute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_attribute (id, name, user_id, realm_id, storage_provider_id, value, long_value_hash, long_value_hash_lower_case, long_value) FROM stdin;
\.


--
-- Data for Name: fed_user_consent; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_consent (id, client_id, user_id, realm_id, storage_provider_id, created_date, last_updated_date, client_storage_provider, external_client_id) FROM stdin;
\.


--
-- Data for Name: fed_user_consent_cl_scope; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_consent_cl_scope (user_consent_id, scope_id) FROM stdin;
\.


--
-- Data for Name: fed_user_credential; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_credential (id, salt, type, created_date, user_id, realm_id, storage_provider_id, user_label, secret_data, credential_data, priority) FROM stdin;
\.


--
-- Data for Name: fed_user_group_membership; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_group_membership (group_id, user_id, realm_id, storage_provider_id) FROM stdin;
\.


--
-- Data for Name: fed_user_required_action; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_required_action (required_action, user_id, realm_id, storage_provider_id) FROM stdin;
\.


--
-- Data for Name: fed_user_role_mapping; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.fed_user_role_mapping (role_id, user_id, realm_id, storage_provider_id) FROM stdin;
\.


--
-- Data for Name: federated_identity; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.federated_identity (identity_provider, realm_id, federated_user_id, federated_username, token, user_id) FROM stdin;
\.


--
-- Data for Name: federated_user; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.federated_user (id, storage_provider_id, realm_id) FROM stdin;
\.


--
-- Data for Name: group_attribute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.group_attribute (id, name, value, group_id) FROM stdin;
\.


--
-- Data for Name: group_role_mapping; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.group_role_mapping (role_id, group_id) FROM stdin;
\.


--
-- Data for Name: identity_provider; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.identity_provider (internal_id, enabled, provider_alias, provider_id, store_token, authenticate_by_default, realm_id, add_token_role, trust_email, first_broker_login_flow_id, post_broker_login_flow_id, provider_display_name, link_only, organization_id, hide_on_login) FROM stdin;
9bca333e-dc8e-4fe7-837d-662a486645dc	t	google	google	f	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	f	\N	\N		f	\N	f
d2a5522d-e81a-430a-a282-2e893ac51fb7	t	facebook	facebook	f	f	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	f	\N	\N		f	\N	f
\.


--
-- Data for Name: identity_provider_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.identity_provider_config (identity_provider_id, value, name) FROM stdin;
9bca333e-dc8e-4fe7-837d-662a486645dc	admin	clientId
9bca333e-dc8e-4fe7-837d-662a486645dc	false	acceptsPromptNoneForwardFromClient
9bca333e-dc8e-4fe7-837d-662a486645dc	false	disableUserInfo
9bca333e-dc8e-4fe7-837d-662a486645dc	LEGACY	syncMode
9bca333e-dc8e-4fe7-837d-662a486645dc	false	filteredByClaim
9bca333e-dc8e-4fe7-837d-662a486645dc	admin	clientSecret
9bca333e-dc8e-4fe7-837d-662a486645dc	false	caseSensitiveOriginalUsername
d2a5522d-e81a-430a-a282-2e893ac51fb7	admin	clientId
d2a5522d-e81a-430a-a282-2e893ac51fb7	false	acceptsPromptNoneForwardFromClient
d2a5522d-e81a-430a-a282-2e893ac51fb7	false	disableUserInfo
d2a5522d-e81a-430a-a282-2e893ac51fb7	LEGACY	syncMode
d2a5522d-e81a-430a-a282-2e893ac51fb7	false	filteredByClaim
d2a5522d-e81a-430a-a282-2e893ac51fb7	admin	clientSecret
d2a5522d-e81a-430a-a282-2e893ac51fb7	false	caseSensitiveOriginalUsername
\.


--
-- Data for Name: identity_provider_mapper; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.identity_provider_mapper (id, name, idp_alias, idp_mapper_name, realm_id) FROM stdin;
\.


--
-- Data for Name: idp_mapper_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.idp_mapper_config (idp_mapper_id, value, name) FROM stdin;
\.


--
-- Data for Name: jgroups_ping; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.jgroups_ping (address, name, cluster_name, ip, coord) FROM stdin;
\.


--
-- Data for Name: keycloak_group; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.keycloak_group (id, name, parent_group, realm_id, type) FROM stdin;
\.


--
-- Data for Name: keycloak_role; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.keycloak_role (id, client_realm_constraint, client_role, description, name, realm_id, client, realm) FROM stdin;
b4450810-c34f-4a44-8e5c-dd185fdbef3a	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	${role_default-roles}	default-roles-master	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	\N
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	${role_admin}	admin	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	\N
427cf14a-20c3-4677-bc14-66ae3ab4b7ef	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	${role_create-realm}	create-realm	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	\N
ba9641b7-1284-4d3f-967f-5a3c907d059b	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_create-client}	create-client	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
15a45b51-74fd-4769-afed-e70c6c217964	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_view-realm}	view-realm	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
0c60bbad-957f-4347-8723-bfe69ce4ccdd	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_view-users}	view-users	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
dd7ac4c9-3f74-42e5-95ef-0a83977578cf	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_view-clients}	view-clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
c4a1283e-e170-44b3-bd1e-eeb5365b3bbd	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_view-events}	view-events	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
c38f62ea-0985-457a-bc02-f0679ac4cdce	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_view-identity-providers}	view-identity-providers	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
7d1d053e-0477-46fa-9300-09c0792d384d	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_view-authorization}	view-authorization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
174f3124-b0c6-4d41-884c-6128651028dd	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_manage-realm}	manage-realm	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
e327373d-49f1-451c-8424-c48fc567b438	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_manage-users}	manage-users	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
bdef878f-76fe-4c3f-a76c-d77e61b01d29	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_manage-clients}	manage-clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
e6d78f65-1098-478c-a611-f23e5bb58a01	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_manage-events}	manage-events	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
d63858d6-f962-433d-b3b1-ce24ef8fc707	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_manage-identity-providers}	manage-identity-providers	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
a8dfd3e6-c4b4-4035-8361-864bc23869ba	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_manage-authorization}	manage-authorization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
38b6a046-483c-4859-844d-b517d47f5760	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_query-users}	query-users	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
6b348828-05d4-41c3-a22a-aad668e5f602	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_query-clients}	query-clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
023d628d-fac0-4ea8-8113-126aa95e421c	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_query-realms}	query-realms	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
99fb241b-b784-448c-b22d-8e9bd3147275	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_query-groups}	query-groups	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
8915e9c0-bd83-4bca-bf1b-b1c1a4541230	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_view-profile}	view-profile	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
057fcb24-70d4-43df-8c5f-6d26d91a0b77	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_manage-account}	manage-account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
5a3a984b-603d-4d38-8a5b-26dd99741850	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_manage-account-links}	manage-account-links	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
e51b2021-b4c3-43d7-a019-689741f2f4ea	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_view-applications}	view-applications	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
df377c6a-6cc5-4f50-b9e6-ec61ae76a0f9	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_view-consent}	view-consent	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
71a0d1cd-c06b-4368-97cb-c680f8905d7f	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_manage-consent}	manage-consent	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
643fba7e-98b5-4b0b-8ee4-14220fe712ee	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_view-groups}	view-groups	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
e54e85f2-9f83-4b17-b61c-bf3aaac41298	d7e66ce3-0769-4b3d-9636-4893459eaf54	t	${role_delete-account}	delete-account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	d7e66ce3-0769-4b3d-9636-4893459eaf54	\N
7bc0a4b6-186b-41fd-af6d-473f17000a2c	cb742081-b162-4207-9130-f1b5f073fd9c	t	${role_read-token}	read-token	eacf1fae-7916-43d5-b7e0-7abf35df7d49	cb742081-b162-4207-9130-f1b5f073fd9c	\N
44e2329b-36d5-4aa9-8418-e51a942a8012	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_impersonation}	impersonation	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
973da7a0-958d-44bf-9eb4-434cbb674f8d	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	${role_offline-access}	offline_access	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	\N
1331af7f-96ee-4be6-8327-174d11a76462	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	${role_uma_authorization}	uma_authorization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	\N	\N
a6fb666e-17a0-4cf9-95c2-820ed013c95b	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	${role_default-roles}	default-roles-tskhra	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N	\N
c3e11b21-9738-4a36-bfc6-fceb29a9ed38	2970b512-2182-4062-9dfe-7299580cf689	t	${role_create-client}	create-client	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
a782e775-7916-4809-b19c-b11eeecf9abe	2970b512-2182-4062-9dfe-7299580cf689	t	${role_view-realm}	view-realm	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
1821e665-8e49-4022-ba20-a02b63b52d8c	2970b512-2182-4062-9dfe-7299580cf689	t	${role_view-users}	view-users	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
d899df67-7201-46b5-8a84-e7beee8d516c	2970b512-2182-4062-9dfe-7299580cf689	t	${role_view-clients}	view-clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
ea87aef2-2c8b-4ef0-856e-15ebd184d07a	2970b512-2182-4062-9dfe-7299580cf689	t	${role_view-events}	view-events	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
8367301d-d8f6-4147-98f6-be21fc338de5	2970b512-2182-4062-9dfe-7299580cf689	t	${role_view-identity-providers}	view-identity-providers	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
3989b164-aae5-4fe2-8ba4-e3b47f274d93	2970b512-2182-4062-9dfe-7299580cf689	t	${role_view-authorization}	view-authorization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
53aeedf4-9e15-47b2-b3fa-baa1953702ae	2970b512-2182-4062-9dfe-7299580cf689	t	${role_manage-realm}	manage-realm	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
d2d79a5f-6693-4080-ba4a-893972e23a10	2970b512-2182-4062-9dfe-7299580cf689	t	${role_manage-users}	manage-users	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
2415a4ce-cd09-4edd-bc77-a87815f7c647	2970b512-2182-4062-9dfe-7299580cf689	t	${role_manage-clients}	manage-clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
2b1e8855-c23c-4c80-8fba-5b41ceae5748	2970b512-2182-4062-9dfe-7299580cf689	t	${role_manage-events}	manage-events	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
601df922-dfd9-4a1f-996c-a353b5f0b25c	2970b512-2182-4062-9dfe-7299580cf689	t	${role_manage-identity-providers}	manage-identity-providers	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
a5951dd5-a5d1-49a3-9e18-3609d496cd13	2970b512-2182-4062-9dfe-7299580cf689	t	${role_manage-authorization}	manage-authorization	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
e7ef5559-f74c-45a4-a327-7e56b190c00e	2970b512-2182-4062-9dfe-7299580cf689	t	${role_query-users}	query-users	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
2092d9c7-6da7-4d09-8c6c-78e63e536578	2970b512-2182-4062-9dfe-7299580cf689	t	${role_query-clients}	query-clients	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
bf241197-8577-4608-87ba-b92778ac17d9	2970b512-2182-4062-9dfe-7299580cf689	t	${role_query-realms}	query-realms	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
036bfab2-b22f-4e71-8364-3a5c495f88ab	2970b512-2182-4062-9dfe-7299580cf689	t	${role_query-groups}	query-groups	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
777c64ef-50fc-4156-adc6-b99383506db9	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_realm-admin}	realm-admin	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
e2e8e8f2-2a3e-480c-ac58-8ebd51f8af57	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_create-client}	create-client	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
cb268d6b-b701-4927-a530-f89cbbf47215	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_view-realm}	view-realm	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
e1c9a6b8-d11f-4436-be68-365bdfdd957b	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_view-users}	view-users	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
27f5d82d-3dab-4d7a-ab08-d8ed85c30824	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_view-clients}	view-clients	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
41ebacff-73be-4670-ae85-78ced8b6afd8	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_view-events}	view-events	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
4c2bf928-da58-49d5-90a6-58474666cb08	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_view-identity-providers}	view-identity-providers	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
5563c20d-400a-4cc3-a45d-ce27f195dd30	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_view-authorization}	view-authorization	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
49adb33d-1e98-4a3f-9b6a-d5b257a5daa7	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_manage-realm}	manage-realm	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
058b3d84-3c8c-4fa3-b61c-f571cb56e4b7	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_manage-users}	manage-users	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
04ab9a03-661b-4c41-bd1c-5cced6df7500	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_manage-clients}	manage-clients	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
6961e028-828b-49ea-891e-c6e9f75a0297	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_manage-events}	manage-events	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
8bdfab18-5e8c-4b68-9339-d320096bdd56	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_manage-identity-providers}	manage-identity-providers	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
4dbdfe9b-3425-4ed8-a4f4-96b0fb9289bc	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_manage-authorization}	manage-authorization	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
ca2e1570-3934-4aff-9a97-d1c48a923a61	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_query-users}	query-users	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
0de47d04-74c1-48c6-a85a-19ccce0f1a6a	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_query-clients}	query-clients	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
ba74d9fe-3f82-4f80-a873-42abf8a40744	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_query-realms}	query-realms	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
aad16b27-5c6a-4247-bdbd-1100d1fface4	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_query-groups}	query-groups	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
117ab336-0aa0-4fdb-8db2-15c0b67d3bbc	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_view-profile}	view-profile	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
27e136f9-a685-4177-b79e-807e18b2492f	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_manage-account}	manage-account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
a3f03a99-f589-4913-b158-8a801467bafb	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_manage-account-links}	manage-account-links	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
d7c421e7-748d-4a56-a8db-5c154dff72ed	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_view-applications}	view-applications	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
ec604650-af44-4bd8-a32c-339d6763730c	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_view-consent}	view-consent	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
6dcaff71-88ae-4bbc-8bd9-5cf176441193	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_manage-consent}	manage-consent	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
b4238827-06c4-4efc-9973-cbc334904655	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_view-groups}	view-groups	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
f36fd713-0deb-41bd-971f-eed1dbbbcc8d	500b5c86-ba2e-4345-8602-4e8576a82347	t	${role_delete-account}	delete-account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	500b5c86-ba2e-4345-8602-4e8576a82347	\N
385b53da-c3ee-4547-ae25-46c6e8164ba9	2970b512-2182-4062-9dfe-7299580cf689	t	${role_impersonation}	impersonation	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
95ca83ff-244f-4a20-922f-d095d9a88c59	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_impersonation}	impersonation	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
6aa6dd0a-80d1-46eb-b540-39fc79878d7f	3fc86730-d04c-4cc7-af16-13a708999082	t	${role_read-token}	read-token	2c411af7-e0b7-4547-b08a-27c7c8c1722c	3fc86730-d04c-4cc7-af16-13a708999082	\N
6c041705-4c82-43a4-b844-5cd1b40ce642	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	${role_offline-access}	offline_access	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N	\N
ac5788ea-c550-4a03-acdb-21993c60ee2d	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	${role_uma_authorization}	uma_authorization	2c411af7-e0b7-4547-b08a-27c7c8c1722c	\N	\N
e8f3dec7-6a74-4840-8ab9-4b23eacabd27	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	t	\N	uma_protection	2c411af7-e0b7-4547-b08a-27c7c8c1722c	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	\N
2357d745-9305-48cf-ac68-a18454b2631d	44f1605b-be38-4157-ab34-194b13dc41c6	t	${role_publish-events}	publish-events	eacf1fae-7916-43d5-b7e0-7abf35df7d49	44f1605b-be38-4157-ab34-194b13dc41c6	\N
e9e29590-cf74-4652-bb95-304bdb502090	2970b512-2182-4062-9dfe-7299580cf689	t	${role_publish-events}	publish-events	eacf1fae-7916-43d5-b7e0-7abf35df7d49	2970b512-2182-4062-9dfe-7299580cf689	\N
6a297c21-af87-43ec-8a28-86f9215439aa	de442f71-6200-4f81-918d-da9fdeea6e9b	t	${role_publish-events}	publish-events	2c411af7-e0b7-4547-b08a-27c7c8c1722c	de442f71-6200-4f81-918d-da9fdeea6e9b	\N
\.


--
-- Data for Name: migration_model; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.migration_model (id, version, update_time) FROM stdin;
cljd1	26.1.5	1770584536
\.


--
-- Data for Name: offline_client_session; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.offline_client_session (user_session_id, client_id, offline_flag, "timestamp", data, client_storage_provider, external_client_id, version) FROM stdin;
4926fa42-8cbc-44ac-ab52-08efe95dea02	15735a86-4946-440b-9251-0e8487f6eb01	0	1771829250	{"authMethod":"openid-connect","redirectUri":"https://10.3.12.148:5173/profile?section=settings","notes":{"clientId":"15735a86-4946-440b-9251-0e8487f6eb01","iss":"http://10.3.12.234:8080/realms/tskhra","startedAt":"1771827892","response_type":"code","level-of-authentication":"-1","code_challenge_method":"S256","nonce":"2c7f0444-aba0-4a24-9cdb-af7fee568042","response_mode":"fragment","scope":"openid","userSessionStartedAt":"1771827892","redirect_uri":"https://10.3.12.148:5173/profile?section=settings","state":"93bfc2ab-7d21-4406-b810-7a0594ed326b","code_challenge":"XB6qt9FkgpRj-tYAiGNfVbPv_2aG9iHHKMQLkv2ndvY","prompt":"none","SSO_AUTH":"true","refreshTokenPrefixcd12100f-cb79-4137-bb01-6889eede1d7f":"df27e295-6cbe-43bd-8ce5-f9c4d69625b5","refreshTokenUsePrefixcd12100f-cb79-4137-bb01-6889eede1d7f":"1","refreshTokenLastRefreshPrefixcd12100f-cb79-4137-bb01-6889eede1d7f":"1771828962"}}	local	local	10
0a89b6c4-83d0-47aa-8f22-362d1fae9b41	15735a86-4946-440b-9251-0e8487f6eb01	0	1771830221	{"authMethod":"openid-connect","redirectUri":"https://10.3.13.35:5173/","notes":{"clientId":"15735a86-4946-440b-9251-0e8487f6eb01","iss":"http://10.3.12.234:8080/realms/tskhra","startedAt":"1771830220","response_type":"code","level-of-authentication":"-1","code_challenge_method":"S256","nonce":"c276a327-3a7e-46fb-8ac5-601ce01445f7","response_mode":"fragment","login_hint":"anano","scope":"openid","userSessionStartedAt":"1771830220","redirect_uri":"https://10.3.13.35:5173/","state":"47ee1d4c-6cdc-4c9c-9ff7-35f4f7bb464c","code_challenge":"JiO1XsfW3gX0Qww1N-bgoZH7_dTIr9fvf8iKIBXaUgQ"}}	local	local	1
\.


--
-- Data for Name: offline_user_session; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.offline_user_session (user_session_id, user_id, realm_id, created_on, offline_flag, data, last_session_refresh, broker_session_id, version) FROM stdin;
4926fa42-8cbc-44ac-ab52-08efe95dea02	82717555-0804-479f-b099-1e797e52ef26	2c411af7-e0b7-4547-b08a-27c7c8c1722c	1771827892	0	{"ipAddress":"10.3.12.148","authMethod":"openid-connect","rememberMe":false,"started":0,"notes":{"KC_DEVICE_NOTE":"eyJpcEFkZHJlc3MiOiIxMC4zLjEyLjE0OCIsIm9zIjoiV2luZG93cyIsIm9zVmVyc2lvbiI6IjEwIiwiYnJvd3NlciI6IkNocm9tZS8xNDUuMC4wIiwiZGV2aWNlIjoiT3RoZXIiLCJsYXN0QWNjZXNzIjowLCJtb2JpbGUiOmZhbHNlfQ==","AUTH_TIME":"1771827892","authenticators-completed":"{\\"579672ce-2364-48dc-a6e1-c961e39ca7ba\\":1771827892,\\"a8a84663-ce45-4dda-a2ab-8eba1e794007\\":1771829250}"},"state":"LOGGED_IN"}	1771829250	\N	10
0a89b6c4-83d0-47aa-8f22-362d1fae9b41	5955cb99-825e-4510-97e1-ed7b260922f4	2c411af7-e0b7-4547-b08a-27c7c8c1722c	1771830220	0	{"ipAddress":"10.3.13.35","authMethod":"openid-connect","rememberMe":false,"started":0,"notes":{"KC_DEVICE_NOTE":"eyJpcEFkZHJlc3MiOiIxMC4zLjEzLjM1Iiwib3MiOiJXaW5kb3dzIiwib3NWZXJzaW9uIjoiMTAiLCJicm93c2VyIjoiQ2hyb21lLzE0NS4wLjAiLCJkZXZpY2UiOiJPdGhlciIsImxhc3RBY2Nlc3MiOjAsIm1vYmlsZSI6ZmFsc2V9","AUTH_TIME":"1771830220"},"state":"LOGGED_IN"}	1771830221	\N	1
\.


--
-- Data for Name: org; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.org (id, enabled, realm_id, group_id, name, description, alias, redirect_url) FROM stdin;
\.


--
-- Data for Name: org_domain; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.org_domain (id, name, verified, org_id) FROM stdin;
\.


--
-- Data for Name: policy_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.policy_config (policy_id, name, value) FROM stdin;
c4f8dde2-c2ad-4809-b5a2-d0516c18ad41	code	// by default, grants any permission associated with this policy\n$evaluation.grant();\n
3064dc90-e62f-4046-b113-e974414ae787	defaultResourceType	urn:user-service:resources:default
\.


--
-- Data for Name: protocol_mapper; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.protocol_mapper (id, name, protocol, protocol_mapper_name, client_id, client_scope_id) FROM stdin;
c6403e00-1830-4c02-a527-0d7b1553dc20	audience resolve	openid-connect	oidc-audience-resolve-mapper	884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	\N
d4058027-1532-475f-8731-c5dc0e5969e1	locale	openid-connect	oidc-usermodel-attribute-mapper	d2c6e8c7-59ae-4b82-96e6-e68e1475b141	\N
1636bf03-9443-4d09-8aa4-42c6669bbeee	role list	saml	saml-role-list-mapper	\N	f992b9ed-1c4b-47fd-83e1-c26c3e795a4b
b6e3f7bd-6e8c-4b7f-9ad5-fbd75d265e7e	organization	saml	saml-organization-membership-mapper	\N	d8720c55-a547-4bdc-9b07-06404c8c1a30
e205bde7-359d-4d18-9903-765b49094222	full name	openid-connect	oidc-full-name-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	family name	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
24ec04c8-5697-4f40-8379-d84dcdebbe1e	given name	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
0fed6f6c-56df-4319-93c0-5b5d869f26a6	middle name	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	nickname	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
25299b58-3862-4ea7-b081-30b5304537fa	username	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
e42df259-ce13-4b49-bd72-2a3708cef8c1	profile	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	picture	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
e5aef8f9-a04c-452f-8c52-d648bc581251	website	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	gender	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
3f1c9a70-048a-4071-adbb-99e48987aff5	birthdate	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
ce0ed821-56a6-428d-8016-813b628f2a39	zoneinfo	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	locale	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
78aa3b0b-21a9-44ea-8175-668d6eded1b6	updated at	openid-connect	oidc-usermodel-attribute-mapper	\N	eab4d0d4-3184-468f-bb10-5b82c5762e97
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	email	openid-connect	oidc-usermodel-attribute-mapper	\N	264770a9-8682-4235-83cf-2e12d59fd9ac
a93f991a-3608-45d9-85b9-138b481be89f	email verified	openid-connect	oidc-usermodel-property-mapper	\N	264770a9-8682-4235-83cf-2e12d59fd9ac
428e009f-2185-4c9f-beeb-314425ae32fc	address	openid-connect	oidc-address-mapper	\N	dc32533a-1e41-47f9-b737-3b644b5713fa
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	phone number	openid-connect	oidc-usermodel-attribute-mapper	\N	b0f472dd-8acb-45cc-9e6b-97efe9536cb0
b340f4de-847e-42d0-abda-ee0aa5d412e0	phone number verified	openid-connect	oidc-usermodel-attribute-mapper	\N	b0f472dd-8acb-45cc-9e6b-97efe9536cb0
bbbb7992-4c26-4952-baa9-109999f138be	realm roles	openid-connect	oidc-usermodel-realm-role-mapper	\N	5af152b0-b6d4-47eb-91d6-bd8589de25b8
72b16897-ba40-4200-b357-4e45bc3e013c	client roles	openid-connect	oidc-usermodel-client-role-mapper	\N	5af152b0-b6d4-47eb-91d6-bd8589de25b8
7ed0a952-766a-41a1-9bc3-f3e8f8a2ae0a	audience resolve	openid-connect	oidc-audience-resolve-mapper	\N	5af152b0-b6d4-47eb-91d6-bd8589de25b8
489b64b0-32d5-46ee-8d1a-b2c1482f58a4	allowed web origins	openid-connect	oidc-allowed-origins-mapper	\N	42cc9b6b-5715-4721-bd05-47c7507840f1
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	upn	openid-connect	oidc-usermodel-attribute-mapper	\N	e3c878a1-9bec-4f37-a5e0-84f3561e9d65
2fafbda3-bf56-4adb-8cc6-3019ee83be32	groups	openid-connect	oidc-usermodel-realm-role-mapper	\N	e3c878a1-9bec-4f37-a5e0-84f3561e9d65
02c35bd2-23b5-43d6-95c3-bee030dbdb5b	acr loa level	openid-connect	oidc-acr-mapper	\N	e7f9379d-5bc0-481c-abc5-f1f8026fdd34
b78a35f4-bfbe-4f7c-abdd-ef179113c666	auth_time	openid-connect	oidc-usersessionmodel-note-mapper	\N	a3b9f256-1ff5-4108-be26-5da60bfc3877
d4c47b53-8127-4fda-b1a4-b1ced1979c16	sub	openid-connect	oidc-sub-mapper	\N	a3b9f256-1ff5-4108-be26-5da60bfc3877
ce235477-336e-4cfe-9781-eefaa25553d5	Client ID	openid-connect	oidc-usersessionmodel-note-mapper	\N	9f0556fd-b362-47de-a330-b4219cf3c2a3
7ae4ffca-c477-41a2-9175-fecf808b6bcc	Client Host	openid-connect	oidc-usersessionmodel-note-mapper	\N	9f0556fd-b362-47de-a330-b4219cf3c2a3
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	Client IP Address	openid-connect	oidc-usersessionmodel-note-mapper	\N	9f0556fd-b362-47de-a330-b4219cf3c2a3
290a7465-2860-498b-a2a8-62f23acf3324	organization	openid-connect	oidc-organization-membership-mapper	\N	75d7722d-3d5f-4a21-9ba0-5ab3d2a17948
182ad1f5-4764-469f-be4b-667031f38543	audience resolve	openid-connect	oidc-audience-resolve-mapper	2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	\N
f96e27f4-82b9-41b5-9ecf-259017eb73ef	role list	saml	saml-role-list-mapper	\N	617e9e7c-c22d-468e-a3ae-86385181237d
b7fb2a6f-c687-4a70-aa07-87d795aef3bd	organization	saml	saml-organization-membership-mapper	\N	e2261f11-2475-4538-bc0e-f663a4131459
8df4041e-47ea-48df-97c3-e884122dbc05	full name	openid-connect	oidc-full-name-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
05344cd0-bc17-4781-ae3f-2949fd10f3e5	family name	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	given name	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
7858a393-6822-4568-85bc-b70477ea3b05	middle name	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
9c2bca7c-764c-4bed-aa40-d52f805bed86	nickname	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
8ce195cb-9b9e-418a-b95b-a18013fc8625	username	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
0984499c-9b3c-4c8d-bdb7-2fd19320b378	profile	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
1c91179b-2b85-4602-81fc-2edf1fc5972c	picture	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	website	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
e9424352-e28e-4ef5-aae5-4616715c92eb	gender	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
61f73752-771f-4e99-9356-364f08b07556	birthdate	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
2b40de72-0e36-414d-b34d-f11a5bca36e4	zoneinfo	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
eeb45841-af41-4010-839b-acecd095720a	locale	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
d16cc909-0fbf-43c7-af69-92ea201a9f37	updated at	openid-connect	oidc-usermodel-attribute-mapper	\N	a3d9b5bb-e717-4518-adbc-07bc0f692d64
72155716-1d06-4d29-821f-54941943412f	email	openid-connect	oidc-usermodel-attribute-mapper	\N	cd5bc29d-1eae-4363-b403-3cd338a2653f
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	email verified	openid-connect	oidc-usermodel-property-mapper	\N	cd5bc29d-1eae-4363-b403-3cd338a2653f
e4d394df-1ee5-4fb7-82a9-8716b42be13a	address	openid-connect	oidc-address-mapper	\N	1aa1a3d0-d37d-4043-9c61-219994890dbe
38228d0b-0ab7-41ef-9683-21302be03dbf	phone number	openid-connect	oidc-usermodel-attribute-mapper	\N	3471014d-13bf-4c91-82fe-e145e45ce62c
50a77ac4-c30e-4ab9-9613-40cb64e4211d	phone number verified	openid-connect	oidc-usermodel-attribute-mapper	\N	3471014d-13bf-4c91-82fe-e145e45ce62c
bcbc9d23-2004-42f3-87d1-5531112a176c	realm roles	openid-connect	oidc-usermodel-realm-role-mapper	\N	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38
99395d82-f56e-4dfd-bbbf-869ccd963fce	client roles	openid-connect	oidc-usermodel-client-role-mapper	\N	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38
3e9b9148-4230-4cde-a40c-56e7b660fbc3	audience resolve	openid-connect	oidc-audience-resolve-mapper	\N	0c80e448-13c4-4cdd-9e32-4c5bde4a7a38
3f55c6be-3147-4f71-ba6c-c295830cf165	allowed web origins	openid-connect	oidc-allowed-origins-mapper	\N	44d90b70-00c8-485c-a91a-f77e616baf36
e171d2a0-2649-4b2a-b3e9-3e796783f69a	upn	openid-connect	oidc-usermodel-attribute-mapper	\N	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912
27d654c6-a67b-452e-b170-9d599c2e72b8	groups	openid-connect	oidc-usermodel-realm-role-mapper	\N	3bf0b9fa-e6ac-469a-b3ee-cd679ec1e912
96db2404-dddd-4536-b6bf-c60518282625	acr loa level	openid-connect	oidc-acr-mapper	\N	74f581d3-8e6c-4ffc-aa96-5780938ff437
cb54c7fb-41ed-4de4-bc49-b5a79a259073	auth_time	openid-connect	oidc-usersessionmodel-note-mapper	\N	30a49f27-9f43-47ee-8a2a-91143cd0a6c4
1689645d-aa17-4604-9b62-d0b2277e8d92	sub	openid-connect	oidc-sub-mapper	\N	30a49f27-9f43-47ee-8a2a-91143cd0a6c4
4474c9d2-9f39-4f79-8601-e5ee23f6745a	Client ID	openid-connect	oidc-usersessionmodel-note-mapper	\N	c46725a6-3bab-4231-afdb-b5d8ad4d9302
7887a57b-f2ad-4647-a90c-63f3bed8866a	Client Host	openid-connect	oidc-usersessionmodel-note-mapper	\N	c46725a6-3bab-4231-afdb-b5d8ad4d9302
63f6c7bf-1450-4822-ae05-2134aca2e822	Client IP Address	openid-connect	oidc-usersessionmodel-note-mapper	\N	c46725a6-3bab-4231-afdb-b5d8ad4d9302
89f89b5a-124b-4d97-8ec2-75657eeddda9	organization	openid-connect	oidc-organization-membership-mapper	\N	b8df8620-7249-4102-a288-c70ca38e4eac
585b56fb-cb34-4545-be4f-abdd969efa04	locale	openid-connect	oidc-usermodel-attribute-mapper	7f207e63-5406-447c-9a3b-97cdddc5e07a	\N
\.


--
-- Data for Name: protocol_mapper_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.protocol_mapper_config (protocol_mapper_id, value, name) FROM stdin;
d4058027-1532-475f-8731-c5dc0e5969e1	true	introspection.token.claim
d4058027-1532-475f-8731-c5dc0e5969e1	true	userinfo.token.claim
d4058027-1532-475f-8731-c5dc0e5969e1	locale	user.attribute
d4058027-1532-475f-8731-c5dc0e5969e1	true	id.token.claim
d4058027-1532-475f-8731-c5dc0e5969e1	true	access.token.claim
d4058027-1532-475f-8731-c5dc0e5969e1	locale	claim.name
d4058027-1532-475f-8731-c5dc0e5969e1	String	jsonType.label
1636bf03-9443-4d09-8aa4-42c6669bbeee	false	single
1636bf03-9443-4d09-8aa4-42c6669bbeee	Basic	attribute.nameformat
1636bf03-9443-4d09-8aa4-42c6669bbeee	Role	attribute.name
0fed6f6c-56df-4319-93c0-5b5d869f26a6	true	introspection.token.claim
0fed6f6c-56df-4319-93c0-5b5d869f26a6	true	userinfo.token.claim
0fed6f6c-56df-4319-93c0-5b5d869f26a6	middleName	user.attribute
0fed6f6c-56df-4319-93c0-5b5d869f26a6	true	id.token.claim
0fed6f6c-56df-4319-93c0-5b5d869f26a6	true	access.token.claim
0fed6f6c-56df-4319-93c0-5b5d869f26a6	middle_name	claim.name
0fed6f6c-56df-4319-93c0-5b5d869f26a6	String	jsonType.label
24ec04c8-5697-4f40-8379-d84dcdebbe1e	true	introspection.token.claim
24ec04c8-5697-4f40-8379-d84dcdebbe1e	true	userinfo.token.claim
24ec04c8-5697-4f40-8379-d84dcdebbe1e	firstName	user.attribute
24ec04c8-5697-4f40-8379-d84dcdebbe1e	true	id.token.claim
24ec04c8-5697-4f40-8379-d84dcdebbe1e	true	access.token.claim
24ec04c8-5697-4f40-8379-d84dcdebbe1e	given_name	claim.name
24ec04c8-5697-4f40-8379-d84dcdebbe1e	String	jsonType.label
25299b58-3862-4ea7-b081-30b5304537fa	true	introspection.token.claim
25299b58-3862-4ea7-b081-30b5304537fa	true	userinfo.token.claim
25299b58-3862-4ea7-b081-30b5304537fa	username	user.attribute
25299b58-3862-4ea7-b081-30b5304537fa	true	id.token.claim
25299b58-3862-4ea7-b081-30b5304537fa	true	access.token.claim
25299b58-3862-4ea7-b081-30b5304537fa	preferred_username	claim.name
25299b58-3862-4ea7-b081-30b5304537fa	String	jsonType.label
3f1c9a70-048a-4071-adbb-99e48987aff5	true	introspection.token.claim
3f1c9a70-048a-4071-adbb-99e48987aff5	true	userinfo.token.claim
3f1c9a70-048a-4071-adbb-99e48987aff5	birthdate	user.attribute
3f1c9a70-048a-4071-adbb-99e48987aff5	true	id.token.claim
3f1c9a70-048a-4071-adbb-99e48987aff5	true	access.token.claim
3f1c9a70-048a-4071-adbb-99e48987aff5	birthdate	claim.name
3f1c9a70-048a-4071-adbb-99e48987aff5	String	jsonType.label
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	true	introspection.token.claim
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	true	userinfo.token.claim
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	nickname	user.attribute
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	true	id.token.claim
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	true	access.token.claim
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	nickname	claim.name
62a3f51d-bf72-4064-bc95-4a9c4ad9b2ef	String	jsonType.label
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	true	introspection.token.claim
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	true	userinfo.token.claim
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	locale	user.attribute
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	true	id.token.claim
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	true	access.token.claim
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	locale	claim.name
642cf0ab-4d47-46c8-95e1-55f14ef0a99b	String	jsonType.label
78aa3b0b-21a9-44ea-8175-668d6eded1b6	true	introspection.token.claim
78aa3b0b-21a9-44ea-8175-668d6eded1b6	true	userinfo.token.claim
78aa3b0b-21a9-44ea-8175-668d6eded1b6	updatedAt	user.attribute
78aa3b0b-21a9-44ea-8175-668d6eded1b6	true	id.token.claim
78aa3b0b-21a9-44ea-8175-668d6eded1b6	true	access.token.claim
78aa3b0b-21a9-44ea-8175-668d6eded1b6	updated_at	claim.name
78aa3b0b-21a9-44ea-8175-668d6eded1b6	long	jsonType.label
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	true	introspection.token.claim
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	true	userinfo.token.claim
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	picture	user.attribute
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	true	id.token.claim
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	true	access.token.claim
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	picture	claim.name
98d4a57e-e1dd-4207-bcc0-25986f67dcf8	String	jsonType.label
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	true	introspection.token.claim
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	true	userinfo.token.claim
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	lastName	user.attribute
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	true	id.token.claim
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	true	access.token.claim
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	family_name	claim.name
aa37b57b-05eb-41a1-bab3-12c5e3c4d04b	String	jsonType.label
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	true	introspection.token.claim
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	true	userinfo.token.claim
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	gender	user.attribute
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	true	id.token.claim
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	true	access.token.claim
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	gender	claim.name
be83412f-9f2b-4c23-bf72-cd3ff1d88d12	String	jsonType.label
ce0ed821-56a6-428d-8016-813b628f2a39	true	introspection.token.claim
ce0ed821-56a6-428d-8016-813b628f2a39	true	userinfo.token.claim
ce0ed821-56a6-428d-8016-813b628f2a39	zoneinfo	user.attribute
ce0ed821-56a6-428d-8016-813b628f2a39	true	id.token.claim
ce0ed821-56a6-428d-8016-813b628f2a39	true	access.token.claim
ce0ed821-56a6-428d-8016-813b628f2a39	zoneinfo	claim.name
ce0ed821-56a6-428d-8016-813b628f2a39	String	jsonType.label
e205bde7-359d-4d18-9903-765b49094222	true	introspection.token.claim
e205bde7-359d-4d18-9903-765b49094222	true	userinfo.token.claim
e205bde7-359d-4d18-9903-765b49094222	true	id.token.claim
e205bde7-359d-4d18-9903-765b49094222	true	access.token.claim
e42df259-ce13-4b49-bd72-2a3708cef8c1	true	introspection.token.claim
e42df259-ce13-4b49-bd72-2a3708cef8c1	true	userinfo.token.claim
e42df259-ce13-4b49-bd72-2a3708cef8c1	profile	user.attribute
e42df259-ce13-4b49-bd72-2a3708cef8c1	true	id.token.claim
e42df259-ce13-4b49-bd72-2a3708cef8c1	true	access.token.claim
e42df259-ce13-4b49-bd72-2a3708cef8c1	profile	claim.name
e42df259-ce13-4b49-bd72-2a3708cef8c1	String	jsonType.label
e5aef8f9-a04c-452f-8c52-d648bc581251	true	introspection.token.claim
e5aef8f9-a04c-452f-8c52-d648bc581251	true	userinfo.token.claim
e5aef8f9-a04c-452f-8c52-d648bc581251	website	user.attribute
e5aef8f9-a04c-452f-8c52-d648bc581251	true	id.token.claim
e5aef8f9-a04c-452f-8c52-d648bc581251	true	access.token.claim
e5aef8f9-a04c-452f-8c52-d648bc581251	website	claim.name
e5aef8f9-a04c-452f-8c52-d648bc581251	String	jsonType.label
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	true	introspection.token.claim
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	true	userinfo.token.claim
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	email	user.attribute
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	true	id.token.claim
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	true	access.token.claim
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	email	claim.name
59ad983b-c37f-4d3e-9358-6bd7d0b8366e	String	jsonType.label
a93f991a-3608-45d9-85b9-138b481be89f	true	introspection.token.claim
a93f991a-3608-45d9-85b9-138b481be89f	true	userinfo.token.claim
a93f991a-3608-45d9-85b9-138b481be89f	emailVerified	user.attribute
a93f991a-3608-45d9-85b9-138b481be89f	true	id.token.claim
a93f991a-3608-45d9-85b9-138b481be89f	true	access.token.claim
a93f991a-3608-45d9-85b9-138b481be89f	email_verified	claim.name
a93f991a-3608-45d9-85b9-138b481be89f	boolean	jsonType.label
428e009f-2185-4c9f-beeb-314425ae32fc	formatted	user.attribute.formatted
428e009f-2185-4c9f-beeb-314425ae32fc	country	user.attribute.country
428e009f-2185-4c9f-beeb-314425ae32fc	true	introspection.token.claim
428e009f-2185-4c9f-beeb-314425ae32fc	postal_code	user.attribute.postal_code
428e009f-2185-4c9f-beeb-314425ae32fc	true	userinfo.token.claim
428e009f-2185-4c9f-beeb-314425ae32fc	street	user.attribute.street
428e009f-2185-4c9f-beeb-314425ae32fc	true	id.token.claim
428e009f-2185-4c9f-beeb-314425ae32fc	region	user.attribute.region
428e009f-2185-4c9f-beeb-314425ae32fc	true	access.token.claim
428e009f-2185-4c9f-beeb-314425ae32fc	locality	user.attribute.locality
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	true	introspection.token.claim
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	true	userinfo.token.claim
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	phoneNumber	user.attribute
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	true	id.token.claim
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	true	access.token.claim
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	phone_number	claim.name
8fdf17ac-1dbc-44c8-a060-10ec0ed72bda	String	jsonType.label
b340f4de-847e-42d0-abda-ee0aa5d412e0	true	introspection.token.claim
b340f4de-847e-42d0-abda-ee0aa5d412e0	true	userinfo.token.claim
b340f4de-847e-42d0-abda-ee0aa5d412e0	phoneNumberVerified	user.attribute
b340f4de-847e-42d0-abda-ee0aa5d412e0	true	id.token.claim
b340f4de-847e-42d0-abda-ee0aa5d412e0	true	access.token.claim
b340f4de-847e-42d0-abda-ee0aa5d412e0	phone_number_verified	claim.name
b340f4de-847e-42d0-abda-ee0aa5d412e0	boolean	jsonType.label
72b16897-ba40-4200-b357-4e45bc3e013c	true	introspection.token.claim
72b16897-ba40-4200-b357-4e45bc3e013c	true	multivalued
72b16897-ba40-4200-b357-4e45bc3e013c	foo	user.attribute
72b16897-ba40-4200-b357-4e45bc3e013c	true	access.token.claim
72b16897-ba40-4200-b357-4e45bc3e013c	resource_access.${client_id}.roles	claim.name
72b16897-ba40-4200-b357-4e45bc3e013c	String	jsonType.label
7ed0a952-766a-41a1-9bc3-f3e8f8a2ae0a	true	introspection.token.claim
7ed0a952-766a-41a1-9bc3-f3e8f8a2ae0a	true	access.token.claim
bbbb7992-4c26-4952-baa9-109999f138be	true	introspection.token.claim
bbbb7992-4c26-4952-baa9-109999f138be	true	multivalued
bbbb7992-4c26-4952-baa9-109999f138be	foo	user.attribute
bbbb7992-4c26-4952-baa9-109999f138be	true	access.token.claim
bbbb7992-4c26-4952-baa9-109999f138be	realm_access.roles	claim.name
bbbb7992-4c26-4952-baa9-109999f138be	String	jsonType.label
489b64b0-32d5-46ee-8d1a-b2c1482f58a4	true	introspection.token.claim
489b64b0-32d5-46ee-8d1a-b2c1482f58a4	true	access.token.claim
2fafbda3-bf56-4adb-8cc6-3019ee83be32	true	introspection.token.claim
2fafbda3-bf56-4adb-8cc6-3019ee83be32	true	multivalued
2fafbda3-bf56-4adb-8cc6-3019ee83be32	foo	user.attribute
2fafbda3-bf56-4adb-8cc6-3019ee83be32	true	id.token.claim
2fafbda3-bf56-4adb-8cc6-3019ee83be32	true	access.token.claim
2fafbda3-bf56-4adb-8cc6-3019ee83be32	groups	claim.name
2fafbda3-bf56-4adb-8cc6-3019ee83be32	String	jsonType.label
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	true	introspection.token.claim
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	true	userinfo.token.claim
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	username	user.attribute
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	true	id.token.claim
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	true	access.token.claim
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	upn	claim.name
9f9f18f8-1e31-4fa6-a3b0-e4042c5eb24d	String	jsonType.label
02c35bd2-23b5-43d6-95c3-bee030dbdb5b	true	introspection.token.claim
02c35bd2-23b5-43d6-95c3-bee030dbdb5b	true	id.token.claim
02c35bd2-23b5-43d6-95c3-bee030dbdb5b	true	access.token.claim
b78a35f4-bfbe-4f7c-abdd-ef179113c666	AUTH_TIME	user.session.note
b78a35f4-bfbe-4f7c-abdd-ef179113c666	true	introspection.token.claim
b78a35f4-bfbe-4f7c-abdd-ef179113c666	true	id.token.claim
b78a35f4-bfbe-4f7c-abdd-ef179113c666	true	access.token.claim
b78a35f4-bfbe-4f7c-abdd-ef179113c666	auth_time	claim.name
b78a35f4-bfbe-4f7c-abdd-ef179113c666	long	jsonType.label
d4c47b53-8127-4fda-b1a4-b1ced1979c16	true	introspection.token.claim
d4c47b53-8127-4fda-b1a4-b1ced1979c16	true	access.token.claim
7ae4ffca-c477-41a2-9175-fecf808b6bcc	clientHost	user.session.note
7ae4ffca-c477-41a2-9175-fecf808b6bcc	true	introspection.token.claim
7ae4ffca-c477-41a2-9175-fecf808b6bcc	true	id.token.claim
7ae4ffca-c477-41a2-9175-fecf808b6bcc	true	access.token.claim
7ae4ffca-c477-41a2-9175-fecf808b6bcc	clientHost	claim.name
7ae4ffca-c477-41a2-9175-fecf808b6bcc	String	jsonType.label
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	clientAddress	user.session.note
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	true	introspection.token.claim
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	true	id.token.claim
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	true	access.token.claim
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	clientAddress	claim.name
ce0ed6d4-acd2-47da-8fa0-2b949d5829d4	String	jsonType.label
ce235477-336e-4cfe-9781-eefaa25553d5	client_id	user.session.note
ce235477-336e-4cfe-9781-eefaa25553d5	true	introspection.token.claim
ce235477-336e-4cfe-9781-eefaa25553d5	true	id.token.claim
ce235477-336e-4cfe-9781-eefaa25553d5	true	access.token.claim
ce235477-336e-4cfe-9781-eefaa25553d5	client_id	claim.name
ce235477-336e-4cfe-9781-eefaa25553d5	String	jsonType.label
290a7465-2860-498b-a2a8-62f23acf3324	true	introspection.token.claim
290a7465-2860-498b-a2a8-62f23acf3324	true	multivalued
290a7465-2860-498b-a2a8-62f23acf3324	true	id.token.claim
290a7465-2860-498b-a2a8-62f23acf3324	true	access.token.claim
290a7465-2860-498b-a2a8-62f23acf3324	organization	claim.name
290a7465-2860-498b-a2a8-62f23acf3324	String	jsonType.label
f96e27f4-82b9-41b5-9ecf-259017eb73ef	false	single
f96e27f4-82b9-41b5-9ecf-259017eb73ef	Basic	attribute.nameformat
f96e27f4-82b9-41b5-9ecf-259017eb73ef	Role	attribute.name
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	true	introspection.token.claim
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	true	userinfo.token.claim
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	firstName	user.attribute
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	true	id.token.claim
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	true	access.token.claim
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	given_name	claim.name
02aee1a8-eaf1-4289-a3e1-8dd0d2a987da	String	jsonType.label
05344cd0-bc17-4781-ae3f-2949fd10f3e5	true	introspection.token.claim
05344cd0-bc17-4781-ae3f-2949fd10f3e5	true	userinfo.token.claim
05344cd0-bc17-4781-ae3f-2949fd10f3e5	lastName	user.attribute
05344cd0-bc17-4781-ae3f-2949fd10f3e5	true	id.token.claim
05344cd0-bc17-4781-ae3f-2949fd10f3e5	true	access.token.claim
05344cd0-bc17-4781-ae3f-2949fd10f3e5	family_name	claim.name
05344cd0-bc17-4781-ae3f-2949fd10f3e5	String	jsonType.label
0984499c-9b3c-4c8d-bdb7-2fd19320b378	true	introspection.token.claim
0984499c-9b3c-4c8d-bdb7-2fd19320b378	true	userinfo.token.claim
0984499c-9b3c-4c8d-bdb7-2fd19320b378	profile	user.attribute
0984499c-9b3c-4c8d-bdb7-2fd19320b378	true	id.token.claim
0984499c-9b3c-4c8d-bdb7-2fd19320b378	true	access.token.claim
0984499c-9b3c-4c8d-bdb7-2fd19320b378	profile	claim.name
0984499c-9b3c-4c8d-bdb7-2fd19320b378	String	jsonType.label
1c91179b-2b85-4602-81fc-2edf1fc5972c	true	introspection.token.claim
1c91179b-2b85-4602-81fc-2edf1fc5972c	true	userinfo.token.claim
1c91179b-2b85-4602-81fc-2edf1fc5972c	picture	user.attribute
1c91179b-2b85-4602-81fc-2edf1fc5972c	true	id.token.claim
1c91179b-2b85-4602-81fc-2edf1fc5972c	true	access.token.claim
1c91179b-2b85-4602-81fc-2edf1fc5972c	picture	claim.name
1c91179b-2b85-4602-81fc-2edf1fc5972c	String	jsonType.label
2b40de72-0e36-414d-b34d-f11a5bca36e4	true	introspection.token.claim
2b40de72-0e36-414d-b34d-f11a5bca36e4	true	userinfo.token.claim
2b40de72-0e36-414d-b34d-f11a5bca36e4	zoneinfo	user.attribute
2b40de72-0e36-414d-b34d-f11a5bca36e4	true	id.token.claim
2b40de72-0e36-414d-b34d-f11a5bca36e4	true	access.token.claim
2b40de72-0e36-414d-b34d-f11a5bca36e4	zoneinfo	claim.name
2b40de72-0e36-414d-b34d-f11a5bca36e4	String	jsonType.label
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	true	introspection.token.claim
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	true	userinfo.token.claim
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	website	user.attribute
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	true	id.token.claim
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	true	access.token.claim
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	website	claim.name
42295f8e-31b2-45e6-8c35-fdccb4c2ca17	String	jsonType.label
61f73752-771f-4e99-9356-364f08b07556	true	introspection.token.claim
61f73752-771f-4e99-9356-364f08b07556	true	userinfo.token.claim
61f73752-771f-4e99-9356-364f08b07556	birthdate	user.attribute
61f73752-771f-4e99-9356-364f08b07556	true	id.token.claim
61f73752-771f-4e99-9356-364f08b07556	true	access.token.claim
61f73752-771f-4e99-9356-364f08b07556	birthdate	claim.name
61f73752-771f-4e99-9356-364f08b07556	String	jsonType.label
7858a393-6822-4568-85bc-b70477ea3b05	true	introspection.token.claim
7858a393-6822-4568-85bc-b70477ea3b05	true	userinfo.token.claim
7858a393-6822-4568-85bc-b70477ea3b05	middleName	user.attribute
7858a393-6822-4568-85bc-b70477ea3b05	true	id.token.claim
7858a393-6822-4568-85bc-b70477ea3b05	true	access.token.claim
7858a393-6822-4568-85bc-b70477ea3b05	middle_name	claim.name
7858a393-6822-4568-85bc-b70477ea3b05	String	jsonType.label
8ce195cb-9b9e-418a-b95b-a18013fc8625	true	introspection.token.claim
8ce195cb-9b9e-418a-b95b-a18013fc8625	true	userinfo.token.claim
8ce195cb-9b9e-418a-b95b-a18013fc8625	username	user.attribute
8ce195cb-9b9e-418a-b95b-a18013fc8625	true	id.token.claim
8ce195cb-9b9e-418a-b95b-a18013fc8625	true	access.token.claim
8ce195cb-9b9e-418a-b95b-a18013fc8625	preferred_username	claim.name
8ce195cb-9b9e-418a-b95b-a18013fc8625	String	jsonType.label
8df4041e-47ea-48df-97c3-e884122dbc05	true	introspection.token.claim
8df4041e-47ea-48df-97c3-e884122dbc05	true	userinfo.token.claim
8df4041e-47ea-48df-97c3-e884122dbc05	true	id.token.claim
8df4041e-47ea-48df-97c3-e884122dbc05	true	access.token.claim
9c2bca7c-764c-4bed-aa40-d52f805bed86	true	introspection.token.claim
9c2bca7c-764c-4bed-aa40-d52f805bed86	true	userinfo.token.claim
9c2bca7c-764c-4bed-aa40-d52f805bed86	nickname	user.attribute
9c2bca7c-764c-4bed-aa40-d52f805bed86	true	id.token.claim
9c2bca7c-764c-4bed-aa40-d52f805bed86	true	access.token.claim
9c2bca7c-764c-4bed-aa40-d52f805bed86	nickname	claim.name
9c2bca7c-764c-4bed-aa40-d52f805bed86	String	jsonType.label
d16cc909-0fbf-43c7-af69-92ea201a9f37	true	introspection.token.claim
d16cc909-0fbf-43c7-af69-92ea201a9f37	true	userinfo.token.claim
d16cc909-0fbf-43c7-af69-92ea201a9f37	updatedAt	user.attribute
d16cc909-0fbf-43c7-af69-92ea201a9f37	true	id.token.claim
d16cc909-0fbf-43c7-af69-92ea201a9f37	true	access.token.claim
d16cc909-0fbf-43c7-af69-92ea201a9f37	updated_at	claim.name
d16cc909-0fbf-43c7-af69-92ea201a9f37	long	jsonType.label
e9424352-e28e-4ef5-aae5-4616715c92eb	true	introspection.token.claim
e9424352-e28e-4ef5-aae5-4616715c92eb	true	userinfo.token.claim
e9424352-e28e-4ef5-aae5-4616715c92eb	gender	user.attribute
e9424352-e28e-4ef5-aae5-4616715c92eb	true	id.token.claim
e9424352-e28e-4ef5-aae5-4616715c92eb	true	access.token.claim
e9424352-e28e-4ef5-aae5-4616715c92eb	gender	claim.name
e9424352-e28e-4ef5-aae5-4616715c92eb	String	jsonType.label
eeb45841-af41-4010-839b-acecd095720a	true	introspection.token.claim
eeb45841-af41-4010-839b-acecd095720a	true	userinfo.token.claim
eeb45841-af41-4010-839b-acecd095720a	locale	user.attribute
eeb45841-af41-4010-839b-acecd095720a	true	id.token.claim
eeb45841-af41-4010-839b-acecd095720a	true	access.token.claim
eeb45841-af41-4010-839b-acecd095720a	locale	claim.name
eeb45841-af41-4010-839b-acecd095720a	String	jsonType.label
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	true	introspection.token.claim
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	true	userinfo.token.claim
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	emailVerified	user.attribute
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	true	id.token.claim
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	true	access.token.claim
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	email_verified	claim.name
3c5c4b86-13da-45d3-932b-0fc455a8bfc7	boolean	jsonType.label
72155716-1d06-4d29-821f-54941943412f	true	introspection.token.claim
72155716-1d06-4d29-821f-54941943412f	true	userinfo.token.claim
72155716-1d06-4d29-821f-54941943412f	email	user.attribute
72155716-1d06-4d29-821f-54941943412f	true	id.token.claim
72155716-1d06-4d29-821f-54941943412f	true	access.token.claim
72155716-1d06-4d29-821f-54941943412f	email	claim.name
72155716-1d06-4d29-821f-54941943412f	String	jsonType.label
e4d394df-1ee5-4fb7-82a9-8716b42be13a	formatted	user.attribute.formatted
e4d394df-1ee5-4fb7-82a9-8716b42be13a	country	user.attribute.country
e4d394df-1ee5-4fb7-82a9-8716b42be13a	true	introspection.token.claim
e4d394df-1ee5-4fb7-82a9-8716b42be13a	postal_code	user.attribute.postal_code
e4d394df-1ee5-4fb7-82a9-8716b42be13a	true	userinfo.token.claim
e4d394df-1ee5-4fb7-82a9-8716b42be13a	street	user.attribute.street
e4d394df-1ee5-4fb7-82a9-8716b42be13a	true	id.token.claim
e4d394df-1ee5-4fb7-82a9-8716b42be13a	region	user.attribute.region
e4d394df-1ee5-4fb7-82a9-8716b42be13a	true	access.token.claim
e4d394df-1ee5-4fb7-82a9-8716b42be13a	locality	user.attribute.locality
38228d0b-0ab7-41ef-9683-21302be03dbf	true	introspection.token.claim
38228d0b-0ab7-41ef-9683-21302be03dbf	true	userinfo.token.claim
38228d0b-0ab7-41ef-9683-21302be03dbf	phoneNumber	user.attribute
38228d0b-0ab7-41ef-9683-21302be03dbf	true	id.token.claim
38228d0b-0ab7-41ef-9683-21302be03dbf	true	access.token.claim
38228d0b-0ab7-41ef-9683-21302be03dbf	phone_number	claim.name
38228d0b-0ab7-41ef-9683-21302be03dbf	String	jsonType.label
50a77ac4-c30e-4ab9-9613-40cb64e4211d	true	introspection.token.claim
50a77ac4-c30e-4ab9-9613-40cb64e4211d	true	userinfo.token.claim
50a77ac4-c30e-4ab9-9613-40cb64e4211d	phoneNumberVerified	user.attribute
50a77ac4-c30e-4ab9-9613-40cb64e4211d	true	id.token.claim
50a77ac4-c30e-4ab9-9613-40cb64e4211d	true	access.token.claim
50a77ac4-c30e-4ab9-9613-40cb64e4211d	phone_number_verified	claim.name
50a77ac4-c30e-4ab9-9613-40cb64e4211d	boolean	jsonType.label
3e9b9148-4230-4cde-a40c-56e7b660fbc3	true	introspection.token.claim
3e9b9148-4230-4cde-a40c-56e7b660fbc3	true	access.token.claim
99395d82-f56e-4dfd-bbbf-869ccd963fce	true	introspection.token.claim
99395d82-f56e-4dfd-bbbf-869ccd963fce	true	multivalued
99395d82-f56e-4dfd-bbbf-869ccd963fce	foo	user.attribute
99395d82-f56e-4dfd-bbbf-869ccd963fce	true	access.token.claim
99395d82-f56e-4dfd-bbbf-869ccd963fce	resource_access.${client_id}.roles	claim.name
99395d82-f56e-4dfd-bbbf-869ccd963fce	String	jsonType.label
bcbc9d23-2004-42f3-87d1-5531112a176c	true	introspection.token.claim
bcbc9d23-2004-42f3-87d1-5531112a176c	true	multivalued
bcbc9d23-2004-42f3-87d1-5531112a176c	foo	user.attribute
bcbc9d23-2004-42f3-87d1-5531112a176c	true	access.token.claim
bcbc9d23-2004-42f3-87d1-5531112a176c	realm_access.roles	claim.name
bcbc9d23-2004-42f3-87d1-5531112a176c	String	jsonType.label
3f55c6be-3147-4f71-ba6c-c295830cf165	true	introspection.token.claim
3f55c6be-3147-4f71-ba6c-c295830cf165	true	access.token.claim
27d654c6-a67b-452e-b170-9d599c2e72b8	true	introspection.token.claim
27d654c6-a67b-452e-b170-9d599c2e72b8	true	multivalued
27d654c6-a67b-452e-b170-9d599c2e72b8	foo	user.attribute
27d654c6-a67b-452e-b170-9d599c2e72b8	true	id.token.claim
27d654c6-a67b-452e-b170-9d599c2e72b8	true	access.token.claim
27d654c6-a67b-452e-b170-9d599c2e72b8	groups	claim.name
27d654c6-a67b-452e-b170-9d599c2e72b8	String	jsonType.label
e171d2a0-2649-4b2a-b3e9-3e796783f69a	true	introspection.token.claim
e171d2a0-2649-4b2a-b3e9-3e796783f69a	true	userinfo.token.claim
e171d2a0-2649-4b2a-b3e9-3e796783f69a	username	user.attribute
e171d2a0-2649-4b2a-b3e9-3e796783f69a	true	id.token.claim
e171d2a0-2649-4b2a-b3e9-3e796783f69a	true	access.token.claim
e171d2a0-2649-4b2a-b3e9-3e796783f69a	upn	claim.name
e171d2a0-2649-4b2a-b3e9-3e796783f69a	String	jsonType.label
96db2404-dddd-4536-b6bf-c60518282625	true	introspection.token.claim
96db2404-dddd-4536-b6bf-c60518282625	true	id.token.claim
96db2404-dddd-4536-b6bf-c60518282625	true	access.token.claim
1689645d-aa17-4604-9b62-d0b2277e8d92	true	introspection.token.claim
1689645d-aa17-4604-9b62-d0b2277e8d92	true	access.token.claim
cb54c7fb-41ed-4de4-bc49-b5a79a259073	AUTH_TIME	user.session.note
cb54c7fb-41ed-4de4-bc49-b5a79a259073	true	introspection.token.claim
cb54c7fb-41ed-4de4-bc49-b5a79a259073	true	id.token.claim
cb54c7fb-41ed-4de4-bc49-b5a79a259073	true	access.token.claim
cb54c7fb-41ed-4de4-bc49-b5a79a259073	auth_time	claim.name
cb54c7fb-41ed-4de4-bc49-b5a79a259073	long	jsonType.label
4474c9d2-9f39-4f79-8601-e5ee23f6745a	client_id	user.session.note
4474c9d2-9f39-4f79-8601-e5ee23f6745a	true	introspection.token.claim
4474c9d2-9f39-4f79-8601-e5ee23f6745a	true	id.token.claim
4474c9d2-9f39-4f79-8601-e5ee23f6745a	true	access.token.claim
4474c9d2-9f39-4f79-8601-e5ee23f6745a	client_id	claim.name
4474c9d2-9f39-4f79-8601-e5ee23f6745a	String	jsonType.label
63f6c7bf-1450-4822-ae05-2134aca2e822	clientAddress	user.session.note
63f6c7bf-1450-4822-ae05-2134aca2e822	true	introspection.token.claim
63f6c7bf-1450-4822-ae05-2134aca2e822	true	id.token.claim
63f6c7bf-1450-4822-ae05-2134aca2e822	true	access.token.claim
63f6c7bf-1450-4822-ae05-2134aca2e822	clientAddress	claim.name
63f6c7bf-1450-4822-ae05-2134aca2e822	String	jsonType.label
7887a57b-f2ad-4647-a90c-63f3bed8866a	clientHost	user.session.note
7887a57b-f2ad-4647-a90c-63f3bed8866a	true	introspection.token.claim
7887a57b-f2ad-4647-a90c-63f3bed8866a	true	id.token.claim
7887a57b-f2ad-4647-a90c-63f3bed8866a	true	access.token.claim
7887a57b-f2ad-4647-a90c-63f3bed8866a	clientHost	claim.name
7887a57b-f2ad-4647-a90c-63f3bed8866a	String	jsonType.label
89f89b5a-124b-4d97-8ec2-75657eeddda9	true	introspection.token.claim
89f89b5a-124b-4d97-8ec2-75657eeddda9	true	multivalued
89f89b5a-124b-4d97-8ec2-75657eeddda9	true	id.token.claim
89f89b5a-124b-4d97-8ec2-75657eeddda9	true	access.token.claim
89f89b5a-124b-4d97-8ec2-75657eeddda9	organization	claim.name
89f89b5a-124b-4d97-8ec2-75657eeddda9	String	jsonType.label
585b56fb-cb34-4545-be4f-abdd969efa04	true	introspection.token.claim
585b56fb-cb34-4545-be4f-abdd969efa04	true	userinfo.token.claim
585b56fb-cb34-4545-be4f-abdd969efa04	locale	user.attribute
585b56fb-cb34-4545-be4f-abdd969efa04	true	id.token.claim
585b56fb-cb34-4545-be4f-abdd969efa04	true	access.token.claim
585b56fb-cb34-4545-be4f-abdd969efa04	locale	claim.name
585b56fb-cb34-4545-be4f-abdd969efa04	String	jsonType.label
\.


--
-- Data for Name: realm; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm (id, access_code_lifespan, user_action_lifespan, access_token_lifespan, account_theme, admin_theme, email_theme, enabled, events_enabled, events_expiration, login_theme, name, not_before, password_policy, registration_allowed, remember_me, reset_password_allowed, social, ssl_required, sso_idle_timeout, sso_max_lifespan, update_profile_on_soc_login, verify_email, master_admin_client, login_lifespan, internationalization_enabled, default_locale, reg_email_as_username, admin_events_enabled, admin_events_details_enabled, edit_username_allowed, otp_policy_counter, otp_policy_window, otp_policy_period, otp_policy_digits, otp_policy_alg, otp_policy_type, browser_flow, registration_flow, direct_grant_flow, reset_credentials_flow, client_auth_flow, offline_session_idle_timeout, revoke_refresh_token, access_token_life_implicit, login_with_email_allowed, duplicate_emails_allowed, docker_auth_flow, refresh_token_max_reuse, allow_user_managed_access, sso_max_lifespan_remember_me, sso_idle_timeout_remember_me, default_role) FROM stdin;
2c411af7-e0b7-4547-b08a-27c7c8c1722c	60	300	300	keycloak.v3	keycloak.v2	keycloak	t	f	0	tskhra-theme	tskhra	0	length(8) and upperCase(1) and digits(1) and specialChars(1) and lowerCase(1) and regexPattern(^\\S+$)	t	f	t	f	EXTERNAL	1800	36000	f	f	2970b512-2182-4062-9dfe-7299580cf689	1800	f	\N	f	f	f	f	0	1	30	6	HmacSHA1	totp	212cfa8d-af30-400e-b7b3-419fb7619a0b	b67f4795-bf0b-46e8-9d26-9bf816f0c59c	ffd184f2-d0b3-4c23-a802-0c62fb3dc76b	a11ceaf5-2b00-4283-aab9-3599df08b5a3	96f9c24b-2903-4ee1-a32f-a0a1400d56b4	2592000	t	900	t	f	22aca36c-7be2-4cc1-bf2c-2657d297df1b	0	f	0	0	a6fb666e-17a0-4cf9-95c2-820ed013c95b
eacf1fae-7916-43d5-b7e0-7abf35df7d49	60	300	60	\N	\N	\N	t	f	0	\N	master	0	\N	f	f	f	f	EXTERNAL	1800	36000	f	f	44f1605b-be38-4157-ab34-194b13dc41c6	1800	f	\N	f	f	f	f	0	1	30	6	HmacSHA1	totp	0f2d5899-3103-436c-a5bb-2a8ab084c3ef	8403259f-d43a-4f64-be20-385b6b23c6ab	9d8b54ea-18d0-43f6-861d-49dde066e744	eab126c3-628a-42d3-850e-e685b877712e	718bda0f-7a85-4b50-a55d-12b6ac640a44	2592000	f	900	t	f	90e3ef83-27cb-4aa7-9013-7ef775291230	0	f	0	0	b4450810-c34f-4a44-8e5c-dd185fdbef3a
\.


--
-- Data for Name: realm_attribute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_attribute (name, realm_id, value) FROM stdin;
bruteForceProtected	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
permanentLockout	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
maxTemporaryLockouts	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
bruteForceStrategy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	MULTIPLE
maxFailureWaitSeconds	eacf1fae-7916-43d5-b7e0-7abf35df7d49	900
minimumQuickLoginWaitSeconds	eacf1fae-7916-43d5-b7e0-7abf35df7d49	60
waitIncrementSeconds	eacf1fae-7916-43d5-b7e0-7abf35df7d49	60
quickLoginCheckMilliSeconds	eacf1fae-7916-43d5-b7e0-7abf35df7d49	1000
maxDeltaTimeSeconds	eacf1fae-7916-43d5-b7e0-7abf35df7d49	43200
failureFactor	eacf1fae-7916-43d5-b7e0-7abf35df7d49	30
realmReusableOtpCode	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
firstBrokerLoginFlowId	eacf1fae-7916-43d5-b7e0-7abf35df7d49	b982b519-a444-4d10-b939-5ccb89cc296b
displayName	eacf1fae-7916-43d5-b7e0-7abf35df7d49	Keycloak
displayNameHtml	eacf1fae-7916-43d5-b7e0-7abf35df7d49	<div class="kc-logo-text"><span>Keycloak</span></div>
defaultSignatureAlgorithm	eacf1fae-7916-43d5-b7e0-7abf35df7d49	RS256
offlineSessionMaxLifespanEnabled	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
offlineSessionMaxLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	5184000
bruteForceProtected	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
permanentLockout	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
maxTemporaryLockouts	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
bruteForceStrategy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	MULTIPLE
maxFailureWaitSeconds	2c411af7-e0b7-4547-b08a-27c7c8c1722c	900
minimumQuickLoginWaitSeconds	2c411af7-e0b7-4547-b08a-27c7c8c1722c	60
waitIncrementSeconds	2c411af7-e0b7-4547-b08a-27c7c8c1722c	60
quickLoginCheckMilliSeconds	2c411af7-e0b7-4547-b08a-27c7c8c1722c	1000
maxDeltaTimeSeconds	2c411af7-e0b7-4547-b08a-27c7c8c1722c	43200
failureFactor	2c411af7-e0b7-4547-b08a-27c7c8c1722c	30
realmReusableOtpCode	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
defaultSignatureAlgorithm	2c411af7-e0b7-4547-b08a-27c7c8c1722c	RS256
offlineSessionMaxLifespanEnabled	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
offlineSessionMaxLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	5184000
actionTokenGeneratedByAdminLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	43200
actionTokenGeneratedByUserLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	300
oauth2DeviceCodeLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	600
oauth2DevicePollingInterval	2c411af7-e0b7-4547-b08a-27c7c8c1722c	5
webAuthnPolicyRpEntityName	2c411af7-e0b7-4547-b08a-27c7c8c1722c	keycloak
webAuthnPolicySignatureAlgorithms	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ES256,RS256
webAuthnPolicyRpId	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
webAuthnPolicyAttestationConveyancePreference	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyAuthenticatorAttachment	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyRequireResidentKey	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyUserVerificationRequirement	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyCreateTimeout	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
webAuthnPolicyAvoidSameAuthenticatorRegister	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
webAuthnPolicyRpEntityNamePasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	keycloak
webAuthnPolicySignatureAlgorithmsPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ES256,RS256
webAuthnPolicyRpIdPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
webAuthnPolicyAttestationConveyancePreferencePasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyAuthenticatorAttachmentPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyRequireResidentKeyPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyUserVerificationRequirementPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	not specified
webAuthnPolicyCreateTimeoutPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
webAuthnPolicyAvoidSameAuthenticatorRegisterPasswordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
cibaBackchannelTokenDeliveryMode	2c411af7-e0b7-4547-b08a-27c7c8c1722c	poll
cibaExpiresIn	2c411af7-e0b7-4547-b08a-27c7c8c1722c	120
cibaInterval	2c411af7-e0b7-4547-b08a-27c7c8c1722c	5
cibaAuthRequestedUserHint	2c411af7-e0b7-4547-b08a-27c7c8c1722c	login_hint
parRequestUriLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	60
firstBrokerLoginFlowId	2c411af7-e0b7-4547-b08a-27c7c8c1722c	83f93401-8fc1-484f-b7f0-8c55381a1943
shortVerificationUri	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
actionTokenGeneratedByUserLifespan.verify-email	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
actionTokenGeneratedByUserLifespan.idp-verify-account-via-email	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
actionTokenGeneratedByUserLifespan.reset-credentials	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
actionTokenGeneratedByUserLifespan.execute-actions	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
organizationsEnabled	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
adminPermissionsEnabled	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
verifiableCredentialsEnabled	2c411af7-e0b7-4547-b08a-27c7c8c1722c	false
clientSessionIdleTimeout	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
clientSessionMaxLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
clientOfflineSessionIdleTimeout	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
clientOfflineSessionMaxLifespan	2c411af7-e0b7-4547-b08a-27c7c8c1722c	0
client-policies.profiles	2c411af7-e0b7-4547-b08a-27c7c8c1722c	{"profiles":[]}
client-policies.policies	2c411af7-e0b7-4547-b08a-27c7c8c1722c	{"policies":[]}
_browser_header.contentSecurityPolicyReportOnly	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
_browser_header.xContentTypeOptions	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nosniff
_browser_header.referrerPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	no-referrer
_browser_header.xRobotsTag	2c411af7-e0b7-4547-b08a-27c7c8c1722c	none
_browser_header.xFrameOptions	2c411af7-e0b7-4547-b08a-27c7c8c1722c	SAMEORIGIN
_browser_header.contentSecurityPolicy	2c411af7-e0b7-4547-b08a-27c7c8c1722c	frame-src 'self'; frame-ancestors 'self'; object-src 'none';
_browser_header.xXSSProtection	2c411af7-e0b7-4547-b08a-27c7c8c1722c	1; mode=block
_browser_header.strictTransportSecurity	2c411af7-e0b7-4547-b08a-27c7c8c1722c	max-age=31536000; includeSubDomains
frontendUrl	eacf1fae-7916-43d5-b7e0-7abf35df7d49	
darkMode	2c411af7-e0b7-4547-b08a-27c7c8c1722c	true
acr.loa.map	eacf1fae-7916-43d5-b7e0-7abf35df7d49	{}
cibaBackchannelTokenDeliveryMode	eacf1fae-7916-43d5-b7e0-7abf35df7d49	poll
cibaExpiresIn	eacf1fae-7916-43d5-b7e0-7abf35df7d49	120
cibaAuthRequestedUserHint	eacf1fae-7916-43d5-b7e0-7abf35df7d49	login_hint
parRequestUriLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	60
cibaInterval	eacf1fae-7916-43d5-b7e0-7abf35df7d49	5
organizationsEnabled	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
adminPermissionsEnabled	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
verifiableCredentialsEnabled	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
actionTokenGeneratedByAdminLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	43200
actionTokenGeneratedByUserLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	300
oauth2DeviceCodeLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	600
oauth2DevicePollingInterval	eacf1fae-7916-43d5-b7e0-7abf35df7d49	5
clientSessionIdleTimeout	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
clientSessionMaxLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
clientOfflineSessionIdleTimeout	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
clientOfflineSessionMaxLifespan	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
webAuthnPolicyRpEntityName	eacf1fae-7916-43d5-b7e0-7abf35df7d49	keycloak
webAuthnPolicySignatureAlgorithms	eacf1fae-7916-43d5-b7e0-7abf35df7d49	ES256,RS256
webAuthnPolicyRpId	eacf1fae-7916-43d5-b7e0-7abf35df7d49	
webAuthnPolicyAttestationConveyancePreference	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyAuthenticatorAttachment	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyRequireResidentKey	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyUserVerificationRequirement	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyCreateTimeout	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
webAuthnPolicyAvoidSameAuthenticatorRegister	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
webAuthnPolicyRpEntityNamePasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	keycloak
webAuthnPolicySignatureAlgorithmsPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	ES256,RS256
webAuthnPolicyRpIdPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	
webAuthnPolicyAttestationConveyancePreferencePasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyAuthenticatorAttachmentPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyRequireResidentKeyPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyUserVerificationRequirementPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	not specified
webAuthnPolicyCreateTimeoutPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	0
webAuthnPolicyAvoidSameAuthenticatorRegisterPasswordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	false
client-policies.profiles	eacf1fae-7916-43d5-b7e0-7abf35df7d49	{"profiles":[]}
client-policies.policies	eacf1fae-7916-43d5-b7e0-7abf35df7d49	{"policies":[]}
_browser_header.contentSecurityPolicyReportOnly	eacf1fae-7916-43d5-b7e0-7abf35df7d49	
_browser_header.xContentTypeOptions	eacf1fae-7916-43d5-b7e0-7abf35df7d49	nosniff
_browser_header.referrerPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	no-referrer
_browser_header.xRobotsTag	eacf1fae-7916-43d5-b7e0-7abf35df7d49	none
_browser_header.xFrameOptions	eacf1fae-7916-43d5-b7e0-7abf35df7d49	SAMEORIGIN
_browser_header.contentSecurityPolicy	eacf1fae-7916-43d5-b7e0-7abf35df7d49	frame-src 'self'; frame-ancestors 'self'; object-src 'none';
_browser_header.xXSSProtection	eacf1fae-7916-43d5-b7e0-7abf35df7d49	1; mode=block
_browser_header.strictTransportSecurity	eacf1fae-7916-43d5-b7e0-7abf35df7d49	max-age=31536000; includeSubDomains
acr.loa.map	2c411af7-e0b7-4547-b08a-27c7c8c1722c	{}
displayName	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
displayNameHtml	2c411af7-e0b7-4547-b08a-27c7c8c1722c	
frontendUrl	2c411af7-e0b7-4547-b08a-27c7c8c1722c	http://10.3.12.234:8080/
\.


--
-- Data for Name: realm_default_groups; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_default_groups (realm_id, group_id) FROM stdin;
\.


--
-- Data for Name: realm_enabled_event_types; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_enabled_event_types (realm_id, value) FROM stdin;
2c411af7-e0b7-4547-b08a-27c7c8c1722c	SEND_RESET_PASSWORD
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_CONSENT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	GRANT_CONSENT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	VERIFY_PROFILE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REMOVE_TOTP
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REVOKE_GRANT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_TOTP
2c411af7-e0b7-4547-b08a-27c7c8c1722c	LOGIN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_LOGIN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	RESET_PASSWORD_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_CREDENTIAL
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IMPERSONATE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CODE_TO_TOKEN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CUSTOM_REQUIRED_ACTION
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_DEVICE_CODE_TO_TOKEN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	RESTART_AUTHENTICATION
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IMPERSONATE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_PROFILE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	LOGIN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_DEVICE_VERIFY_USER_CODE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_PASSWORD_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_INITIATED_ACCOUNT_LINKING
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_EXTENSION_GRANT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	USER_DISABLED_BY_PERMANENT_LOCKOUT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REMOVE_CREDENTIAL_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	TOKEN_EXCHANGE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	AUTHREQID_TO_TOKEN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	LOGOUT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REGISTER
2c411af7-e0b7-4547-b08a-27c7c8c1722c	DELETE_ACCOUNT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_REGISTER
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IDENTITY_PROVIDER_LINK_ACCOUNT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	USER_DISABLED_BY_TEMPORARY_LOCKOUT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	DELETE_ACCOUNT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_PASSWORD
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_DELETE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	FEDERATED_IDENTITY_LINK_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IDENTITY_PROVIDER_FIRST_LOGIN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_DELETE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	VERIFY_EMAIL
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_LOGIN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	RESTART_AUTHENTICATION_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	EXECUTE_ACTIONS
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REMOVE_FEDERATED_IDENTITY_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	TOKEN_EXCHANGE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	PERMISSION_TOKEN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	FEDERATED_IDENTITY_OVERRIDE_LINK
2c411af7-e0b7-4547-b08a-27c7c8c1722c	SEND_IDENTITY_PROVIDER_LINK_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_CREDENTIAL_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	EXECUTE_ACTION_TOKEN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_EXTENSION_GRANT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	SEND_VERIFY_EMAIL
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_DEVICE_AUTH
2c411af7-e0b7-4547-b08a-27c7c8c1722c	EXECUTE_ACTIONS_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REMOVE_FEDERATED_IDENTITY
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_DEVICE_CODE_TO_TOKEN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IDENTITY_PROVIDER_POST_LOGIN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IDENTITY_PROVIDER_LINK_ACCOUNT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	FEDERATED_IDENTITY_OVERRIDE_LINK_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_DEVICE_VERIFY_USER_CODE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_EMAIL
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REGISTER_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REVOKE_GRANT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	EXECUTE_ACTION_TOKEN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	LOGOUT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_EMAIL_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_UPDATE_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	AUTHREQID_TO_TOKEN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	INVITE_ORG_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_PROFILE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_REGISTER_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	FEDERATED_IDENTITY_LINK
2c411af7-e0b7-4547-b08a-27c7c8c1722c	INVITE_ORG
2c411af7-e0b7-4547-b08a-27c7c8c1722c	SEND_IDENTITY_PROVIDER_LINK
2c411af7-e0b7-4547-b08a-27c7c8c1722c	SEND_VERIFY_EMAIL_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	RESET_PASSWORD
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_INITIATED_ACCOUNT_LINKING_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	OAUTH2_DEVICE_AUTH_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REMOVE_CREDENTIAL
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_CONSENT
2c411af7-e0b7-4547-b08a-27c7c8c1722c	REMOVE_TOTP_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	VERIFY_EMAIL_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	SEND_RESET_PASSWORD_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CLIENT_UPDATE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CUSTOM_REQUIRED_ACTION_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IDENTITY_PROVIDER_POST_LOGIN_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	UPDATE_TOTP_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	CODE_TO_TOKEN
2c411af7-e0b7-4547-b08a-27c7c8c1722c	VERIFY_PROFILE
2c411af7-e0b7-4547-b08a-27c7c8c1722c	GRANT_CONSENT_ERROR
2c411af7-e0b7-4547-b08a-27c7c8c1722c	IDENTITY_PROVIDER_FIRST_LOGIN_ERROR
\.


--
-- Data for Name: realm_events_listeners; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_events_listeners (realm_id, value) FROM stdin;
2c411af7-e0b7-4547-b08a-27c7c8c1722c	my-registration-listener
2c411af7-e0b7-4547-b08a-27c7c8c1722c	jboss-logging
eacf1fae-7916-43d5-b7e0-7abf35df7d49	jboss-logging
\.


--
-- Data for Name: realm_localizations; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_localizations (realm_id, locale, texts) FROM stdin;
\.


--
-- Data for Name: realm_required_credential; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_required_credential (type, form_label, input, secret, realm_id) FROM stdin;
password	password	t	t	eacf1fae-7916-43d5-b7e0-7abf35df7d49
password	password	t	t	2c411af7-e0b7-4547-b08a-27c7c8c1722c
\.


--
-- Data for Name: realm_smtp_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_smtp_config (realm_id, value, name) FROM stdin;
\.


--
-- Data for Name: realm_supported_locales; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.realm_supported_locales (realm_id, value) FROM stdin;
\.


--
-- Data for Name: redirect_uris; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.redirect_uris (client_id, value) FROM stdin;
d7e66ce3-0769-4b3d-9636-4893459eaf54	/realms/master/account/*
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	/realms/master/account/*
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	/admin/master/console/*
500b5c86-ba2e-4345-8602-4e8576a82347	/realms/tskhra/account/*
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	/realms/tskhra/account/*
7f207e63-5406-447c-9a3b-97cdddc5e07a	/admin/tskhra/console/*
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	/*
b4b39689-8818-4208-b102-ee758dad2268	http://localhost:5175/*
15735a86-4946-440b-9251-0e8487f6eb01	http://10.3.12.148:5173/*
15735a86-4946-440b-9251-0e8487f6eb01	https://10.3.13.35:5173/*
15735a86-4946-440b-9251-0e8487f6eb01	http://localhost:5173/*
15735a86-4946-440b-9251-0e8487f6eb01	http://localhost:5175/*
15735a86-4946-440b-9251-0e8487f6eb01	http://10.3.13.35:5173/*
15735a86-4946-440b-9251-0e8487f6eb01	https://10.3.12.148:5173/*
\.


--
-- Data for Name: required_action_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.required_action_config (required_action_id, value, name) FROM stdin;
\.


--
-- Data for Name: required_action_provider; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.required_action_provider (id, alias, name, realm_id, enabled, default_action, provider_id, priority) FROM stdin;
f4309e73-a2c8-42be-be08-a92db8d89b7a	VERIFY_EMAIL	Verify Email	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	VERIFY_EMAIL	50
6dae3370-c935-4dc5-a21f-a156aa7cd9fe	UPDATE_PROFILE	Update Profile	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	UPDATE_PROFILE	40
5afc7dae-f568-4422-ac23-d657dbcda2e3	CONFIGURE_TOTP	Configure OTP	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	CONFIGURE_TOTP	10
900c998a-a90c-4cef-ad72-87e2e167fad2	UPDATE_PASSWORD	Update Password	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	UPDATE_PASSWORD	30
3d21031c-f842-4833-98d4-d3a9d4e8d983	TERMS_AND_CONDITIONS	Terms and Conditions	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	f	TERMS_AND_CONDITIONS	20
2e57ab5d-3ab5-4c3a-9051-378073d6fde9	delete_account	Delete Account	eacf1fae-7916-43d5-b7e0-7abf35df7d49	f	f	delete_account	60
b6347af6-f205-468a-8348-ad7d145862b4	delete_credential	Delete Credential	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	delete_credential	100
00ac20f1-cda5-42aa-ba10-91e319f2625e	update_user_locale	Update User Locale	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	update_user_locale	1000
9f37a046-0d8c-4893-af78-ee9492a1be62	webauthn-register	Webauthn Register	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	webauthn-register	70
95b08c59-9947-49d5-9c97-a9221a731895	webauthn-register-passwordless	Webauthn Register Passwordless	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	webauthn-register-passwordless	80
3c5edad8-2aa7-4a2d-bad4-46397fbc6554	VERIFY_PROFILE	Verify Profile	eacf1fae-7916-43d5-b7e0-7abf35df7d49	t	f	VERIFY_PROFILE	90
93320ffb-a893-4b64-abbb-f2952a6cded6	VERIFY_EMAIL	Verify Email	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	VERIFY_EMAIL	50
b96b5870-50f8-4ae5-a13e-8a4c5a615f0c	UPDATE_PROFILE	Update Profile	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	UPDATE_PROFILE	40
a63ba3f3-142f-4da3-8532-4d3483e180c8	CONFIGURE_TOTP	Configure OTP	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	CONFIGURE_TOTP	10
63b3270b-045b-4084-991a-3b76374b0bac	UPDATE_PASSWORD	Update Password	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	UPDATE_PASSWORD	30
61f13533-10a6-43ee-912d-3c9320404447	TERMS_AND_CONDITIONS	Terms and Conditions	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	f	TERMS_AND_CONDITIONS	20
41c02d35-6bca-4c80-bb73-026bfbcb142b	delete_account	Delete Account	2c411af7-e0b7-4547-b08a-27c7c8c1722c	f	f	delete_account	60
ed571aaa-0861-4206-a602-47948de3ae0c	delete_credential	Delete Credential	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	delete_credential	100
15436604-f2c9-4d88-8b58-2368d978ca64	update_user_locale	Update User Locale	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	update_user_locale	1000
94dc9534-00dd-4b84-aab0-8289f3e00515	webauthn-register	Webauthn Register	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	webauthn-register	70
7f6e7290-603b-4709-8c9a-20c670d7e420	webauthn-register-passwordless	Webauthn Register Passwordless	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	webauthn-register-passwordless	80
7cf58e31-1048-481c-9a07-4dc097199e60	VERIFY_PROFILE	Verify Profile	2c411af7-e0b7-4547-b08a-27c7c8c1722c	t	f	VERIFY_PROFILE	90
\.


--
-- Data for Name: resource_attribute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_attribute (id, name, value, resource_id) FROM stdin;
\.


--
-- Data for Name: resource_policy; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_policy (resource_id, policy_id) FROM stdin;
\.


--
-- Data for Name: resource_scope; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_scope (resource_id, scope_id) FROM stdin;
\.


--
-- Data for Name: resource_server; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_server (id, allow_rs_remote_mgmt, policy_enforce_mode, decision_strategy) FROM stdin;
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	t	0	1
\.


--
-- Data for Name: resource_server_perm_ticket; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_server_perm_ticket (id, owner, requester, created_timestamp, granted_timestamp, resource_id, scope_id, resource_server_id, policy_id) FROM stdin;
\.


--
-- Data for Name: resource_server_policy; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_server_policy (id, name, description, type, decision_strategy, logic, resource_server_id, owner) FROM stdin;
c4f8dde2-c2ad-4809-b5a2-d0516c18ad41	Default Policy	A policy that grants access only for users within this realm	js	0	0	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	\N
3064dc90-e62f-4046-b113-e974414ae787	Default Permission	A permission that applies to the default resource type	resource	1	0	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	\N
\.


--
-- Data for Name: resource_server_resource; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_server_resource (id, name, type, icon_uri, owner, resource_server_id, owner_managed_access, display_name) FROM stdin;
4b6110d7-2b8d-46fb-90ec-7f4f5810056f	Default Resource	urn:user-service:resources:default	\N	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	f	\N
\.


--
-- Data for Name: resource_server_scope; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_server_scope (id, name, icon_uri, resource_server_id, display_name) FROM stdin;
\.


--
-- Data for Name: resource_uris; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.resource_uris (resource_id, value) FROM stdin;
4b6110d7-2b8d-46fb-90ec-7f4f5810056f	/*
\.


--
-- Data for Name: revoked_token; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.revoked_token (id, expire) FROM stdin;
\.


--
-- Data for Name: role_attribute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.role_attribute (id, role_id, name, value) FROM stdin;
\.


--
-- Data for Name: scope_mapping; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.scope_mapping (client_id, role_id) FROM stdin;
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	643fba7e-98b5-4b0b-8ee4-14220fe712ee
884bbb5a-f06a-4a93-b2a2-c52426a1ef0d	057fcb24-70d4-43df-8c5f-6d26d91a0b77
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	b4238827-06c4-4efc-9973-cbc334904655
2b0555eb-7a6e-48fd-9dba-a91a70bbc7f0	27e136f9-a685-4177-b79e-807e18b2492f
\.


--
-- Data for Name: scope_policy; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.scope_policy (scope_id, policy_id) FROM stdin;
\.


--
-- Data for Name: user_attribute; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_attribute (name, value, user_id, id, long_value_hash, long_value_hash_lower_case, long_value) FROM stdin;
is_temporary_admin	true	021c2681-cf67-48bf-905d-c9f04db47c15	0d1bdad5-c328-44a2-ada3-7f61eb58512a	\N	\N	\N
\.


--
-- Data for Name: user_consent; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_consent (id, client_id, user_id, created_date, last_updated_date, client_storage_provider, external_client_id) FROM stdin;
\.


--
-- Data for Name: user_consent_client_scope; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_consent_client_scope (user_consent_id, scope_id) FROM stdin;
\.


--
-- Data for Name: user_entity; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_entity (id, email, email_constraint, email_verified, enabled, federation_link, first_name, last_name, realm_id, username, created_timestamp, service_account_client_link, not_before) FROM stdin;
021c2681-cf67-48bf-905d-c9f04db47c15	\N	d57671b4-3d26-48c6-9b6a-898e91cea6f5	f	t	\N	\N	\N	eacf1fae-7916-43d5-b7e0-7abf35df7d49	admin	1770584539741	\N	0
ca73b406-e6fc-4e6e-a4b4-7002473ee4f9	\N	38f6cb2d-002a-4324-a133-b7f33f4c96a7	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	service-account-user-service	1770585862699	1b0f8fa6-dea3-4924-ad21-b92aefb3e748	0
13b381de-f825-4f42-8075-1cb5fc968420	kukilek1i@gmail.com	kukilek1i@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	m_k	1771248430347	\N	0
2f63ed80-ccf2-441b-a133-039c8e23451c	nino.mtsituridze@makingscience.com	nino.mtsituridze@makingscience.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nino_nino	1771252255892	\N	0
a508ba28-813f-4e1a-9054-8d3296d45f68	mtsituridze@makingscience.com	mtsituridze@makingscience.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	n23	1771253156266	\N	0
82717555-0804-479f-b099-1e797e52ef26	amo3@gmail.com	amo3@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	amo3	1770973890096	\N	0
c1b9eb69-f809-4926-90c8-74cdd61c49dd	gebar31205@mailinator.com	gebar31205@mailinator.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	test	1771253334138	\N	0
2bf9e0a5-4ff9-4a1c-9656-af1deaf9a360	mtsiturid@makingscience.com	mtsiturid@makingscience.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nino	1771253369476	\N	0
f2e705f1-22bf-462d-96bd-f28e4f3e5dd4	gebar31205@mailinator	gebar31205@mailinator	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	gbdbgscg	1771253664937	\N	0
11410dc4-aaf5-4d12-ba7e-98faa22dad4e	1@tnet.ge	1@tnet.ge	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	123	1771253717841	\N	0
4cffe999-c408-47d8-b373-a135c33c584b	gebar@mailinator	gebar@mailinator	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	vgebcdhj	1771253732633	\N	0
9c59c419-de93-4c22-90f8-0acc8441258c	kukilekascsace12332i@gmail	kukilekascsace12332i@gmail	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	trgrefre	1771253818203	\N	0
0a6def52-8847-4d71-99e6-f05ea861e89f	2@tnet.ge	2@tnet.ge	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nin	1771255044298	\N	0
54fa4a2f-1a44-4839-afb9-273cbb76b6c5	2@tnetge	2@tnetge	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nin1	1771255093211	\N	0
f3501123-3a28-4069-91f9-c5cd37cae847	testmail1@gmail.com	testmail1@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	mkk	1771256101579	\N	0
c49a2488-fec3-41a4-b045-64523f61a72c	testmail5@gmail.com	testmail5@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	misha	1771312897553	\N	0
6dc077ea-1aed-45a3-864f-d9e9192ab3b4	btgvfddcs@gamil.uk	btgvfddcs@gamil.uk	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ytrvgfecbtv	1771318788568	\N	0
622a15dd-1b68-4359-9b83-749167855ddf	1@makingscience.com	1@makingscience.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nino123	1771322378747	\N	0
c4ddb6a8-262f-4fac-a56b-cc9aec5395d1	2@makingscience.com	2@makingscience.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nino1234	1771322547524	\N	0
a0216fcd-713f-4ede-aa6e-0c9a183bf5fc	misha123@gmail.com	misha123@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	misha_228	1771325323007	\N	0
9512c9ac-fb14-44b3-a6bb-80fde34f6f9d	mt@gmail.com	mt@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	mtsirekidze	1771229664032	\N	0
16aa7fe9-754b-44f4-bc6e-dd9ad46ac548	test123@gmail.com	test123@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	test23	1771326123338	\N	0
93655b56-7b7a-4ba3-8839-1ad920809cf2	cwrceve@gmail.com	cwrceve@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	fgfgvtgv	1771336148327	\N	0
0ac233ac-ec8e-4a37-9183-af309a5bbc2c	hhhhh@hhhhhh.hhh	hhhhh@hhhhhh.hhh	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	hhh	1771336424731	\N	0
87d8e1bf-4026-4e60-ae30-a7e17a8e97a8	testmail100@gmail.com	testmail100@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	test237	1771400814989	\N	0
cf0282bc-09f2-4bd2-a51b-eaae07dddb32	kavtaradze.keti@gmail.com	kavtaradze.keti@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	kkk	1771503136158	\N	0
0cc2b18a-72d2-4c3a-b073-8608ac0a4d3d	mail@gmail.com	mail@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ads	1771233442064	\N	0
bf32ef13-193f-4cb4-8f94-1d8944e92036	a@gmail.com	a@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	miriantsirekidze123	1771509811790	\N	0
f2bd8ba3-7d1b-4884-987a-53f58ffb903c	xixadof354@amiralty.com	xixadof354@amiralty.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	ghost	1771511120575	\N	0
040af51b-8763-4bef-933d-15ede5142995	amo@chamo.com	amo@chamo.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	amochamo	1771234231122	\N	0
5fe53f87-d1cf-4673-8a1f-561b8f31c740	testmail@gmail.com	testmail@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	lalala	1771234334311	\N	0
70e74a1d-5e8c-4349-9f14-0272f44464f8	lalala@gmail.com	lalala@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	new_use	1771573026154	\N	0
db8b7221-7ad2-4daa-80a1-663fdc3a5049	mail2@gmail.com	mail2@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	nkk	1771244703667	\N	0
5b0c5b26-6648-4e6e-b324-be8b36ee4982	kukileki@gmail.com	kukileki@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	12334	1771247513299	\N	0
5955cb99-825e-4510-97e1-ed7b260922f4	anano.topuriaa@gmail.com	anano.topuriaa@gmail.com	f	t	\N	\N	\N	2c411af7-e0b7-4547-b08a-27c7c8c1722c	anano	1771830220663	\N	0
\.


--
-- Data for Name: user_federation_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_federation_config (user_federation_provider_id, value, name) FROM stdin;
\.


--
-- Data for Name: user_federation_mapper; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_federation_mapper (id, name, federation_provider_id, federation_mapper_type, realm_id) FROM stdin;
\.


--
-- Data for Name: user_federation_mapper_config; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_federation_mapper_config (user_federation_mapper_id, value, name) FROM stdin;
\.


--
-- Data for Name: user_federation_provider; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_federation_provider (id, changed_sync_period, display_name, full_sync_period, last_sync, priority, provider_name, realm_id) FROM stdin;
\.


--
-- Data for Name: user_group_membership; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_group_membership (group_id, user_id, membership_type) FROM stdin;
\.


--
-- Data for Name: user_required_action; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_required_action (user_id, required_action) FROM stdin;
\.


--
-- Data for Name: user_role_mapping; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.user_role_mapping (role_id, user_id) FROM stdin;
b4450810-c34f-4a44-8e5c-dd185fdbef3a	021c2681-cf67-48bf-905d-c9f04db47c15
2f900f42-4321-4fa3-9e4e-4a49a9f30dc5	021c2681-cf67-48bf-905d-c9f04db47c15
a6fb666e-17a0-4cf9-95c2-820ed013c95b	ca73b406-e6fc-4e6e-a4b4-7002473ee4f9
e8f3dec7-6a74-4840-8ab9-4b23eacabd27	ca73b406-e6fc-4e6e-a4b4-7002473ee4f9
e1c9a6b8-d11f-4436-be68-365bdfdd957b	ca73b406-e6fc-4e6e-a4b4-7002473ee4f9
058b3d84-3c8c-4fa3-b61c-f571cb56e4b7	ca73b406-e6fc-4e6e-a4b4-7002473ee4f9
a6fb666e-17a0-4cf9-95c2-820ed013c95b	5955cb99-825e-4510-97e1-ed7b260922f4
a6fb666e-17a0-4cf9-95c2-820ed013c95b	82717555-0804-479f-b099-1e797e52ef26
a6fb666e-17a0-4cf9-95c2-820ed013c95b	9512c9ac-fb14-44b3-a6bb-80fde34f6f9d
a6fb666e-17a0-4cf9-95c2-820ed013c95b	0cc2b18a-72d2-4c3a-b073-8608ac0a4d3d
a6fb666e-17a0-4cf9-95c2-820ed013c95b	040af51b-8763-4bef-933d-15ede5142995
a6fb666e-17a0-4cf9-95c2-820ed013c95b	5fe53f87-d1cf-4673-8a1f-561b8f31c740
a6fb666e-17a0-4cf9-95c2-820ed013c95b	db8b7221-7ad2-4daa-80a1-663fdc3a5049
a6fb666e-17a0-4cf9-95c2-820ed013c95b	5b0c5b26-6648-4e6e-b324-be8b36ee4982
a6fb666e-17a0-4cf9-95c2-820ed013c95b	13b381de-f825-4f42-8075-1cb5fc968420
a6fb666e-17a0-4cf9-95c2-820ed013c95b	2f63ed80-ccf2-441b-a133-039c8e23451c
a6fb666e-17a0-4cf9-95c2-820ed013c95b	a508ba28-813f-4e1a-9054-8d3296d45f68
a6fb666e-17a0-4cf9-95c2-820ed013c95b	c1b9eb69-f809-4926-90c8-74cdd61c49dd
a6fb666e-17a0-4cf9-95c2-820ed013c95b	2bf9e0a5-4ff9-4a1c-9656-af1deaf9a360
a6fb666e-17a0-4cf9-95c2-820ed013c95b	f2e705f1-22bf-462d-96bd-f28e4f3e5dd4
a6fb666e-17a0-4cf9-95c2-820ed013c95b	11410dc4-aaf5-4d12-ba7e-98faa22dad4e
a6fb666e-17a0-4cf9-95c2-820ed013c95b	4cffe999-c408-47d8-b373-a135c33c584b
a6fb666e-17a0-4cf9-95c2-820ed013c95b	9c59c419-de93-4c22-90f8-0acc8441258c
a6fb666e-17a0-4cf9-95c2-820ed013c95b	0a6def52-8847-4d71-99e6-f05ea861e89f
a6fb666e-17a0-4cf9-95c2-820ed013c95b	54fa4a2f-1a44-4839-afb9-273cbb76b6c5
a6fb666e-17a0-4cf9-95c2-820ed013c95b	f3501123-3a28-4069-91f9-c5cd37cae847
a6fb666e-17a0-4cf9-95c2-820ed013c95b	c49a2488-fec3-41a4-b045-64523f61a72c
a6fb666e-17a0-4cf9-95c2-820ed013c95b	6dc077ea-1aed-45a3-864f-d9e9192ab3b4
a6fb666e-17a0-4cf9-95c2-820ed013c95b	622a15dd-1b68-4359-9b83-749167855ddf
a6fb666e-17a0-4cf9-95c2-820ed013c95b	c4ddb6a8-262f-4fac-a56b-cc9aec5395d1
a6fb666e-17a0-4cf9-95c2-820ed013c95b	a0216fcd-713f-4ede-aa6e-0c9a183bf5fc
a6fb666e-17a0-4cf9-95c2-820ed013c95b	16aa7fe9-754b-44f4-bc6e-dd9ad46ac548
a6fb666e-17a0-4cf9-95c2-820ed013c95b	93655b56-7b7a-4ba3-8839-1ad920809cf2
a6fb666e-17a0-4cf9-95c2-820ed013c95b	0ac233ac-ec8e-4a37-9183-af309a5bbc2c
a6fb666e-17a0-4cf9-95c2-820ed013c95b	87d8e1bf-4026-4e60-ae30-a7e17a8e97a8
a6fb666e-17a0-4cf9-95c2-820ed013c95b	cf0282bc-09f2-4bd2-a51b-eaae07dddb32
a6fb666e-17a0-4cf9-95c2-820ed013c95b	bf32ef13-193f-4cb4-8f94-1d8944e92036
a6fb666e-17a0-4cf9-95c2-820ed013c95b	f2bd8ba3-7d1b-4884-987a-53f58ffb903c
a6fb666e-17a0-4cf9-95c2-820ed013c95b	70e74a1d-5e8c-4349-9f14-0272f44464f8
\.


--
-- Data for Name: web_origins; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.web_origins (client_id, value) FROM stdin;
d2c6e8c7-59ae-4b82-96e6-e68e1475b141	+
7f207e63-5406-447c-9a3b-97cdddc5e07a	+
1b0f8fa6-dea3-4924-ad21-b92aefb3e748	/*
b4b39689-8818-4208-b102-ee758dad2268	/*
15735a86-4946-440b-9251-0e8487f6eb01	*
\.


--
-- Data for Name: webhook; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.webhook (id, enabled, url, secret, created_at, created_by_user_id, realm_id, algorithm) FROM stdin;
\.


--
-- Data for Name: webhook_event; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.webhook_event (id, realm_id, event_type, event_id, admin_event_id, event_object) FROM stdin;
\.


--
-- Data for Name: webhook_event_types; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.webhook_event_types (webhook_id, value) FROM stdin;
\.


--
-- Data for Name: webhook_send; Type: TABLE DATA; Schema: public; Owner: admin
--

COPY public.webhook_send (id, event_type, webhook_id, webhook_event_id, sent_at, retries, status) FROM stdin;
\.


--
-- Name: org_domain ORG_DOMAIN_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.org_domain
    ADD CONSTRAINT "ORG_DOMAIN_pkey" PRIMARY KEY (id, name);


--
-- Name: org ORG_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT "ORG_pkey" PRIMARY KEY (id);


--
-- Name: keycloak_role UK_J3RWUVD56ONTGSUHOGM184WW2-2; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.keycloak_role
    ADD CONSTRAINT "UK_J3RWUVD56ONTGSUHOGM184WW2-2" UNIQUE (name, client_realm_constraint);


--
-- Name: client_auth_flow_bindings c_cli_flow_bind; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_auth_flow_bindings
    ADD CONSTRAINT c_cli_flow_bind PRIMARY KEY (client_id, binding_name);


--
-- Name: client_scope_client c_cli_scope_bind; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope_client
    ADD CONSTRAINT c_cli_scope_bind PRIMARY KEY (client_id, scope_id);


--
-- Name: client_initial_access cnstr_client_init_acc_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_initial_access
    ADD CONSTRAINT cnstr_client_init_acc_pk PRIMARY KEY (id);


--
-- Name: realm_default_groups con_group_id_def_groups; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_default_groups
    ADD CONSTRAINT con_group_id_def_groups UNIQUE (group_id);


--
-- Name: broker_link constr_broker_link_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.broker_link
    ADD CONSTRAINT constr_broker_link_pk PRIMARY KEY (identity_provider, user_id);


--
-- Name: component_config constr_component_config_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.component_config
    ADD CONSTRAINT constr_component_config_pk PRIMARY KEY (id);


--
-- Name: component constr_component_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.component
    ADD CONSTRAINT constr_component_pk PRIMARY KEY (id);


--
-- Name: fed_user_required_action constr_fed_required_action; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_required_action
    ADD CONSTRAINT constr_fed_required_action PRIMARY KEY (required_action, user_id);


--
-- Name: fed_user_attribute constr_fed_user_attr_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_attribute
    ADD CONSTRAINT constr_fed_user_attr_pk PRIMARY KEY (id);


--
-- Name: fed_user_consent constr_fed_user_consent_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_consent
    ADD CONSTRAINT constr_fed_user_consent_pk PRIMARY KEY (id);


--
-- Name: fed_user_credential constr_fed_user_cred_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_credential
    ADD CONSTRAINT constr_fed_user_cred_pk PRIMARY KEY (id);


--
-- Name: fed_user_group_membership constr_fed_user_group; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_group_membership
    ADD CONSTRAINT constr_fed_user_group PRIMARY KEY (group_id, user_id);


--
-- Name: fed_user_role_mapping constr_fed_user_role; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_role_mapping
    ADD CONSTRAINT constr_fed_user_role PRIMARY KEY (role_id, user_id);


--
-- Name: federated_user constr_federated_user; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.federated_user
    ADD CONSTRAINT constr_federated_user PRIMARY KEY (id);


--
-- Name: realm_default_groups constr_realm_default_groups; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_default_groups
    ADD CONSTRAINT constr_realm_default_groups PRIMARY KEY (realm_id, group_id);


--
-- Name: realm_enabled_event_types constr_realm_enabl_event_types; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_enabled_event_types
    ADD CONSTRAINT constr_realm_enabl_event_types PRIMARY KEY (realm_id, value);


--
-- Name: realm_events_listeners constr_realm_events_listeners; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_events_listeners
    ADD CONSTRAINT constr_realm_events_listeners PRIMARY KEY (realm_id, value);


--
-- Name: realm_supported_locales constr_realm_supported_locales; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_supported_locales
    ADD CONSTRAINT constr_realm_supported_locales PRIMARY KEY (realm_id, value);


--
-- Name: identity_provider constraint_2b; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider
    ADD CONSTRAINT constraint_2b PRIMARY KEY (internal_id);


--
-- Name: client_attributes constraint_3c; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_attributes
    ADD CONSTRAINT constraint_3c PRIMARY KEY (client_id, name);


--
-- Name: event_entity constraint_4; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.event_entity
    ADD CONSTRAINT constraint_4 PRIMARY KEY (id);


--
-- Name: federated_identity constraint_40; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.federated_identity
    ADD CONSTRAINT constraint_40 PRIMARY KEY (identity_provider, user_id);


--
-- Name: realm constraint_4a; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm
    ADD CONSTRAINT constraint_4a PRIMARY KEY (id);


--
-- Name: user_federation_provider constraint_5c; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_provider
    ADD CONSTRAINT constraint_5c PRIMARY KEY (id);


--
-- Name: client constraint_7; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT constraint_7 PRIMARY KEY (id);


--
-- Name: scope_mapping constraint_81; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scope_mapping
    ADD CONSTRAINT constraint_81 PRIMARY KEY (client_id, role_id);


--
-- Name: client_node_registrations constraint_84; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_node_registrations
    ADD CONSTRAINT constraint_84 PRIMARY KEY (client_id, name);


--
-- Name: realm_attribute constraint_9; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_attribute
    ADD CONSTRAINT constraint_9 PRIMARY KEY (name, realm_id);


--
-- Name: realm_required_credential constraint_92; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_required_credential
    ADD CONSTRAINT constraint_92 PRIMARY KEY (realm_id, type);


--
-- Name: keycloak_role constraint_a; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.keycloak_role
    ADD CONSTRAINT constraint_a PRIMARY KEY (id);


--
-- Name: admin_event_entity constraint_admin_event_entity; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.admin_event_entity
    ADD CONSTRAINT constraint_admin_event_entity PRIMARY KEY (id);


--
-- Name: authenticator_config_entry constraint_auth_cfg_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authenticator_config_entry
    ADD CONSTRAINT constraint_auth_cfg_pk PRIMARY KEY (authenticator_id, name);


--
-- Name: authentication_execution constraint_auth_exec_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authentication_execution
    ADD CONSTRAINT constraint_auth_exec_pk PRIMARY KEY (id);


--
-- Name: authentication_flow constraint_auth_flow_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authentication_flow
    ADD CONSTRAINT constraint_auth_flow_pk PRIMARY KEY (id);


--
-- Name: authenticator_config constraint_auth_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authenticator_config
    ADD CONSTRAINT constraint_auth_pk PRIMARY KEY (id);


--
-- Name: user_role_mapping constraint_c; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT constraint_c PRIMARY KEY (role_id, user_id);


--
-- Name: composite_role constraint_composite_role; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.composite_role
    ADD CONSTRAINT constraint_composite_role PRIMARY KEY (composite, child_role);


--
-- Name: identity_provider_config constraint_d; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider_config
    ADD CONSTRAINT constraint_d PRIMARY KEY (identity_provider_id, name);


--
-- Name: policy_config constraint_dpc; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.policy_config
    ADD CONSTRAINT constraint_dpc PRIMARY KEY (policy_id, name);


--
-- Name: realm_smtp_config constraint_e; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_smtp_config
    ADD CONSTRAINT constraint_e PRIMARY KEY (realm_id, name);


--
-- Name: credential constraint_f; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.credential
    ADD CONSTRAINT constraint_f PRIMARY KEY (id);


--
-- Name: user_federation_config constraint_f9; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_config
    ADD CONSTRAINT constraint_f9 PRIMARY KEY (user_federation_provider_id, name);


--
-- Name: resource_server_perm_ticket constraint_fapmt; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT constraint_fapmt PRIMARY KEY (id);


--
-- Name: resource_server_resource constraint_farsr; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_resource
    ADD CONSTRAINT constraint_farsr PRIMARY KEY (id);


--
-- Name: resource_server_policy constraint_farsrp; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_policy
    ADD CONSTRAINT constraint_farsrp PRIMARY KEY (id);


--
-- Name: associated_policy constraint_farsrpap; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.associated_policy
    ADD CONSTRAINT constraint_farsrpap PRIMARY KEY (policy_id, associated_policy_id);


--
-- Name: resource_policy constraint_farsrpp; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_policy
    ADD CONSTRAINT constraint_farsrpp PRIMARY KEY (resource_id, policy_id);


--
-- Name: resource_server_scope constraint_farsrs; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_scope
    ADD CONSTRAINT constraint_farsrs PRIMARY KEY (id);


--
-- Name: resource_scope constraint_farsrsp; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_scope
    ADD CONSTRAINT constraint_farsrsp PRIMARY KEY (resource_id, scope_id);


--
-- Name: scope_policy constraint_farsrsps; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scope_policy
    ADD CONSTRAINT constraint_farsrsps PRIMARY KEY (scope_id, policy_id);


--
-- Name: user_entity constraint_fb; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_entity
    ADD CONSTRAINT constraint_fb PRIMARY KEY (id);


--
-- Name: user_federation_mapper_config constraint_fedmapper_cfg_pm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_mapper_config
    ADD CONSTRAINT constraint_fedmapper_cfg_pm PRIMARY KEY (user_federation_mapper_id, name);


--
-- Name: user_federation_mapper constraint_fedmapperpm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_mapper
    ADD CONSTRAINT constraint_fedmapperpm PRIMARY KEY (id);


--
-- Name: fed_user_consent_cl_scope constraint_fgrntcsnt_clsc_pm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.fed_user_consent_cl_scope
    ADD CONSTRAINT constraint_fgrntcsnt_clsc_pm PRIMARY KEY (user_consent_id, scope_id);


--
-- Name: user_consent_client_scope constraint_grntcsnt_clsc_pm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_consent_client_scope
    ADD CONSTRAINT constraint_grntcsnt_clsc_pm PRIMARY KEY (user_consent_id, scope_id);


--
-- Name: user_consent constraint_grntcsnt_pm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT constraint_grntcsnt_pm PRIMARY KEY (id);


--
-- Name: keycloak_group constraint_group; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.keycloak_group
    ADD CONSTRAINT constraint_group PRIMARY KEY (id);


--
-- Name: group_attribute constraint_group_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.group_attribute
    ADD CONSTRAINT constraint_group_attribute_pk PRIMARY KEY (id);


--
-- Name: group_role_mapping constraint_group_role; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.group_role_mapping
    ADD CONSTRAINT constraint_group_role PRIMARY KEY (role_id, group_id);


--
-- Name: identity_provider_mapper constraint_idpm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider_mapper
    ADD CONSTRAINT constraint_idpm PRIMARY KEY (id);


--
-- Name: idp_mapper_config constraint_idpmconfig; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.idp_mapper_config
    ADD CONSTRAINT constraint_idpmconfig PRIMARY KEY (idp_mapper_id, name);


--
-- Name: jgroups_ping constraint_jgroups_ping; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.jgroups_ping
    ADD CONSTRAINT constraint_jgroups_ping PRIMARY KEY (address);


--
-- Name: migration_model constraint_migmod; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.migration_model
    ADD CONSTRAINT constraint_migmod PRIMARY KEY (id);


--
-- Name: offline_client_session constraint_offl_cl_ses_pk3; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.offline_client_session
    ADD CONSTRAINT constraint_offl_cl_ses_pk3 PRIMARY KEY (user_session_id, client_id, client_storage_provider, external_client_id, offline_flag);


--
-- Name: offline_user_session constraint_offl_us_ses_pk2; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.offline_user_session
    ADD CONSTRAINT constraint_offl_us_ses_pk2 PRIMARY KEY (user_session_id, offline_flag);


--
-- Name: protocol_mapper constraint_pcm; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.protocol_mapper
    ADD CONSTRAINT constraint_pcm PRIMARY KEY (id);


--
-- Name: protocol_mapper_config constraint_pmconfig; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.protocol_mapper_config
    ADD CONSTRAINT constraint_pmconfig PRIMARY KEY (protocol_mapper_id, name);


--
-- Name: redirect_uris constraint_redirect_uris; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.redirect_uris
    ADD CONSTRAINT constraint_redirect_uris PRIMARY KEY (client_id, value);


--
-- Name: required_action_config constraint_req_act_cfg_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.required_action_config
    ADD CONSTRAINT constraint_req_act_cfg_pk PRIMARY KEY (required_action_id, name);


--
-- Name: required_action_provider constraint_req_act_prv_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.required_action_provider
    ADD CONSTRAINT constraint_req_act_prv_pk PRIMARY KEY (id);


--
-- Name: user_required_action constraint_required_action; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_required_action
    ADD CONSTRAINT constraint_required_action PRIMARY KEY (required_action, user_id);


--
-- Name: resource_uris constraint_resour_uris_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_uris
    ADD CONSTRAINT constraint_resour_uris_pk PRIMARY KEY (resource_id, value);


--
-- Name: role_attribute constraint_role_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.role_attribute
    ADD CONSTRAINT constraint_role_attribute_pk PRIMARY KEY (id);


--
-- Name: revoked_token constraint_rt; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.revoked_token
    ADD CONSTRAINT constraint_rt PRIMARY KEY (id);


--
-- Name: user_attribute constraint_user_attribute_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_attribute
    ADD CONSTRAINT constraint_user_attribute_pk PRIMARY KEY (id);


--
-- Name: user_group_membership constraint_user_group; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_group_membership
    ADD CONSTRAINT constraint_user_group PRIMARY KEY (group_id, user_id);


--
-- Name: web_origins constraint_web_origins; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.web_origins
    ADD CONSTRAINT constraint_web_origins PRIMARY KEY (client_id, value);


--
-- Name: databasechangeloglock databasechangeloglock_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.databasechangeloglock
    ADD CONSTRAINT databasechangeloglock_pkey PRIMARY KEY (id);


--
-- Name: client_scope_attributes pk_cl_tmpl_attr; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope_attributes
    ADD CONSTRAINT pk_cl_tmpl_attr PRIMARY KEY (scope_id, name);


--
-- Name: client_scope pk_cli_template; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope
    ADD CONSTRAINT pk_cli_template PRIMARY KEY (id);


--
-- Name: resource_server pk_resource_server; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server
    ADD CONSTRAINT pk_resource_server PRIMARY KEY (id);


--
-- Name: client_scope_role_mapping pk_template_scope; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope_role_mapping
    ADD CONSTRAINT pk_template_scope PRIMARY KEY (scope_id, role_id);


--
-- Name: default_client_scope r_def_cli_scope_bind; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.default_client_scope
    ADD CONSTRAINT r_def_cli_scope_bind PRIMARY KEY (realm_id, scope_id);


--
-- Name: realm_localizations realm_localizations_pkey; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_localizations
    ADD CONSTRAINT realm_localizations_pkey PRIMARY KEY (realm_id, locale);


--
-- Name: resource_attribute res_attr_pk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_attribute
    ADD CONSTRAINT res_attr_pk PRIMARY KEY (id);


--
-- Name: keycloak_group sibling_names; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.keycloak_group
    ADD CONSTRAINT sibling_names UNIQUE (realm_id, parent_group, name);


--
-- Name: identity_provider uk_2daelwnibji49avxsrtuf6xj33; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider
    ADD CONSTRAINT uk_2daelwnibji49avxsrtuf6xj33 UNIQUE (provider_alias, realm_id);


--
-- Name: client uk_b71cjlbenv945rb6gcon438at; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT uk_b71cjlbenv945rb6gcon438at UNIQUE (realm_id, client_id);


--
-- Name: client_scope uk_cli_scope; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope
    ADD CONSTRAINT uk_cli_scope UNIQUE (realm_id, name);


--
-- Name: user_entity uk_dykn684sl8up1crfei6eckhd7; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_entity
    ADD CONSTRAINT uk_dykn684sl8up1crfei6eckhd7 UNIQUE (realm_id, email_constraint);


--
-- Name: user_consent uk_external_consent; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT uk_external_consent UNIQUE (client_storage_provider, external_client_id, user_id);


--
-- Name: resource_server_resource uk_frsr6t700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_resource
    ADD CONSTRAINT uk_frsr6t700s9v50bu18ws5ha6 UNIQUE (name, owner, resource_server_id);


--
-- Name: resource_server_perm_ticket uk_frsr6t700s9v50bu18ws5pmt; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT uk_frsr6t700s9v50bu18ws5pmt UNIQUE (owner, requester, resource_server_id, resource_id, scope_id);


--
-- Name: resource_server_policy uk_frsrpt700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_policy
    ADD CONSTRAINT uk_frsrpt700s9v50bu18ws5ha6 UNIQUE (name, resource_server_id);


--
-- Name: resource_server_scope uk_frsrst700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_scope
    ADD CONSTRAINT uk_frsrst700s9v50bu18ws5ha6 UNIQUE (name, resource_server_id);


--
-- Name: user_consent uk_local_consent; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT uk_local_consent UNIQUE (client_id, user_id);


--
-- Name: org uk_org_alias; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT uk_org_alias UNIQUE (realm_id, alias);


--
-- Name: org uk_org_group; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT uk_org_group UNIQUE (group_id);


--
-- Name: org uk_org_name; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.org
    ADD CONSTRAINT uk_org_name UNIQUE (realm_id, name);


--
-- Name: realm uk_orvsdmla56612eaefiq6wl5oi; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm
    ADD CONSTRAINT uk_orvsdmla56612eaefiq6wl5oi UNIQUE (name);


--
-- Name: user_entity uk_ru8tt6t700s9v50bu18ws5ha6; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_entity
    ADD CONSTRAINT uk_ru8tt6t700s9v50bu18ws5ha6 UNIQUE (realm_id, username);


--
-- Name: webhook_event webhook_eventpk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_event
    ADD CONSTRAINT webhook_eventpk PRIMARY KEY (id);


--
-- Name: webhook_send webhook_sendpk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_send
    ADD CONSTRAINT webhook_sendpk PRIMARY KEY (id);


--
-- Name: webhook webhookpk; Type: CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook
    ADD CONSTRAINT webhookpk PRIMARY KEY (id);


--
-- Name: fed_user_attr_long_values; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX fed_user_attr_long_values ON public.fed_user_attribute USING btree (long_value_hash, name);


--
-- Name: fed_user_attr_long_values_lower_case; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX fed_user_attr_long_values_lower_case ON public.fed_user_attribute USING btree (long_value_hash_lower_case, name);


--
-- Name: idx_admin_event_time; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_admin_event_time ON public.admin_event_entity USING btree (realm_id, admin_event_time);


--
-- Name: idx_assoc_pol_assoc_pol_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_assoc_pol_assoc_pol_id ON public.associated_policy USING btree (associated_policy_id);


--
-- Name: idx_auth_config_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_auth_config_realm ON public.authenticator_config USING btree (realm_id);


--
-- Name: idx_auth_exec_flow; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_auth_exec_flow ON public.authentication_execution USING btree (flow_id);


--
-- Name: idx_auth_exec_realm_flow; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_auth_exec_realm_flow ON public.authentication_execution USING btree (realm_id, flow_id);


--
-- Name: idx_auth_flow_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_auth_flow_realm ON public.authentication_flow USING btree (realm_id);


--
-- Name: idx_cl_clscope; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_cl_clscope ON public.client_scope_client USING btree (scope_id);


--
-- Name: idx_client_att_by_name_value; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_client_att_by_name_value ON public.client_attributes USING btree (name, substr(value, 1, 255));


--
-- Name: idx_client_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_client_id ON public.client USING btree (client_id);


--
-- Name: idx_client_init_acc_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_client_init_acc_realm ON public.client_initial_access USING btree (realm_id);


--
-- Name: idx_clscope_attrs; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_clscope_attrs ON public.client_scope_attributes USING btree (scope_id);


--
-- Name: idx_clscope_cl; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_clscope_cl ON public.client_scope_client USING btree (client_id);


--
-- Name: idx_clscope_protmap; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_clscope_protmap ON public.protocol_mapper USING btree (client_scope_id);


--
-- Name: idx_clscope_role; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_clscope_role ON public.client_scope_role_mapping USING btree (scope_id);


--
-- Name: idx_compo_config_compo; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_compo_config_compo ON public.component_config USING btree (component_id);


--
-- Name: idx_component_provider_type; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_component_provider_type ON public.component USING btree (provider_type);


--
-- Name: idx_component_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_component_realm ON public.component USING btree (realm_id);


--
-- Name: idx_composite; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_composite ON public.composite_role USING btree (composite);


--
-- Name: idx_composite_child; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_composite_child ON public.composite_role USING btree (child_role);


--
-- Name: idx_defcls_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_defcls_realm ON public.default_client_scope USING btree (realm_id);


--
-- Name: idx_defcls_scope; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_defcls_scope ON public.default_client_scope USING btree (scope_id);


--
-- Name: idx_event_time; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_event_time ON public.event_entity USING btree (realm_id, event_time);


--
-- Name: idx_fedidentity_feduser; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fedidentity_feduser ON public.federated_identity USING btree (federated_user_id);


--
-- Name: idx_fedidentity_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fedidentity_user ON public.federated_identity USING btree (user_id);


--
-- Name: idx_fu_attribute; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_attribute ON public.fed_user_attribute USING btree (user_id, realm_id, name);


--
-- Name: idx_fu_cnsnt_ext; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_cnsnt_ext ON public.fed_user_consent USING btree (user_id, client_storage_provider, external_client_id);


--
-- Name: idx_fu_consent; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_consent ON public.fed_user_consent USING btree (user_id, client_id);


--
-- Name: idx_fu_consent_ru; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_consent_ru ON public.fed_user_consent USING btree (realm_id, user_id);


--
-- Name: idx_fu_credential; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_credential ON public.fed_user_credential USING btree (user_id, type);


--
-- Name: idx_fu_credential_ru; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_credential_ru ON public.fed_user_credential USING btree (realm_id, user_id);


--
-- Name: idx_fu_group_membership; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_group_membership ON public.fed_user_group_membership USING btree (user_id, group_id);


--
-- Name: idx_fu_group_membership_ru; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_group_membership_ru ON public.fed_user_group_membership USING btree (realm_id, user_id);


--
-- Name: idx_fu_required_action; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_required_action ON public.fed_user_required_action USING btree (user_id, required_action);


--
-- Name: idx_fu_required_action_ru; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_required_action_ru ON public.fed_user_required_action USING btree (realm_id, user_id);


--
-- Name: idx_fu_role_mapping; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_role_mapping ON public.fed_user_role_mapping USING btree (user_id, role_id);


--
-- Name: idx_fu_role_mapping_ru; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_fu_role_mapping_ru ON public.fed_user_role_mapping USING btree (realm_id, user_id);


--
-- Name: idx_group_att_by_name_value; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_group_att_by_name_value ON public.group_attribute USING btree (name, ((value)::character varying(250)));


--
-- Name: idx_group_attr_group; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_group_attr_group ON public.group_attribute USING btree (group_id);


--
-- Name: idx_group_role_mapp_group; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_group_role_mapp_group ON public.group_role_mapping USING btree (group_id);


--
-- Name: idx_id_prov_mapp_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_id_prov_mapp_realm ON public.identity_provider_mapper USING btree (realm_id);


--
-- Name: idx_ident_prov_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_ident_prov_realm ON public.identity_provider USING btree (realm_id);


--
-- Name: idx_idp_for_login; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_idp_for_login ON public.identity_provider USING btree (realm_id, enabled, link_only, hide_on_login, organization_id);


--
-- Name: idx_idp_realm_org; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_idp_realm_org ON public.identity_provider USING btree (realm_id, organization_id);


--
-- Name: idx_keycloak_role_client; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_keycloak_role_client ON public.keycloak_role USING btree (client);


--
-- Name: idx_keycloak_role_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_keycloak_role_realm ON public.keycloak_role USING btree (realm);


--
-- Name: idx_offline_uss_by_broker_session_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_offline_uss_by_broker_session_id ON public.offline_user_session USING btree (broker_session_id, realm_id);


--
-- Name: idx_offline_uss_by_last_session_refresh; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_offline_uss_by_last_session_refresh ON public.offline_user_session USING btree (realm_id, offline_flag, last_session_refresh);


--
-- Name: idx_offline_uss_by_user; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_offline_uss_by_user ON public.offline_user_session USING btree (user_id, realm_id, offline_flag);


--
-- Name: idx_org_domain_org_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_org_domain_org_id ON public.org_domain USING btree (org_id);


--
-- Name: idx_perm_ticket_owner; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_perm_ticket_owner ON public.resource_server_perm_ticket USING btree (owner);


--
-- Name: idx_perm_ticket_requester; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_perm_ticket_requester ON public.resource_server_perm_ticket USING btree (requester);


--
-- Name: idx_protocol_mapper_client; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_protocol_mapper_client ON public.protocol_mapper USING btree (client_id);


--
-- Name: idx_realm_attr_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_attr_realm ON public.realm_attribute USING btree (realm_id);


--
-- Name: idx_realm_clscope; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_clscope ON public.client_scope USING btree (realm_id);


--
-- Name: idx_realm_def_grp_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_def_grp_realm ON public.realm_default_groups USING btree (realm_id);


--
-- Name: idx_realm_evt_list_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_evt_list_realm ON public.realm_events_listeners USING btree (realm_id);


--
-- Name: idx_realm_evt_types_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_evt_types_realm ON public.realm_enabled_event_types USING btree (realm_id);


--
-- Name: idx_realm_master_adm_cli; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_master_adm_cli ON public.realm USING btree (master_admin_client);


--
-- Name: idx_realm_supp_local_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_realm_supp_local_realm ON public.realm_supported_locales USING btree (realm_id);


--
-- Name: idx_redir_uri_client; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_redir_uri_client ON public.redirect_uris USING btree (client_id);


--
-- Name: idx_req_act_prov_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_req_act_prov_realm ON public.required_action_provider USING btree (realm_id);


--
-- Name: idx_res_policy_policy; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_res_policy_policy ON public.resource_policy USING btree (policy_id);


--
-- Name: idx_res_scope_scope; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_res_scope_scope ON public.resource_scope USING btree (scope_id);


--
-- Name: idx_res_serv_pol_res_serv; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_res_serv_pol_res_serv ON public.resource_server_policy USING btree (resource_server_id);


--
-- Name: idx_res_srv_res_res_srv; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_res_srv_res_res_srv ON public.resource_server_resource USING btree (resource_server_id);


--
-- Name: idx_res_srv_scope_res_srv; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_res_srv_scope_res_srv ON public.resource_server_scope USING btree (resource_server_id);


--
-- Name: idx_rev_token_on_expire; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_rev_token_on_expire ON public.revoked_token USING btree (expire);


--
-- Name: idx_role_attribute; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_role_attribute ON public.role_attribute USING btree (role_id);


--
-- Name: idx_role_clscope; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_role_clscope ON public.client_scope_role_mapping USING btree (role_id);


--
-- Name: idx_scope_mapping_role; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_scope_mapping_role ON public.scope_mapping USING btree (role_id);


--
-- Name: idx_scope_policy_policy; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_scope_policy_policy ON public.scope_policy USING btree (policy_id);


--
-- Name: idx_update_time; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_update_time ON public.migration_model USING btree (update_time);


--
-- Name: idx_usconsent_clscope; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usconsent_clscope ON public.user_consent_client_scope USING btree (user_consent_id);


--
-- Name: idx_usconsent_scope_id; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usconsent_scope_id ON public.user_consent_client_scope USING btree (scope_id);


--
-- Name: idx_user_attribute; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_attribute ON public.user_attribute USING btree (user_id);


--
-- Name: idx_user_attribute_name; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_attribute_name ON public.user_attribute USING btree (name, value);


--
-- Name: idx_user_consent; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_consent ON public.user_consent USING btree (user_id);


--
-- Name: idx_user_credential; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_credential ON public.credential USING btree (user_id);


--
-- Name: idx_user_email; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_email ON public.user_entity USING btree (email);


--
-- Name: idx_user_group_mapping; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_group_mapping ON public.user_group_membership USING btree (user_id);


--
-- Name: idx_user_reqactions; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_reqactions ON public.user_required_action USING btree (user_id);


--
-- Name: idx_user_role_mapping; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_role_mapping ON public.user_role_mapping USING btree (user_id);


--
-- Name: idx_user_service_account; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_user_service_account ON public.user_entity USING btree (realm_id, service_account_client_link);


--
-- Name: idx_usr_fed_map_fed_prv; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usr_fed_map_fed_prv ON public.user_federation_mapper USING btree (federation_provider_id);


--
-- Name: idx_usr_fed_map_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usr_fed_map_realm ON public.user_federation_mapper USING btree (realm_id);


--
-- Name: idx_usr_fed_prv_realm; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_usr_fed_prv_realm ON public.user_federation_provider USING btree (realm_id);


--
-- Name: idx_web_orig_client; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX idx_web_orig_client ON public.web_origins USING btree (client_id);


--
-- Name: user_attr_long_values; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX user_attr_long_values ON public.user_attribute USING btree (long_value_hash, name);


--
-- Name: user_attr_long_values_lower_case; Type: INDEX; Schema: public; Owner: admin
--

CREATE INDEX user_attr_long_values_lower_case ON public.user_attribute USING btree (long_value_hash_lower_case, name);


--
-- Name: identity_provider fk2b4ebc52ae5c3b34; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider
    ADD CONSTRAINT fk2b4ebc52ae5c3b34 FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: client_attributes fk3c47c64beacca966; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_attributes
    ADD CONSTRAINT fk3c47c64beacca966 FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: federated_identity fk404288b92ef007a6; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.federated_identity
    ADD CONSTRAINT fk404288b92ef007a6 FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: client_node_registrations fk4129723ba992f594; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_node_registrations
    ADD CONSTRAINT fk4129723ba992f594 FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: redirect_uris fk_1burs8pb4ouj97h5wuppahv9f; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.redirect_uris
    ADD CONSTRAINT fk_1burs8pb4ouj97h5wuppahv9f FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: user_federation_provider fk_1fj32f6ptolw2qy60cd8n01e8; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_provider
    ADD CONSTRAINT fk_1fj32f6ptolw2qy60cd8n01e8 FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: realm_required_credential fk_5hg65lybevavkqfki3kponh9v; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_required_credential
    ADD CONSTRAINT fk_5hg65lybevavkqfki3kponh9v FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: resource_attribute fk_5hrm2vlf9ql5fu022kqepovbr; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_attribute
    ADD CONSTRAINT fk_5hrm2vlf9ql5fu022kqepovbr FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: user_attribute fk_5hrm2vlf9ql5fu043kqepovbr; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_attribute
    ADD CONSTRAINT fk_5hrm2vlf9ql5fu043kqepovbr FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: user_required_action fk_6qj3w1jw9cvafhe19bwsiuvmd; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_required_action
    ADD CONSTRAINT fk_6qj3w1jw9cvafhe19bwsiuvmd FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: keycloak_role fk_6vyqfe4cn4wlq8r6kt5vdsj5c; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.keycloak_role
    ADD CONSTRAINT fk_6vyqfe4cn4wlq8r6kt5vdsj5c FOREIGN KEY (realm) REFERENCES public.realm(id);


--
-- Name: realm_smtp_config fk_70ej8xdxgxd0b9hh6180irr0o; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_smtp_config
    ADD CONSTRAINT fk_70ej8xdxgxd0b9hh6180irr0o FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: webhook_event fk_77mtitm94zpozjiy2af0tadfs; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_event
    ADD CONSTRAINT fk_77mtitm94zpozjiy2af0tadfs FOREIGN KEY (admin_event_id) REFERENCES public.admin_event_entity(id) ON DELETE CASCADE;


--
-- Name: realm_attribute fk_8shxd6l3e9atqukacxgpffptw; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_attribute
    ADD CONSTRAINT fk_8shxd6l3e9atqukacxgpffptw FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: composite_role fk_a63wvekftu8jo1pnj81e7mce2; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.composite_role
    ADD CONSTRAINT fk_a63wvekftu8jo1pnj81e7mce2 FOREIGN KEY (composite) REFERENCES public.keycloak_role(id);


--
-- Name: authentication_execution fk_auth_exec_flow; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authentication_execution
    ADD CONSTRAINT fk_auth_exec_flow FOREIGN KEY (flow_id) REFERENCES public.authentication_flow(id);


--
-- Name: authentication_execution fk_auth_exec_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authentication_execution
    ADD CONSTRAINT fk_auth_exec_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: authentication_flow fk_auth_flow_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authentication_flow
    ADD CONSTRAINT fk_auth_flow_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: authenticator_config fk_auth_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.authenticator_config
    ADD CONSTRAINT fk_auth_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: webhook_send fk_b5wfy7zzy2ssx72df6yvrpp06; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_send
    ADD CONSTRAINT fk_b5wfy7zzy2ssx72df6yvrpp06 FOREIGN KEY (webhook_event_id) REFERENCES public.webhook_event(id) ON DELETE CASCADE;


--
-- Name: user_role_mapping fk_c4fqv34p1mbylloxang7b1q3l; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_role_mapping
    ADD CONSTRAINT fk_c4fqv34p1mbylloxang7b1q3l FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: client_scope_attributes fk_cl_scope_attr_scope; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope_attributes
    ADD CONSTRAINT fk_cl_scope_attr_scope FOREIGN KEY (scope_id) REFERENCES public.client_scope(id);


--
-- Name: client_scope_role_mapping fk_cl_scope_rm_scope; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_scope_role_mapping
    ADD CONSTRAINT fk_cl_scope_rm_scope FOREIGN KEY (scope_id) REFERENCES public.client_scope(id);


--
-- Name: protocol_mapper fk_cli_scope_mapper; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.protocol_mapper
    ADD CONSTRAINT fk_cli_scope_mapper FOREIGN KEY (client_scope_id) REFERENCES public.client_scope(id);


--
-- Name: client_initial_access fk_client_init_acc_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.client_initial_access
    ADD CONSTRAINT fk_client_init_acc_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: component_config fk_component_config; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.component_config
    ADD CONSTRAINT fk_component_config FOREIGN KEY (component_id) REFERENCES public.component(id);


--
-- Name: component fk_component_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.component
    ADD CONSTRAINT fk_component_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: realm_default_groups fk_def_groups_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_default_groups
    ADD CONSTRAINT fk_def_groups_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: user_federation_mapper_config fk_fedmapper_cfg; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_mapper_config
    ADD CONSTRAINT fk_fedmapper_cfg FOREIGN KEY (user_federation_mapper_id) REFERENCES public.user_federation_mapper(id);


--
-- Name: user_federation_mapper fk_fedmapperpm_fedprv; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_mapper
    ADD CONSTRAINT fk_fedmapperpm_fedprv FOREIGN KEY (federation_provider_id) REFERENCES public.user_federation_provider(id);


--
-- Name: user_federation_mapper fk_fedmapperpm_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_mapper
    ADD CONSTRAINT fk_fedmapperpm_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: associated_policy fk_frsr5s213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.associated_policy
    ADD CONSTRAINT fk_frsr5s213xcx4wnkog82ssrfy FOREIGN KEY (associated_policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: scope_policy fk_frsrasp13xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scope_policy
    ADD CONSTRAINT fk_frsrasp13xcx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: resource_server_perm_ticket fk_frsrho213xcx4wnkog82sspmt; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrho213xcx4wnkog82sspmt FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: resource_server_resource fk_frsrho213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_resource
    ADD CONSTRAINT fk_frsrho213xcx4wnkog82ssrfy FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: resource_server_perm_ticket fk_frsrho213xcx4wnkog83sspmt; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrho213xcx4wnkog83sspmt FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: resource_server_perm_ticket fk_frsrho213xcx4wnkog84sspmt; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrho213xcx4wnkog84sspmt FOREIGN KEY (scope_id) REFERENCES public.resource_server_scope(id);


--
-- Name: associated_policy fk_frsrpas14xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.associated_policy
    ADD CONSTRAINT fk_frsrpas14xcx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: scope_policy fk_frsrpass3xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scope_policy
    ADD CONSTRAINT fk_frsrpass3xcx4wnkog82ssrfy FOREIGN KEY (scope_id) REFERENCES public.resource_server_scope(id);


--
-- Name: resource_server_perm_ticket fk_frsrpo2128cx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_perm_ticket
    ADD CONSTRAINT fk_frsrpo2128cx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: resource_server_policy fk_frsrpo213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_policy
    ADD CONSTRAINT fk_frsrpo213xcx4wnkog82ssrfy FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: resource_scope fk_frsrpos13xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_scope
    ADD CONSTRAINT fk_frsrpos13xcx4wnkog82ssrfy FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: resource_policy fk_frsrpos53xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_policy
    ADD CONSTRAINT fk_frsrpos53xcx4wnkog82ssrfy FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: resource_policy fk_frsrpp213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_policy
    ADD CONSTRAINT fk_frsrpp213xcx4wnkog82ssrfy FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: resource_scope fk_frsrps213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_scope
    ADD CONSTRAINT fk_frsrps213xcx4wnkog82ssrfy FOREIGN KEY (scope_id) REFERENCES public.resource_server_scope(id);


--
-- Name: resource_server_scope fk_frsrso213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_server_scope
    ADD CONSTRAINT fk_frsrso213xcx4wnkog82ssrfy FOREIGN KEY (resource_server_id) REFERENCES public.resource_server(id);


--
-- Name: composite_role fk_gr7thllb9lu8q4vqa4524jjy8; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.composite_role
    ADD CONSTRAINT fk_gr7thllb9lu8q4vqa4524jjy8 FOREIGN KEY (child_role) REFERENCES public.keycloak_role(id);


--
-- Name: user_consent_client_scope fk_grntcsnt_clsc_usc; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_consent_client_scope
    ADD CONSTRAINT fk_grntcsnt_clsc_usc FOREIGN KEY (user_consent_id) REFERENCES public.user_consent(id);


--
-- Name: user_consent fk_grntcsnt_user; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_consent
    ADD CONSTRAINT fk_grntcsnt_user FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: group_attribute fk_group_attribute_group; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.group_attribute
    ADD CONSTRAINT fk_group_attribute_group FOREIGN KEY (group_id) REFERENCES public.keycloak_group(id);


--
-- Name: group_role_mapping fk_group_role_group; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.group_role_mapping
    ADD CONSTRAINT fk_group_role_group FOREIGN KEY (group_id) REFERENCES public.keycloak_group(id);


--
-- Name: realm_enabled_event_types fk_h846o4h0w8epx5nwedrf5y69j; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_enabled_event_types
    ADD CONSTRAINT fk_h846o4h0w8epx5nwedrf5y69j FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: realm_events_listeners fk_h846o4h0w8epx5nxev9f5y69j; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_events_listeners
    ADD CONSTRAINT fk_h846o4h0w8epx5nxev9f5y69j FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: webhook_event_types fk_h84rsk1gfrpjgwmn21upw149j; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_event_types
    ADD CONSTRAINT fk_h84rsk1gfrpjgwmn21upw149j FOREIGN KEY (webhook_id) REFERENCES public.webhook(id);


--
-- Name: identity_provider_mapper fk_idpm_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider_mapper
    ADD CONSTRAINT fk_idpm_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: idp_mapper_config fk_idpmconfig; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.idp_mapper_config
    ADD CONSTRAINT fk_idpmconfig FOREIGN KEY (idp_mapper_id) REFERENCES public.identity_provider_mapper(id);


--
-- Name: web_origins fk_lojpho213xcx4wnkog82ssrfy; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.web_origins
    ADD CONSTRAINT fk_lojpho213xcx4wnkog82ssrfy FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: scope_mapping fk_ouse064plmlr732lxjcn1q5f1; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.scope_mapping
    ADD CONSTRAINT fk_ouse064plmlr732lxjcn1q5f1 FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: protocol_mapper fk_pcm_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.protocol_mapper
    ADD CONSTRAINT fk_pcm_realm FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: credential fk_pfyr0glasqyl0dei3kl69r6v0; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.credential
    ADD CONSTRAINT fk_pfyr0glasqyl0dei3kl69r6v0 FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: webhook_event fk_pkcqew0vy67vp2rb4t8co7nwj; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_event
    ADD CONSTRAINT fk_pkcqew0vy67vp2rb4t8co7nwj FOREIGN KEY (event_id) REFERENCES public.event_entity(id) ON DELETE CASCADE;


--
-- Name: webhook_send fk_pmau51lz70wuixrhq4ce83466; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.webhook_send
    ADD CONSTRAINT fk_pmau51lz70wuixrhq4ce83466 FOREIGN KEY (webhook_id) REFERENCES public.webhook(id) ON DELETE CASCADE;


--
-- Name: protocol_mapper_config fk_pmconfig; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.protocol_mapper_config
    ADD CONSTRAINT fk_pmconfig FOREIGN KEY (protocol_mapper_id) REFERENCES public.protocol_mapper(id);


--
-- Name: default_client_scope fk_r_def_cli_scope_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.default_client_scope
    ADD CONSTRAINT fk_r_def_cli_scope_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: required_action_provider fk_req_act_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.required_action_provider
    ADD CONSTRAINT fk_req_act_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: resource_uris fk_resource_server_uris; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.resource_uris
    ADD CONSTRAINT fk_resource_server_uris FOREIGN KEY (resource_id) REFERENCES public.resource_server_resource(id);


--
-- Name: role_attribute fk_role_attribute_id; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.role_attribute
    ADD CONSTRAINT fk_role_attribute_id FOREIGN KEY (role_id) REFERENCES public.keycloak_role(id);


--
-- Name: realm_supported_locales fk_supported_locales_realm; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.realm_supported_locales
    ADD CONSTRAINT fk_supported_locales_realm FOREIGN KEY (realm_id) REFERENCES public.realm(id);


--
-- Name: user_federation_config fk_t13hpu1j94r2ebpekr39x5eu5; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_federation_config
    ADD CONSTRAINT fk_t13hpu1j94r2ebpekr39x5eu5 FOREIGN KEY (user_federation_provider_id) REFERENCES public.user_federation_provider(id);


--
-- Name: user_group_membership fk_user_group_user; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.user_group_membership
    ADD CONSTRAINT fk_user_group_user FOREIGN KEY (user_id) REFERENCES public.user_entity(id);


--
-- Name: policy_config fkdc34197cf864c4e43; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.policy_config
    ADD CONSTRAINT fkdc34197cf864c4e43 FOREIGN KEY (policy_id) REFERENCES public.resource_server_policy(id);


--
-- Name: identity_provider_config fkdc4897cf864c4e43; Type: FK CONSTRAINT; Schema: public; Owner: admin
--

ALTER TABLE ONLY public.identity_provider_config
    ADD CONSTRAINT fkdc4897cf864c4e43 FOREIGN KEY (identity_provider_id) REFERENCES public.identity_provider(internal_id);


--
-- PostgreSQL database dump complete
--

\unrestrict GFY7KexulMgJsyQzdfOYDaaHxVRB81u0Jyz9CR5zp9dKay95Ltj0PzvuYB7ahBG

