SELECT t1.q_id, AVG(t1.score) AS avg_ans_score_tag FROM
(
SELECT t1.q_id, t1.ans_id, t1.ups - IFNULL(t2.downs,0) AS score FROM
    (
        SELECT t1.id AS q_id, t4.id AS ans_id, COUNT(t5.id) AS ups FROM
            forum_node AS t1,
            (SELECT tag_id,node_id FROM forum_node_tags GROUP BY node_id ORDER BY id) AS t2,
            forum_node_tags AS t3,
            forum_node AS t4,
            forum_action AS t5
        WHERE
            t1.id=t2.node_id AND
            t2.tag_id=t3.tag_id AND
            t3.node_id=t4.parent_id AND
            t4.node_type='answer' AND
            t4.id=t5.node_id AND
            t5.action_type='voteup' AND
            t5.action_date<t1.added_at
        GROUP BY t1.id, t4.id
    ) AS t1 LEFT JOIN
    (
        SELECT t1.id AS q_id, t4.id AS ans_id, COUNT(t5.id) AS downs FROM
            forum_node AS t1,
            (SELECT tag_id,node_id FROM forum_node_tags GROUP BY node_id ORDER BY id) AS t2,
            forum_node_tags AS t3,
            forum_node AS t4,
            forum_action AS t5
        WHERE
            t1.id=t2.node_id AND
            t2.tag_id=t3.tag_id AND
            t3.node_id=t4.parent_id AND
            t4.node_type='answer' AND
            t4.id=t5.node_id AND
            t5.action_type='votedown' AND
            t5.action_date<t1.added_at
        GROUP BY t1.id, t4.id
    ) AS t2 ON t1.q_id=t2.q_id AND t1.ans_id=t2.ans_id

UNION

SELECT t2.q_id, t2.ans_id, IFNULL(t1.ups,0) - t2.downs AS score FROM
    (
        SELECT t1.id AS q_id, t4.id AS ans_id, COUNT(t5.id) AS ups FROM
            forum_node AS t1,
            (SELECT tag_id,node_id FROM forum_node_tags GROUP BY node_id ORDER BY id) AS t2,
            forum_node_tags AS t3,
            forum_node AS t4,
            forum_action AS t5
        WHERE
            t1.id=t2.node_id AND
            t2.tag_id=t3.tag_id AND
            t3.node_id=t4.parent_id AND
            t4.node_type='answer' AND
            t4.id=t5.node_id AND
            t5.action_type='voteup' AND
            t5.action_date<t1.added_at
        GROUP BY t1.id, t4.id
    ) AS t1 RIGHT JOIN
    (
        SELECT t1.id AS q_id, t4.id AS ans_id, COUNT(t5.id) AS downs FROM
            osqa.forum_node AS t1,
            (SELECT tag_id,node_id FROM forum_node_tags GROUP BY node_id ORDER BY id) AS t2,
            forum_node_tags AS t3,
            forum_node AS t4,
            forum_action AS t5
        WHERE
            t1.id=t2.node_id AND
            t2.tag_id=t3.tag_id AND
            t3.node_id=t4.parent_id AND
            t4.node_type='answer' AND
            t4.id=t5.node_id AND
            t5.action_type='votedown' AND
            t5.action_date<t1.added_at
        GROUP BY t1.id, t4.id
    ) AS t2 ON t1.q_id=t2.q_id AND t1.ans_id=t2.ans_id
) AS t1
GROUP BY t1.q_id;
