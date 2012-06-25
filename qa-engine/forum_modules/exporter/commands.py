PG_SEQUENCE_RESETS = """
SELECT setval('"auth_user_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user";
SELECT setval('"auth_user_groups_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user_groups";
SELECT setval('"auth_user_user_permissions_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "auth_user_user_permissions";
SELECT setval('"forum_keyvalue_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_keyvalue";
SELECT setval('"forum_action_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_action";
SELECT setval('"forum_actionrepute_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_actionrepute";
SELECT setval('"forum_subscriptionsettings_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_subscriptionsettings";
SELECT setval('"forum_validationhash_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_validationhash";
SELECT setval('"forum_authkeyuserassociation_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_authkeyuserassociation";
SELECT setval('"forum_tag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_tag";
SELECT setval('"forum_markedtag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_markedtag";
SELECT setval('"forum_node_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node";
SELECT setval('"forum_nodestate_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_nodestate";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_noderevision_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_noderevision";
SELECT setval('"forum_node_tags_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_node_tags";
SELECT setval('"forum_questionsubscription_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_questionsubscription";
SELECT setval('"forum_vote_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_vote";
SELECT setval('"forum_flag_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_flag";
SELECT setval('"forum_badge_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_badge";
SELECT setval('"forum_award_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_award";
SELECT setval('"forum_openidnonce_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_openidnonce";
SELECT setval('"forum_openidassociation_id_seq"', coalesce(max("id"), 1) + 2, max("id") IS NOT null) FROM "forum_openidassociation";
"""

PG_DISABLE_TRIGGERS = """
ALTER table auth_user DISABLE TRIGGER ALL;
ALTER table auth_user_groups DISABLE TRIGGER ALL;
ALTER table auth_user_user_permissions DISABLE TRIGGER ALL;
ALTER table forum_keyvalue DISABLE TRIGGER ALL;
ALTER table forum_action DISABLE TRIGGER ALL;
ALTER table forum_actionrepute DISABLE TRIGGER ALL;
ALTER table forum_subscriptionsettings DISABLE TRIGGER ALL;
ALTER table forum_validationhash DISABLE TRIGGER ALL;
ALTER table forum_authkeyuserassociation DISABLE TRIGGER ALL;
ALTER table forum_tag DISABLE TRIGGER ALL;
ALTER table forum_markedtag DISABLE TRIGGER ALL;
ALTER table forum_node DISABLE TRIGGER ALL;
ALTER table forum_nodestate DISABLE TRIGGER ALL;
ALTER table forum_node_tags DISABLE TRIGGER ALL;
ALTER table forum_noderevision DISABLE TRIGGER ALL;
ALTER table forum_node_tags DISABLE TRIGGER ALL;
ALTER table forum_questionsubscription DISABLE TRIGGER ALL;
ALTER table forum_vote DISABLE TRIGGER ALL;
ALTER table forum_flag DISABLE TRIGGER ALL;
ALTER table forum_badge DISABLE TRIGGER ALL;
ALTER table forum_award DISABLE TRIGGER ALL;
ALTER table forum_openidnonce DISABLE TRIGGER ALL;
ALTER table forum_openidassociation DISABLE TRIGGER ALL;
"""

PG_ENABLE_TRIGGERS = """
ALTER table auth_user ENABLE TRIGGER ALL;
ALTER table auth_user_groups ENABLE TRIGGER ALL;
ALTER table auth_user_user_permissions ENABLE TRIGGER ALL;
ALTER table forum_keyvalue ENABLE TRIGGER ALL;
ALTER table forum_action ENABLE TRIGGER ALL;
ALTER table forum_actionrepute ENABLE TRIGGER ALL;
ALTER table forum_subscriptionsettings ENABLE TRIGGER ALL;
ALTER table forum_validationhash ENABLE TRIGGER ALL;
ALTER table forum_authkeyuserassociation ENABLE TRIGGER ALL;
ALTER table forum_tag ENABLE TRIGGER ALL;
ALTER table forum_markedtag ENABLE TRIGGER ALL;
ALTER table forum_node ENABLE TRIGGER ALL;
ALTER table forum_nodestate ENABLE TRIGGER ALL;
ALTER table forum_node_tags ENABLE TRIGGER ALL;
ALTER table forum_noderevision ENABLE TRIGGER ALL;
ALTER table forum_node_tags ENABLE TRIGGER ALL;
ALTER table forum_questionsubscription ENABLE TRIGGER ALL;
ALTER table forum_vote ENABLE TRIGGER ALL;
ALTER table forum_flag ENABLE TRIGGER ALL;
ALTER table forum_badge ENABLE TRIGGER ALL;
ALTER table forum_award ENABLE TRIGGER ALL;
ALTER table forum_openidnonce ENABLE TRIGGER ALL;
ALTER table forum_openidassociation ENABLE TRIGGER ALL;
"""