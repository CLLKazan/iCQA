SELECT t4.id AS q_id, COUNT(t3.id) AS user_rating FROM 
    forum_user AS t1,
    forum_node AS t2,
    forum_action AS t3,
    forum_node AS t4
WHERE
    t4.node_type='question' AND
    t4.author_id=t1.user_ptr_id AND
    t1.user_ptr_id=t2.author_id AND
    t2.added_at<t4.added_at AND
    t2.id=t3.node_id AND
    t3.action_type='voteup'
GROUP BY t4.id;
