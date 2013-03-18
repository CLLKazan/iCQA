package org.ninit.models.bm25;

/**
 * BM25BooleanScorer.java
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

import org.apache.lucene.index.IndexReader;
import org.apache.lucene.search.Explanation;
import org.apache.lucene.search.Scorer;
import org.apache.lucene.search.Similarity;
import org.ninit.models.bm25.BM25BooleanQuery.BooleanTermQuery;
import org.ninit.models.bm25f.BM25FTermScorer;
import org.ninit.models.bool.AbstractBooleanScorer;
import org.ninit.models.bool.MatchAllBooleanScorer;
import org.ninit.models.bool.MustBooleanScorer;
import org.ninit.models.bool.NotBooleanScorer;
import org.ninit.models.bool.ShouldBooleanScorer;

/**
 * BM25BooleanScorer, calculates the total relevance value based in a boolean
 * expression.<BR>
 * 
 * @author "Joaquin Perez-Iglesias"
 * 
 */
public class BM25BooleanScorer extends Scorer {

	private AbstractBooleanScorer shouldBooleanScorer;
	private AbstractBooleanScorer mustBooleanScorer;
	private AbstractBooleanScorer notBooleanScorer;
	private boolean hasMoreShould = false;
	private boolean hasMoreMust = false;
	private boolean hasMoreNot = false;
	private int doc = -1;
	private int ndocs;
	private boolean initialized = false;

	public BM25BooleanScorer(IndexReader reader, BooleanTermQuery[] should,
			BooleanTermQuery[] must, BooleanTermQuery[] not,
			Similarity similarity) throws IOException {
		super(similarity);
		this.ndocs = reader.numDocs();

		if (should != null && should.length > 0) {

			Scorer[] shouldScorer = new Scorer[should.length];
			for (int i = 0; i < shouldScorer.length; i++) {
				shouldScorer[i] = new BM25TermScorer(reader,
						should[i].termQuery, similarity);
			}
			this.shouldBooleanScorer = new ShouldBooleanScorer(similarity,
					shouldScorer);

		} else
			this.shouldBooleanScorer = new MatchAllBooleanScorer(similarity,
					this.ndocs);

		if (must != null && must.length > 0) {
			Scorer[] mustScorer = new Scorer[must.length];
			for (int i = 0; i < mustScorer.length; i++) {
				mustScorer[i] = new BM25TermScorer(reader, must[i].termQuery,
						similarity);
			}

			this.mustBooleanScorer = new MustBooleanScorer(similarity,
					mustScorer);
		} else
			this.mustBooleanScorer = new MatchAllBooleanScorer(similarity,
					this.ndocs);

		if (not != null && not.length > 0) {
			Scorer[] notScorer = new Scorer[not.length];
			for (int i = 0; i < notScorer.length; i++) {
				notScorer[i] = new BM25TermScorer(reader, not[i].termQuery,
						similarity);
			}

			this.notBooleanScorer = new NotBooleanScorer(similarity, notScorer,
					this.ndocs);
		} else
			this.notBooleanScorer = new MatchAllBooleanScorer(similarity,
					this.ndocs);
	}

	public BM25BooleanScorer(IndexReader reader, BooleanTermQuery[] should,
			BooleanTermQuery[] must, BooleanTermQuery[] not,
			Similarity similarity, String[] fields, float[] boosts,
			float[] bParams) throws IOException {
		super(similarity);
		this.ndocs = reader.numDocs();
		if (should != null && should.length > 0) {
			Scorer[] shouldScorer = new Scorer[should.length];
			for (int i = 0; i < shouldScorer.length; i++) {
				shouldScorer[i] = new BM25FTermScorer(reader,
						should[i].termQuery, fields, boosts, bParams,
						similarity);
			}

			this.shouldBooleanScorer = new ShouldBooleanScorer(similarity,
					shouldScorer);
		} else
			this.shouldBooleanScorer = new MatchAllBooleanScorer(similarity,
					this.ndocs);

		if (must != null && must.length > 0) {
			Scorer[] mustScorer = new Scorer[must.length];
			for (int i = 0; i < mustScorer.length; i++) {
				mustScorer[i] = new BM25FTermScorer(reader, must[i].termQuery,
						fields, boosts, bParams, similarity);
			}

			this.mustBooleanScorer = new MustBooleanScorer(similarity,
					mustScorer);
		} else
			this.mustBooleanScorer = new MatchAllBooleanScorer(similarity,
					this.ndocs);

		if (not != null && not.length > 0) {
			Scorer[] notScorer = new Scorer[not.length];
			for (int i = 0; i < notScorer.length; i++) {
				notScorer[i] = new BM25FTermScorer(reader, not[i].termQuery,
						fields, boosts, bParams, similarity);
			}

			this.notBooleanScorer = new NotBooleanScorer(similarity, notScorer,
					this.ndocs);
		} else
			this.notBooleanScorer = new MatchAllBooleanScorer(similarity,
					this.ndocs);

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#doc()
	 */
	@Override
	public int doc() {
		return this.doc;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#explain(int)
	 */
	@Override
	public Explanation explain(int doc) throws IOException {
		if (!this.skipTo(doc))
			return null;
		Explanation result = new Explanation();
		result.setDescription("Total");
		Explanation detail = null;
		float value = 0f;
		if (this.hasMoreMust && this.mustBooleanScorer.doc() == doc)
			detail = this.mustBooleanScorer.explain(doc);
		if (detail != null) {
			result.addDetail(this.mustBooleanScorer.explain(doc));
			value += detail.getValue();
		}

		if (this.hasMoreShould && this.shouldBooleanScorer.doc() == doc)
			detail = this.shouldBooleanScorer.explain(doc);
		if (detail != null) {
			result.addDetail(this.shouldBooleanScorer.explain(doc));
			value += detail.getValue();
		}
		result.setValue(value);
		return result;
	}

	private void init() throws IOException {
		this.hasMoreShould = this.shouldBooleanScorer.next();
		this.hasMoreMust = this.mustBooleanScorer.next();
		this.hasMoreNot = this.notBooleanScorer.next();
	}

	private void doNext() throws IOException {
		if (this.hasMoreShould && this.shouldBooleanScorer.doc() == this.doc)
			this.hasMoreShould = this.shouldBooleanScorer.next();
		if (this.hasMoreMust && this.mustBooleanScorer.doc() == this.doc)
			this.hasMoreMust = this.mustBooleanScorer.next();
		if (this.hasMoreNot && this.notBooleanScorer.doc() == this.doc)
			this.hasMoreNot = this.notBooleanScorer.next();
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#next()
	 */
	@Override
	public boolean next() throws IOException {

		if (!this.initialized) {
			this.initialized = true;
			this.init();
		} else {
			this.doNext();
		}

		while (this.doc < this.ndocs - 1) {
			this.doc++;
			if (this.hasMoreMust) {
				if (this.mustBooleanScorer.doc() < this.doc)
					this.hasMoreMust = this.mustBooleanScorer.next();
			} else
				return false;

			if (this.hasMoreNot) {
				if (this.notBooleanScorer.doc() < this.doc)
					this.hasMoreNot = this.notBooleanScorer.next();
			} else
				return false;

			if (this.hasMoreShould) {
				if (this.shouldBooleanScorer.doc() < this.doc)
					this.hasMoreShould = this.shouldBooleanScorer.next();
			}

			if (this.hasMoreMust && this.hasMoreNot) {
				if (this.mustBooleanScorer.doc() == this.notBooleanScorer.doc())
					return true;
			} else
				return false;
		}

		return false;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#score()
	 */
	@Override
	public float score() throws IOException {
		float result = 0f;
		if (this.hasMoreMust && this.mustBooleanScorer.doc() == doc)
			result += this.mustBooleanScorer.score();

		if (this.hasMoreShould && this.shouldBooleanScorer.doc() == doc)
			result += this.shouldBooleanScorer.score();

		return result;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#skipTo(int)
	 */
	@Override
	public boolean skipTo(int target) throws IOException {
		while (this.next() && this.doc() < target) {
		}

		return this.doc() == target;
	}

}
