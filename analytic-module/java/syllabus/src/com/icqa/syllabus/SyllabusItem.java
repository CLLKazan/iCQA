package com.icqa.syllabus;

import net.sf.json.JSONObject;

import java.util.ArrayList;

/**
 * Created with IntelliJ IDEA.
 * User: ramis
 * Date: 3/24/13
 * Time: 9:44 PM
 * To change this template use File | Settings | File Templates.
 */
public class SyllabusItem {
    public String mTitle;
    public ArrayList<Post> mPosts;

    public static class Post{
        long id;
        String title;
        String body;
        String answer;

        public Post(long id, String title, String body, String answer){
            this.id = id;
            this.title = title;
            this.body = body;
            this.answer = answer;
        }

        public String toJSON(){
            JSONObject jsonObject = new JSONObject();
            jsonObject.put("id", id);
            jsonObject.put("title", title);
            jsonObject.put("body", body);
            jsonObject.put("answer", answer);
            return jsonObject.toString();
        }
    }

    public SyllabusItem(String title, ArrayList<Post> posts){
        mTitle = title;
        mPosts = posts;
    }
}
