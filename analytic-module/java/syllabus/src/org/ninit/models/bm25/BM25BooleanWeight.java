package org.ninit.models.bm25;

/**
 * BM25BooleanWeight.java
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
import org.apache.lucene.search.Query;
import org.apache.lucene.search.Scorer;
import org.apache.lucene.search.Weight;
import org.ninit.models.bm25.BM25BooleanQuery.BooleanTermQuery;

/**
 * Weight BM25 class, implements <I>public Scorer scorer(IndexReader reader)
 * throws IOException</I> <BR>
 * and <I>public Explanation explain(IndexReader reader, int doc) throws
 * IOException </I><BR>
 * Query weight is not used in this BM25 implementation.
 * 
 * @author "Joaquin Perez-Iglesias"
 * 
 */
@SuppressWarnings("serial")
public class BM25BooleanWeight extends Weight {

	private BooleanTermQuery[] should;
	private BooleanTermQuery[] must;
	private BooleanTermQuery[] not;
	private BooleanTermQuery[] unique = null;
	private String[] fields = null;
	private float[] boosts;
	private float[] bParams;
	private int howMany = 0;

	public BM25BooleanWeight(BooleanTermQuery[] should,
			BooleanTermQuery[] must, BooleanTermQuery[] not) {
		if (should.length > 0) {
			this.should = should;
			this.unique = this.should;
			howMany++;
		}
		if (must.length > 0) {
			this.must = must;
			this.unique = this.must;
			howMany++;
		}
		if (not.length > 0) {
			this.not = not;
			this.unique = this.not;
			howMany++;
		}
	}

	public BM25BooleanWeight(BooleanTermQuery[] should,
			BooleanTermQuery[] must, BooleanTermQuery[] not, String fields[],
			float[] boosts, float[] bParams) {
		this(should, must, not);
		this.fields = fields;
		this.boosts = boosts;
		this.bParams = bParams;
	}

	/**
	 * Return null
	 * 
	 * @see org.apache.lucene.search.Weight#explain(org.apache.lucene.index.IndexReader,
	 *      int)
	 */
	@Override
	public Explanation explain(IndexReader reader, int doc) throws IOException {
		if (this.fields == null)
			return new BM25BooleanScorer(reader, this.should, this.must,
					this.not, new BM25Similarity()).explain(doc);
		else
			return new BM25BooleanScorer(reader, this.should, this.must,
					this.not, new BM25Similarity(), this.fields, this.boosts,
					this.bParams).explain(doc);
	}

	/*
	 * Return null
	 * 
	 * @see org.apache.lucene.search.Weight#getQuery()
	 */
	@Override
	public Query getQuery() {
		return null;
	}

	/**
	 * Return 0
	 * 
	 * @see org.apache.lucene.search.Weight#getValue()
	 */
	@Override
	public float getValue() {
		return 0;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Weight#normalize(float)
	 */
	@Override
	public void normalize(float norm) {

	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see
	 * org.apache.lucene.search.Weight#scorer(org.apache.lucene.index.IndexReader
	 * )
	 */
	@Override
	public Scorer scorer(IndexReader reader, boolean b, boolean b1) throws IOException {
		if (howMany > 1) { // BM25BooleaScorer
			if (this.fields == null)
				return new BM25BooleanScorer(reader, this.should, this.must,
						this.not, new BM25Similarity());
			else
				return new BM25BooleanScorer(reader, this.should, this.must,
						this.not, new BM25Similarity(), this.fields,
						this.boosts, this.bParams);
		} else {// BM25SingleBooleanScorer
			if (this.fields == null)
				return new BM25SingleBooleanScorer(reader, this.unique,
						new BM25Similarity());
			else
				return new BM25SingleBooleanScorer(reader, this.unique,
						new BM25Similarity(), this.fields, this.boosts,
						this.bParams);
		}

	}

	/**
	 * Return 0.
	 * 
	 * @see org.apache.lucene.search.Weight#sumOfSquaredWeights()
	 */
	@Override
	public float sumOfSquaredWeights() throws IOException {
		return 0;
	}

}
