
PG_MIGRATION_QUERY = """
SELECT id AS user_ptr_id, is_approved, email_isvalid, email_key, reputation, gravatar, gold, silver, bronze, questions_per_page, last_seen, real_name, website, location, date_of_birth, about, hide_ignored_questions, tag_filter_setting INTO forum_user FROM auth_user;

ALTER TABLE forum_user
  ADD CONSTRAINT forum_user_pkey PRIMARY KEY(user_ptr_id);

ALTER TABLE forum_user
  ADD CONSTRAINT forum_user_user_ptr_id_fkey FOREIGN KEY (user_ptr_id)
      REFERENCES auth_user (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE forum_user
  ADD CONSTRAINT forum_user_reputation_check CHECK (reputation >= 0);

ALTER TABLE auth_user DROP COLUMN is_approved;
ALTER TABLE auth_user DROP COLUMN email_isvalid;
ALTER TABLE auth_user DROP COLUMN email_key;
ALTER TABLE auth_user DROP COLUMN reputation;
ALTER TABLE auth_user DROP COLUMN gravatar;
ALTER TABLE auth_user DROP COLUMN gold;
ALTER TABLE auth_user DROP COLUMN silver;
ALTER TABLE auth_user DROP COLUMN bronze;
ALTER TABLE auth_user DROP COLUMN questions_per_page;
ALTER TABLE auth_user DROP COLUMN last_seen;
ALTER TABLE auth_user DROP COLUMN real_name;
ALTER TABLE auth_user DROP COLUMN website;
ALTER TABLE auth_user DROP COLUMN "location";
ALTER TABLE auth_user DROP COLUMN date_of_birth;
ALTER TABLE auth_user DROP COLUMN about;
ALTER TABLE auth_user DROP COLUMN hide_ignored_questions;
ALTER TABLE auth_user DROP COLUMN tag_filter_setting;

"""

PG_FKEYS_QUERY = """

ALTER TABLE "public"."activity"
DROP CONSTRAINT "activity_user_id_fkey",
ADD CONSTRAINT "activity_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."answer"
DROP CONSTRAINT "answer_author_id_fkey",
ADD CONSTRAINT "answer_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "answer_deleted_by_id_fkey",
ADD CONSTRAINT "answer_deleted_by_id_fkey" FOREIGN KEY ("deleted_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "answer_last_edited_by_id_fkey",
ADD CONSTRAINT "answer_last_edited_by_id_fkey" FOREIGN KEY ("last_edited_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "answer_locked_by_id_fkey",
ADD CONSTRAINT "answer_locked_by_id_fkey" FOREIGN KEY ("locked_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."answer_revision"
DROP CONSTRAINT "answer_revision_author_id_fkey",
ADD CONSTRAINT "answer_revision_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."award"
DROP CONSTRAINT "award_user_id_fkey",
ADD CONSTRAINT "award_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."comment"
DROP CONSTRAINT "comment_user_id_fkey",
ADD CONSTRAINT "comment_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."favorite_question"
DROP CONSTRAINT "favorite_question_user_id_fkey",
ADD CONSTRAINT "favorite_question_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."flagged_item"
DROP CONSTRAINT "flagged_item_user_id_fkey",
ADD CONSTRAINT "flagged_item_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_anonymousanswer"
DROP CONSTRAINT "forum_anonymousanswer_author_id_fkey",
ADD CONSTRAINT "forum_anonymousanswer_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_anonymousquestion"
DROP CONSTRAINT "forum_anonymousquestion_author_id_fkey",
ADD CONSTRAINT "forum_anonymousquestion_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_authkeyuserassociation"
DROP CONSTRAINT "forum_authkeyuserassociation_user_id_fkey",
ADD CONSTRAINT "forum_authkeyuserassociation_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_markedtag"
DROP CONSTRAINT "forum_markedtag_user_id_fkey",
ADD CONSTRAINT "forum_markedtag_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_questionsubscription"
DROP CONSTRAINT "forum_questionsubscription_user_id_fkey",
ADD CONSTRAINT "forum_questionsubscription_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_subscriptionsettings"
DROP CONSTRAINT "forum_subscriptionsettings_user_id_fkey",
ADD CONSTRAINT "forum_subscriptionsettings_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."forum_validationhash"
DROP CONSTRAINT "forum_validationhash_user_id_fkey",
ADD CONSTRAINT "forum_validationhash_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."question"
DROP CONSTRAINT "question_author_id_fkey",
ADD CONSTRAINT "question_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "question_closed_by_id_fkey",
ADD CONSTRAINT "question_closed_by_id_fkey" FOREIGN KEY ("closed_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "question_deleted_by_id_fkey",
ADD CONSTRAINT "question_deleted_by_id_fkey" FOREIGN KEY ("deleted_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "question_last_activity_by_id_fkey",
ADD CONSTRAINT "question_last_activity_by_id_fkey" FOREIGN KEY ("last_activity_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "question_last_edited_by_id_fkey",
ADD CONSTRAINT "question_last_edited_by_id_fkey" FOREIGN KEY ("last_edited_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "question_locked_by_id_fkey",
ADD CONSTRAINT "question_locked_by_id_fkey" FOREIGN KEY ("locked_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."question_followed_by"
DROP CONSTRAINT "question_followed_by_user_id_fkey",
ADD CONSTRAINT "question_followed_by_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."question_revision"
DROP CONSTRAINT "question_revision_author_id_fkey",
ADD CONSTRAINT "question_revision_author_id_fkey" FOREIGN KEY ("author_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."repute"
DROP CONSTRAINT "repute_user_id_fkey",
ADD CONSTRAINT "repute_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."tag"
DROP CONSTRAINT "tag_created_by_id_fkey",
ADD CONSTRAINT "tag_created_by_id_fkey" FOREIGN KEY ("created_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED,
DROP CONSTRAINT "tag_deleted_by_id_fkey",
ADD CONSTRAINT "tag_deleted_by_id_fkey" FOREIGN KEY ("deleted_by_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

ALTER TABLE "public"."vote"
DROP CONSTRAINT "vote_user_id_fkey",
ADD CONSTRAINT "vote_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "public"."forum_user" (user_ptr_id) ON DELETE NO ACTION ON UPDATE NO ACTION DEFERRABLE INITIALLY DEFERRED;

"""

MYSQL_MIGRATION_QUERY = """
CREATE TABLE `forum_user` (
  `user_ptr_id` int(11) NOT NULL,
  `is_approved` tinyint(1) NOT NULL,
  `email_isvalid` tinyint(1) NOT NULL,
  `email_key` varchar(32) DEFAULT NULL,
  `reputation` int(10) unsigned NOT NULL,
  `gravatar` varchar(32) NOT NULL,
  `gold` smallint(6) NOT NULL,
  `silver` smallint(6) NOT NULL,
  `bronze` smallint(6) NOT NULL,
  `questions_per_page` smallint(6) NOT NULL,
  `last_seen` datetime NOT NULL,
  `real_name` varchar(100) NOT NULL,
  `website` varchar(200) NOT NULL,
  `location` varchar(100) NOT NULL,
  `date_of_birth` date DEFAULT NULL,
  `about` longtext NOT NULL,
  `hide_ignored_questions` tinyint(1) NOT NULL,
  `tag_filter_setting` varchar(16) NOT NULL,
  PRIMARY KEY (`user_ptr_id`),
  CONSTRAINT `user_ptr_id_refs_id_71071d7` FOREIGN KEY (`user_ptr_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8
SELECT id AS user_ptr_id, is_approved, email_isvalid, email_key, reputation, gravatar, gold, silver, bronze, questions_per_page,
	last_seen, real_name, website, location, date_of_birth, about, hide_ignored_questions, tag_filter_setting FROM auth_user;

ALTER TABLE `auth_user`
DROP COLUMN `is_approved`,
DROP COLUMN `email_isvalid`,
DROP COLUMN `email_key`,
DROP COLUMN `reputation`,
DROP COLUMN `gravatar`,
DROP COLUMN `gold`,
DROP COLUMN `silver`,
DROP COLUMN `bronze`,
DROP COLUMN `questions_per_page`,
DROP COLUMN `last_seen`,
DROP COLUMN `real_name`,
DROP COLUMN `website`,
DROP COLUMN `location`,
DROP COLUMN `date_of_birth`,
DROP COLUMN `about`,
DROP COLUMN `hide_ignored_questions`,
DROP COLUMN `tag_filter_setting`;

"""

MYSQL_FKEYS_QUERY = """

ALTER TABLE `activity` DROP FOREIGN KEY `user_id_refs_id_47c8583f`;
ALTER TABLE `activity` ADD CONSTRAINT `user_id_refs_user_ptr_id_62ae9785` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `answer` DROP FOREIGN KEY `author_id_refs_id_192b0170`;
ALTER TABLE `answer` ADD CONSTRAINT `author_id_refs_user_ptr_id_9681994` FOREIGN KEY (`author_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `answer` DROP FOREIGN KEY `deleted_by_id_refs_id_192b0170`;
ALTER TABLE `answer` ADD CONSTRAINT `deleted_by_id_refs_user_ptr_id_9681994` FOREIGN KEY (`deleted_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `answer` DROP FOREIGN KEY `last_edited_by_id_refs_id_192b0170`;
ALTER TABLE `answer` ADD CONSTRAINT `last_edited_by_id_refs_user_ptr_id_9681994` FOREIGN KEY (`last_edited_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `answer` DROP FOREIGN KEY `locked_by_id_refs_id_192b0170`;
ALTER TABLE `answer` ADD CONSTRAINT `locked_by_id_refs_user_ptr_id_9681994` FOREIGN KEY (`locked_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `answer_revision` DROP FOREIGN KEY `author_id_refs_id_3ccc055f`;
ALTER TABLE `answer_revision` ADD CONSTRAINT `author_id_refs_user_ptr_id_331f0123` FOREIGN KEY (`author_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `award` DROP FOREIGN KEY `user_id_refs_id_2d83e9b6`;
ALTER TABLE `award` ADD CONSTRAINT `user_id_refs_user_ptr_id_1b2d0192` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `comment` DROP FOREIGN KEY `user_id_refs_id_6be725e8`;
ALTER TABLE `comment` ADD CONSTRAINT `user_id_refs_user_ptr_id_1ac2320c` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `favorite_question` DROP FOREIGN KEY `user_id_refs_id_52853822`;
ALTER TABLE `favorite_question` ADD CONSTRAINT `user_id_refs_user_ptr_id_3f419c1a` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `flagged_item` DROP FOREIGN KEY `user_id_refs_id_35e3c608`;
ALTER TABLE `flagged_item` ADD CONSTRAINT `user_id_refs_user_ptr_id_1ce834d4` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_anonymousanswer` DROP FOREIGN KEY `author_id_refs_id_13fb542e`;
ALTER TABLE `forum_anonymousanswer` ADD CONSTRAINT `author_id_refs_user_ptr_id_6b5b476a` FOREIGN KEY (`author_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_anonymousquestion` DROP FOREIGN KEY `author_id_refs_id_7511a98a`;
ALTER TABLE `forum_anonymousquestion` ADD CONSTRAINT `author_id_refs_user_ptr_id_104edd52` FOREIGN KEY (`author_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_authkeyuserassociation` DROP FOREIGN KEY `user_id_refs_id_2c2a6b01`;
ALTER TABLE `forum_authkeyuserassociation` ADD CONSTRAINT `user_id_refs_user_ptr_id_3f0ec0c3` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_markedtag` DROP FOREIGN KEY `user_id_refs_id_23b833bd`;
ALTER TABLE `forum_markedtag` ADD CONSTRAINT `user_id_refs_user_ptr_id_5a13f081` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_questionsubscription` DROP FOREIGN KEY `user_id_refs_id_18e1489`;
ALTER TABLE `forum_questionsubscription` ADD CONSTRAINT `user_id_refs_user_ptr_id_521b19ad` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_subscriptionsettings` DROP FOREIGN KEY `user_id_refs_id_35edacb4`;
ALTER TABLE `forum_subscriptionsettings` ADD CONSTRAINT `user_id_refs_user_ptr_id_1bc4fc70` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `forum_validationhash` DROP FOREIGN KEY `user_id_refs_id_2c2d214b`;
ALTER TABLE `forum_validationhash` ADD CONSTRAINT `user_id_refs_user_ptr_id_4e5b2d6f` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `question` DROP FOREIGN KEY `author_id_refs_id_56e9d00c`;
ALTER TABLE `question` ADD CONSTRAINT `author_id_refs_user_ptr_id_60d41818` FOREIGN KEY (`author_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `question` DROP FOREIGN KEY `closed_by_id_refs_id_56e9d00c`;
ALTER TABLE `question` ADD CONSTRAINT `closed_by_id_refs_user_ptr_id_60d41818` FOREIGN KEY (`closed_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `question` DROP FOREIGN KEY `deleted_by_id_refs_id_56e9d00c`;
ALTER TABLE `question` ADD CONSTRAINT `deleted_by_id_refs_user_ptr_id_60d41818` FOREIGN KEY (`deleted_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `question` DROP FOREIGN KEY `last_activity_by_id_refs_id_56e9d00c`;
ALTER TABLE `question` ADD CONSTRAINT `last_activity_by_id_refs_user_ptr_id_60d41818` FOREIGN KEY (`last_activity_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `question` DROP FOREIGN KEY `last_edited_by_id_refs_id_56e9d00c`;
ALTER TABLE `question` ADD CONSTRAINT `last_edited_by_id_refs_user_ptr_id_60d41818` FOREIGN KEY (`last_edited_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `question` DROP FOREIGN KEY `locked_by_id_refs_id_56e9d00c`;
ALTER TABLE `question` ADD CONSTRAINT `locked_by_id_refs_user_ptr_id_60d41818` FOREIGN KEY (`locked_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `question_followed_by` DROP FOREIGN KEY `user_id_refs_id_6d30712d`;
ALTER TABLE `question_followed_by` ADD CONSTRAINT `user_id_refs_user_ptr_id_615e65af` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `question_revision` DROP FOREIGN KEY `author_id_refs_id_4f88024f`;
ALTER TABLE `question_revision` ADD CONSTRAINT `author_id_refs_user_ptr_id_42e3d48d` FOREIGN KEY (`author_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `repute` DROP FOREIGN KEY `user_id_refs_id_5a426cd`;
ALTER TABLE `repute` ADD CONSTRAINT `user_id_refs_user_ptr_id_5ea9540f` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `tag` DROP FOREIGN KEY `created_by_id_refs_id_47205d6d`;
ALTER TABLE `tag` ADD CONSTRAINT `created_by_id_refs_user_ptr_id_417f3449` FOREIGN KEY (`created_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;
ALTER TABLE `tag` DROP FOREIGN KEY `deleted_by_id_refs_id_47205d6d`;
ALTER TABLE `tag` ADD CONSTRAINT `deleted_by_id_refs_user_ptr_id_417f3449` FOREIGN KEY (`deleted_by_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

ALTER TABLE `vote` DROP FOREIGN KEY `user_id_refs_id_760a4df0`;
ALTER TABLE `vote` ADD CONSTRAINT `user_id_refs_user_ptr_id_18723e34` FOREIGN KEY (`user_id`) REFERENCES `forum_user` (`user_ptr_id`) ON DELETE RESTRICT ON UPDATE RESTRICT;

"""

from django.core.management.base import NoArgsCommand
from django.db import connection, transaction
from django.conf import settings

class Command(NoArgsCommand):
    def handle_noargs(self, **options):
        if settings.DATABASE_ENGINE in ('postgresql_psycopg2', 'postgresql', ):
            migration_query = PG_MIGRATION_QUERY
            fkeys_query = PG_FKEYS_QUERY
        elif settings.DATABASE_ENGINE == 'mysql':
            migration_query = MYSQL_MIGRATION_QUERY
            fkeys_query = MYSQL_FKEYS_QUERY
        else:
            raise Exception("Database backend not suported by this migration command")

        cursor = connection.cursor()
        cursor.execute(migration_query)
        cursor.execute(fkeys_query)
        transaction.commit_unless_managed()