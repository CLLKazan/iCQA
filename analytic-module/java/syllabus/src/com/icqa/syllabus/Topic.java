package com.icqa.syllabus;

import net.sf.json.JSONArray;
import net.sf.json.JSONObject;

import java.util.ArrayList;

/**
 * Created with IntelliJ IDEA.
 * User: ramis
 * Date: 3/24/13
 * Time: 9:44 PM
 * To change this template use File | Settings | File Templates.
 */
public class Topic {
    public String mTitle;
    public ArrayList<Post> mPosts;

    public static class Post{
        long id;
        String title;
        String body;
        int score;
        boolean marked;
        ArrayList<Post> answers = null;

        public Post(long id, String title, String body, int score, boolean marked, ArrayList<Post> answers){
            this.id = id;
            this.title = title;
            this.body = body;
            this.answers = answers;
            this.score = score;
            this.marked = marked;
        }

        public String toJSON(){
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", id);
            jsonObject.put("title", title);
            jsonObject.put("body", body);
            jsonObject.put("score", score);
            jsonObject.put("marked", marked);
            if(answers != null && answers.size() > 0){
                ArrayList<String> answersString = new ArrayList<String>(answers.size());
                for(Post answer : answers){
                    answersString.add(answer.toJSON());
                }
                jsonObject.put("answers", JSONArray.fromObject(answersString));
            }
            return jsonObject.toString();
        }
    }

    public Topic(String title, ArrayList<Post> posts){
        mTitle = title;
        mPosts = posts;
    }

    public String toString(){
        return mTitle;
    }
}
