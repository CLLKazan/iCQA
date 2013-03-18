package com.icqa.syllabus;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.SimpleFSDirectory;
import org.apache.lucene.util.Version;
import org.jsoup.Jsoup;
import org.ninit.models.bm25.BM25BooleanQuery;
import org.ninit.models.bm25f.BM25FParameters;

import java.io.*;
import java.sql.*;


public class Main {

    public static SimpleFSDirectory INDEX_DIR;
    public static final String BM_25_F_PARAMETERS = "BM25FParameters";

    public static String sql = "SELECT node_id, title, body FROM forum_node " +
            "INNER JOIN forum_node_tags ON forum_node.id=forum_node_tags.node_id " +
            "WHERE tag_id=70";

    public static String answer_sql = "SELECT parent_id, GROUP_CONCAT(body) as answer FROM forum_node " +
            "WHERE parent_id=? GROUP BY parent_id";

    public static String asql = "SELECT node_id, title, body, answer FROM (\n" +
            "  SELECT * FROM (\n" +
            "    SELECT id, title, body FROM forum_node \n" +
            "    WHERE parent_id IS NULL\n" +
            "  ) as questions \n" +
            "  INNER JOIN forum_node_tags ON questions.id=forum_node_tags.node_id\n" +
            "  WHERE tag_id=70\n" +
            ") as questions_by_tag\n" +
            "INNER JOIN (\n" +
            "  SELECT parent_id, GROUP_CONCAT(body) as answer\n" +
            "  FROM forum_node WHERE marked=1 GROUP BY parent_id\n" +
            ") as answers ON questions_by_tag.id=answers.parent_id";

    public static void main(String[] args) throws Exception {

        INDEX_DIR = new SimpleFSDirectory(new File("index"));
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in, "UTF-8"));
        String line = in.readLine();

        if(line.equals("index")) {
            indexDb();
        }
        else if(line.equals("search")){
            search(new File("syllabus.txt"));
        }
    }

    public static Connection getConnection() throws ClassNotFoundException, IllegalAccessException, InstantiationException, SQLException {
        Class.forName("com.mysql.jdbc.Driver").newInstance();
        return DriverManager.getConnection("jdbc:mysql://localhost/osqa", "osqa", "osqapass");
    }

    public static void indexDb(){
        try{
            long titlesLength = 0, bodyLength = 0, answersLength = 0, docsCount = 0;

            StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_29);
            IndexWriter writer = new IndexWriter(INDEX_DIR, analyzer);

            System.out.println("Indexing to directory '" + INDEX_DIR.getFile().getAbsolutePath() + "'...");
            Connection connection = getConnection();
            Statement questionsStatement = connection.createStatement();
            PreparedStatement answerStatement = connection.prepareStatement(answer_sql);
            ResultSet rs = questionsStatement.executeQuery(sql);
            while (rs.next()) {
                Document d = new Document();

                answerStatement.setInt(1, rs.getInt("node_id"));
                answerStatement.execute();
                ResultSet resultSet = answerStatement.getResultSet();

                String title = rs.getString("title");
                String body = Jsoup.parse(rs.getString("body")).text();
                String answer = resultSet.next() ? Jsoup.parse(resultSet.getString("answer")).text() : "";

                d.add(new Field("id", rs.getString("node_id"), Field.Store.YES, Field.Index.NOT_ANALYZED));

                d.add(new Field("title", title, Field.Store.YES, Field.Index.ANALYZED));
                d.add(new Field("body", body, Field.Store.NO, Field.Index.ANALYZED));
                d.add(new Field("answer", answer, Field.Store.NO, Field.Index.ANALYZED));

                titlesLength += title.length();
                bodyLength += body.length();
                answersLength += answer.length();

                docsCount += 1;

                writer.addDocument(d);
                System.out.println(rs.getString("node_id") + " " + title.length() + " " + answer.length());
            }

            String params = "title\n" + Float.toString(titlesLength/(float)docsCount) + "\n" +
                    "body\n" + Float.toString(bodyLength/(float)docsCount) + "\n" +
                    "answer\n" + Float.toString(answersLength/(float)docsCount) + "\n";
            BufferedWriter bufferedWriter = new BufferedWriter(new FileWriter(BM_25_F_PARAMETERS));
            bufferedWriter.write(params);
            bufferedWriter.close();

            writer.close();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    public static void search(File queries) throws IOException {
        try{
            String[] fields = {"title", "body", "answer"};
            float[]  boosts = {1f, 0.0f, 0.0f};
            float[]  bParams= {0.75f, 0.75f, 0.75f};

            BM25FParameters.load(BM_25_F_PARAMETERS);

            IndexSearcher searcher = new IndexSearcher(IndexReader.open(INDEX_DIR));
            StandardAnalyzer analyzer = new StandardAnalyzer(Version.LUCENE_29);

            BufferedReader reader = new BufferedReader(new FileReader(queries));
            String line;
            while((line = reader.readLine()) != null){
                BM25BooleanQuery query = new BM25BooleanQuery(line, fields, analyzer, boosts, bParams);

                TopDocs topDocs = searcher.search(query, 5);

                System.out.println("Found " + topDocs.totalHits + " results for '" + line + "'");
                ScoreDoc[] hits = topDocs.scoreDocs;
                for (int i = 0; i < hits.length; i++){
                    Document doc = searcher.doc(hits[i].doc);
                    String title = doc.get("title");
                    System.out.println((i + 1) + ": " + hits[i].score + "\t\t" + doc.get("id") + "\t\t" + title);
                }
            }
        }catch(Exception e){
            e.printStackTrace();
        }
    }
}
