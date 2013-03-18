package org.ninit.models.bm25;

/**
 * BM25Similarity.java
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

import org.apache.lucene.search.Similarity;

/**
 * Similarity for BM25 ranking functions family.<BR>
 * This class only implements public <I>float idf(int docFreq, int numDocs)</I>,
 * others method always return 1 and are never invoked from the Scorers.<BR>
 * IDF is implemented as next:<BR>
 * log ((N-n+0.5)/(n+0.5))<BR>
 * where n = docFreq(term) and N = numDocs().
 * 
 * @author "Joaquin Perez-Iglesias"
 * 
 */
public class BM25Similarity extends Similarity {

	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Similarity#coord(int, int)
	 */
	@Override
	public float coord(int overlap, int maxOverlap) {
		return (float) overlap / (float) maxOverlap;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Similarity#idf(int, int)
	 */
	@Override
	public float idf(int docFreq, int numDocs) {
		float result = (numDocs - docFreq + 0.5f);
		result = result / (docFreq + 0.5f);
		return (float) Math.log(result);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Similarity#lengthNorm(java.lang.String,
	 * int)
	 */
	@Override
	public float lengthNorm(String fieldName, int numTokens) {
		return 1;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Similarity#queryNorm(float)
	 */
	@Override
	public float queryNorm(float sumOfSquaredWeights) {

		return 1;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Similarity#sloppyFreq(int)
	 */
	@Override
	public float sloppyFreq(int distance) {

		return 1;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Similarity#tf(float)
	 */
	@Override
	public float tf(float freq) {

		return freq;
	}

}
