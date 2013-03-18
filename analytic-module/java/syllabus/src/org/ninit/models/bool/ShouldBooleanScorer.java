package org.ninit.models.bool;

/**
 * ShouldBooleanScorer.java
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

import org.apache.lucene.search.Explanation;
import org.apache.lucene.search.Scorer;
import org.apache.lucene.search.Similarity;

/**
 * Boolean Scorer that matches all documents that contains at least one term (OR
 * operator).<BR>
 * 
 * @author "Joaquin Perez-Iglesias"
 * 
 */
public class ShouldBooleanScorer extends AbstractBooleanScorer {

	private boolean initializated = false;
	private int doc = Integer.MAX_VALUE;

	public ShouldBooleanScorer(Similarity similarity, Scorer scorer[])
			throws IOException {
		super(similarity, scorer);
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
		Explanation detail;
		result.setDescription("OR");
		float value = 0f;
		for (int i = 0; i < this.subScorer.length; i++) {
			if (this.subScorer[i].doc() == doc) {
				detail = this.subScorer[i].explain(doc);
				result.addDetail(detail);
				value += detail.getValue();
			}
		}
		result.setValue(value);
		return result;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#next()
	 */
	@Override
	public boolean next() throws IOException {
		if (!this.initializated) {
			this.initializated = true;
			return this.init();
		}
		int min = Integer.MAX_VALUE;
		// AVANZO LOS TERMDOCS CON MENOR ID
		for (int i = 0; i < this.subScorer.length; i++) {
			if (this.subScorerNext[i] && this.subScorer[i].doc() == this.doc) {
				this.subScorerNext[i] = this.subScorer[i].next();
			}
			if (this.subScorerNext[i] && this.subScorer[i].doc() < min)
				min = this.subScorer[i].doc();
		}
		return ((this.doc = min) != Integer.MAX_VALUE);
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#skipTo(int)
	 */
	@Override
	public boolean skipTo(int target) throws IOException {
		while (this.doc() < target && this.next()) {
		}

		return this.doc() == target;
	}

	/*
	 * (non-Javadoc)
	 * 
	 * @see org.apache.lucene.search.Scorer#score()
	 */
	@Override
	public float score() throws IOException {
		double result = 0f;
		for (int i = 0; i < this.subScorer.length; i++) {
			if (this.subScorer[i].doc() == this.doc)
				result += this.subScorer[i].score();

		}
		return (float) result;
	}

	private boolean init() throws IOException {
		boolean result = false;
		for (int i = 0; i < this.subScorer.length; i++) {
			this.subScorerNext[i] = this.subScorer[i].next();
			if (this.subScorerNext[i] && this.subScorer[i].doc() < this.doc) {
				this.doc = this.subScorer[i].doc();
				result = true;
			}
		}
		return result;
	}

}
