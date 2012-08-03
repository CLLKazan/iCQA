CREATE OR REPLACE FUNCTION public.create_plpgsql_language ()
    RETURNS TEXT
    AS $$
        CREATE LANGUAGE plpgsql;
        SELECT 'language plpgsql created'::TEXT;
    $$
LANGUAGE 'sql';

SELECT CASE WHEN
      (SELECT true::BOOLEAN
         FROM pg_language
        WHERE lanname='plpgsql')
    THEN
      (SELECT 'language already installed'::TEXT)
    ELSE
      (SELECT public.create_plpgsql_language())
    END;

DROP FUNCTION public.create_plpgsql_language ();

CREATE OR REPLACE FUNCTION public.drop_tsv_noderevision_column () RETURNS VOID AS $$
begin
        ALTER TABLE forum_noderevision DROP COLUMN tsv;
        DROP TRIGGER IF EXISTS tsvectorupdate ON forum_noderevision;
end
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.tsv_noderevision_column_exists() RETURNS int AS $$
 SELECT COUNT(attname)::int FROM pg_attribute WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = 'forum_noderevision') AND attname = 'tsv';
$$ LANGUAGE 'sql';

select case when public.tsv_noderevision_column_exists()>0 then public.drop_tsv_noderevision_column()end;

drop function drop_tsv_noderevision_column();
drop function tsv_noderevision_column_exists();

CREATE OR REPLACE FUNCTION set_doctable_tsv() RETURNS TRIGGER AS $$
declare
  root_id int;
  doc tsvector;
  rcount int;
  cv tsvector;
begin
    SELECT abs_parent_id INTO root_id FROM forum_node WHERE id = new.node_id;

    IF root_id IS NULL THEN
	  root_id := new.node_id;
    END IF;

    SELECT count(*)::int INTO rcount FROM forum_node WHERE id = root_id;

    IF rcount = 0 THEN
        return new;
    END IF;

    SELECT
      setweight(to_tsvector('english', coalesce(tagnames,'')), 'A') ||
      setweight(to_tsvector('english', coalesce(title,'')), 'B') ||
      setweight(to_tsvector('english', coalesce(body,'')), 'C') INTO doc
      FROM forum_node WHERE id = root_id;

    SELECT count(*)::int INTO rcount FROM forum_node WHERE abs_parent_id = root_id AND (NOT state_string LIKE '%%deleted%%');

    IF rcount > 0 THEN
       FOR cv in SELECT setweight(to_tsvector('english', coalesce(body,'')), 'C') FROM forum_node WHERE abs_parent_id = root_id  AND (NOT state_string LIKE '%%deleted%%') LOOP
           doc :=(doc || cv);
       END LOOP;
     END IF;

    SELECT count(*)::int INTO rcount FROM forum_rootnode_doc WHERE node_id = root_id;

    IF rcount > 0 THEN
       UPDATE forum_rootnode_doc SET document = doc WHERE node_id = root_id;
    ELSE
       INSERT INTO forum_rootnode_doc (node_id, document) VALUES (root_id, doc);
    END IF;

  RETURN new;
end
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.build_doc_table() RETURNS VOID as $$
  CREATE TABLE forum_rootnode_doc
  (
     node_id integer,
     "document" tsvector,
      PRIMARY KEY (node_id),
      FOREIGN KEY (node_id) REFERENCES forum_node (id)    ON UPDATE NO ACTION ON DELETE NO ACTION
  ) WITH (OIDS=FALSE);

  DROP TRIGGER IF EXISTS tsvectorupdate ON forum_noderevision;

  CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
    ON forum_noderevision FOR EACH ROW EXECUTE PROCEDURE set_doctable_tsv();

  CREATE INDEX doctable_tsv ON forum_rootnode_doc USING gin(document);
$$ LANGUAGE 'sql';

CREATE OR REPLACE FUNCTION public.doc_table_exists() RETURNS int AS $$
 SELECT COUNT(table_name)::int FROM information_schema.tables WHERE table_name = 'forum_rootnode_doc';
$$ LANGUAGE 'sql';

select case when public.doc_table_exists()=0 then public.build_doc_table()end;

drop function build_doc_table();
drop function doc_table_exists();

CREATE OR REPLACE FUNCTION rank_exact_matches(rank float) RETURNS float AS $$
begin
	IF rank = 0 THEN
		return 1;
	ELSE
		return rank;
	END IF;

end
$$ LANGUAGE plpgsql;

CREATE OR REPLACE FUNCTION public.rebuild_index() RETURNS VOID as $$
	DECLARE
		r integer;
	BEGIN
		FOR r IN SELECT active_revision_id FROM forum_node WHERE node_type = 'question' LOOP
			UPDATE forum_noderevision SET id = id WHERE id = r;
		END LOOP;
	END
$$ LANGUAGE 'plpgsql';

SELECT rebuild_index();
