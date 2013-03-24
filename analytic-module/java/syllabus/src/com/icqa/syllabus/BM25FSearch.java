package com.icqa.syllabus;

import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.document.Document;
import org.apache.lucene.index.IndexReader;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.apache.lucene.store.SimpleFSDirectory;
import org.apache.lucene.util.Version;
import org.ninit.models.bm25.BM25BooleanQuery;
import org.ninit.models.bm25f.BM25FParameters;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;


public class BM25FSearch {
    private String[] fields = {"title", "body", "answer"};
    private float[]  boosts = {1f, 0.0f, 0.0f};
    private float[]  bParams= {0.75f, 0.75f, 0.75f};

    IndexSearcher searcher;
    StandardAnalyzer analyzer;

    public BM25FSearch(String parametersFileName) throws IOException {

        BM25FParameters.load(parametersFileName);

        searcher = new IndexSearcher(IndexReader.open(Main.INDEX_DIR));
        analyzer = new StandardAnalyzer(Version.LUCENE_29);
    }

    public long[] getTopN(String queryParam, int n) throws IOException, ParseException {
        long[] res = new long[n];
        BM25BooleanQuery query = new BM25BooleanQuery(queryParam, fields, analyzer, boosts, bParams);

        TopDocs topDocs = searcher.search(query, n);

        ScoreDoc[] hits = topDocs.scoreDocs;
        n = Math.min(n, hits.length);
        for (int i = 0; i < n; i++){
            Document doc = searcher.doc(hits[i].doc);
            res[i] = Long.parseLong(doc.get("id"));
        }
        return res;
    }

    public void setBoosts(float[] newBoosts){
        boosts = newBoosts;
    }
}
