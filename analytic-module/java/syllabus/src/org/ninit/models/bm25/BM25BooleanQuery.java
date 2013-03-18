package org.ninit.models.bm25;

/**
 * BM25BooleanQuery.java
 *
 * Copyright (c) 2008 "Joaquín Pérez-Iglesias"
 *
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

import java.io.IOException;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Set;

import org.apache.lucene.analysis.Analyzer;
import org.apache.lucene.analysis.standard.StandardAnalyzer;
import org.apache.lucene.index.CorruptIndexException;
import org.apache.lucene.index.Term;
import org.apache.lucene.queryParser.ParseException;
import org.apache.lucene.queryParser.QueryParser;
import org.apache.lucene.search.BooleanClause;
import org.apache.lucene.search.BooleanQuery;
import org.apache.lucene.search.Query;
import org.apache.lucene.search.Searcher;
import org.apache.lucene.search.TermQuery;
import org.apache.lucene.search.Weight;
import org.ninit.models.bm25f.BM25FParameters;

/**
 * Query based in BM25 family ranking functions.<BR>
 * <B>WARNING:Searcher similarity will be ignored, in order to calculate the
 * relevance BM25Similarity or BM25FSimilarity are used.</B><BR>
 * <B>WARNING:BM25Parameters.setAverageLength or
 * BM25FParameters.setAverageLength must be invoked in order to set the average
 * length for the field(s).</B>
 * 
 * @author "Joaquin Perez-Iglesias"
 *@see BM25Parameters
 *@see BM25FParameters
 */
@SuppressWarnings("serial")
public class BM25BooleanQuery extends Query {

	private List<BooleanTermQuery> mustBoolTermQueries = new ArrayList<BooleanTermQuery>();
	private List<BooleanTermQuery> shouldBoolTermQueries = new ArrayList<BooleanTermQuery>();
	private List<BooleanTermQuery> notBoolTermQueries = new ArrayList<BooleanTermQuery>();
	private String[] fields = null;
	private float[] boosts;
	private float[] bParams;

	/**
	 * Build a query that will use BM25 function ranking in the field passed as
	 * parameter.<BR>
	 * <B>WARNING:BM25Parameters.setAverageLength must be invoked in order to
	 * set the average length for the field 'field'.</B>
	 * 
	 * @see BM25Parameters
	 * @param query
	 *            The query String
	 * @param field
	 *            The field to search
	 * @param analyzer
	 *            Analyzer used to parse the query String
	 * @throws ParseException
	 * @throws IOException
	 */
	@SuppressWarnings("unchecked")
	public BM25BooleanQuery(String query, String field, Analyzer analyzer)
			throws ParseException, IOException {
		QueryParser qp = new QueryParser(field, analyzer);
		Query q = qp.parse(query);

		if (q instanceof BooleanQuery) {
			List<BooleanClause> clauses = ((BooleanQuery) q).clauses();
			for (int i = 0; i < clauses.size(); i++) {
				Set<Term> terms = new HashSet<Term>();
				clauses.get(i).getQuery().extractTerms(terms);
				Iterator<Term> iter = terms.iterator();
				while (iter.hasNext()) {
					BooleanTermQuery boolTerm = new BooleanTermQuery(
							new TermQuery(new Term(field, iter.next().text())),
							clauses.get(i).getQuery().getBoost(), clauses
									.get(i).getOccur());
					this.addClause(boolTerm);
				}
			}
		} else {
			Set<Term> terms = new HashSet<Term>();
			q.extractTerms(terms);
			Iterator<Term> iter = terms.iterator();
			while (iter.hasNext()) {
				this.mustBoolTermQueries.add(new BooleanTermQuery(
						new TermQuery(new Term(field, iter.next().text())),
						BooleanClause.Occur.MUST));
			}

		}
	}

	/**
	 * Build a query that will use BM25F function ranking. By default a boost
	 * factor equals to 1 for each field will be applied. The length
	 * normalization parameter for each field b_field will be set up to 0.75. <BR>
	 * <B>WARNING:BM25FParameters.setAverageLength must be invoked in order to
	 * set the average length for each field in 'fields'.</B>
	 * 
	 * @see BM25FParameters
	 * @param query
	 *            The query String
	 * @param fields
	 *            The fields to search
	 * @param analyzer
	 *            Analyzer used to parse the query String
	 * @throws ParseException
	 * @throws IOException
	 */
	public BM25BooleanQuery(String query, String[] fields, Analyzer analyzer)
			throws ParseException, IOException {
		this(query, "ALL_FIELDS", analyzer);
		this.fields = fields;
		this.boosts = new float[this.fields.length];
		this.bParams = new float[this.fields.length];
		for (int i = 0; i < this.fields.length; i++) {
			this.boosts[i] = 1;
			this.bParams[i] = 0.75f;
		}

	}

	/**
	 * 
	 * @param query
	 *            The query String
	 * @param fields
	 *            The fields to search
	 * @param analyzer
	 *            Analyzer used to parse the query String
	 * @throws ParseException
	 * @throws IOException
	 */

	/**
	 * Build a query that will use BM25F function ranking. <BR>
	 * <B>WARNING:BM25FParameters.setAverageLength must be invoked in order to
	 * set the average length for each field in 'fields'.</B>
	 * 
	 * @see BM25FParameters
	 * @param query
	 *            The query String
	 * @param fields
	 *            The fields to search
	 * @param analyzer
	 *            Analyzer used to parse the query String
	 * @param boosts
	 *            The boost factor applied to the fields array
	 * @param bParams
	 *            The length normalization factors applied to the fields array
	 * @throws ParseException
	 * @throws IOException
	 */
	public BM25BooleanQuery(String query, String[] fields, Analyzer analyzer,
			float[] boosts, float[] bParams) throws ParseException, IOException {
		this(query, "ALL_FIELDS", analyzer);
		this.fields = fields;
		this.boosts = boosts;
		this.bParams = bParams;

	}

	@Override
	public Weight weight(Searcher searcher) throws IOException {

		if (this.fields == null)
			return new BM25BooleanWeight(this.shouldBoolTermQueries
					.toArray(new BooleanTermQuery[this.shouldBoolTermQueries
							.size()]), this.mustBoolTermQueries
					.toArray(new BooleanTermQuery[this.mustBoolTermQueries
							.size()]), this.notBoolTermQueries
					.toArray(new BooleanTermQuery[this.notBoolTermQueries
							.size()]));
		else
			return new BM25BooleanWeight(this.shouldBoolTermQueries
					.toArray(new BooleanTermQuery[this.shouldBoolTermQueries
							.size()]), this.mustBoolTermQueries
					.toArray(new BooleanTermQuery[this.mustBoolTermQueries
							.size()]), this.notBoolTermQueries
					.toArray(new BooleanTermQuery[this.notBoolTermQueries
							.size()]), this.fields, this.boosts, this.bParams);
	}

	private void addClause(BooleanTermQuery boolTerm) {
		if (boolTerm.occur == BooleanClause.Occur.MUST)
			this.mustBoolTermQueries.add(boolTerm);
		else if (boolTerm.occur == BooleanClause.Occur.SHOULD)
			this.shouldBoolTermQueries.add(boolTerm);
		else
			this.notBoolTermQueries.add(boolTerm);
	}

	public String toString() {
		StringBuilder buffer = new StringBuilder();
		for (BooleanTermQuery btq : this.mustBoolTermQueries) {
			buffer.append(btq.toString());
			buffer.append(" ");
		}
		for (BooleanTermQuery btq : this.shouldBoolTermQueries) {
			buffer.append(btq.toString());
			buffer.append(" ");
		}
		for (BooleanTermQuery btq : this.notBoolTermQueries) {
			buffer.append(btq.toString());
		}
		return buffer.toString();
	}

	@Override
	public String toString(String field) {
		return this.toString();
	}

	public class BooleanTermQuery {

		TermQuery termQuery;
		BooleanClause.Occur occur;

		public BooleanTermQuery(TermQuery termQuery, BooleanClause.Occur occur) {
			this.termQuery = termQuery;
			this.occur = occur;
		}

		public BooleanTermQuery(TermQuery termQuery, float boost,
				BooleanClause.Occur occur) {
			this(termQuery, occur);
			this.termQuery.setBoost(boost);
		}

		public TermQuery getTermQuery() {
			return termQuery;
		}

		public float getBoost() {
			return this.termQuery.getBoost();
		}

		public void setTermQuery(TermQuery termQuery) {
			this.termQuery = termQuery;
		}

		public BooleanClause.Occur getOccur() {
			return occur;
		}

		public void setOccur(BooleanClause.Occur occur) {
			this.occur = occur;
		}

		public String toString() {
			String result = "";
			result = "(" + this.occur + "(" + this.getTermQuery().getTerm()
					+ "^" + this.getBoost() + "))";
			return result;
		}
	}

	public static void main(String args[]) throws ParseException,
			CorruptIndexException, IOException {
		BM25BooleanQuery q = new BM25BooleanQuery("(+product +faroe +islands +exported)", "CONTENT",
				new StandardAnalyzer());
		System.out.println(q);
	}

}
