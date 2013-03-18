package org.ninit.models.bm25f;

/**
 * BM25FParameters.java
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

import java.io.BufferedReader;
import java.io.FileReader;
import java.io.IOException;
import java.util.Iterator;
import java.util.Map.Entry;

import org.ninit.models.bm25.BM25Parameters;

/**
 * Parameters needed to calculate the BM25 relevance.
 * 
 * @author "Joaquin Perez-Iglesias"
 * 
 */

public class BM25FParameters extends BM25Parameters {

	private static float K1 = 2f;
	private static String idfField = null;

	protected BM25FParameters() {
	};

	/**
	 * 
	 * @return The field with the longest average length
	 */
	public static String getIdfField() {
		if (idfField == null) {
			float max = -1;
			String maxField = "";
			Iterator<Entry<String, Float>> iter = BM25FParameters.avgLength.entrySet().iterator();
			while (iter.hasNext()) {
				Entry<String, Float> entry = iter.next();
				if (entry.getValue() > max) {
					max = entry.getValue();
					maxField = entry.getKey();
				}

			}
			BM25FParameters.idfField = maxField;
		}
		return idfField;

	}

	/**
	 * 
	 * @return the parameter k1, by default is 2
	 */
	public static float getK1() {
		return K1;
	}

	/**
	 * Set the k1 parameter
	 * 
	 * @param k1
	 */
	public static void setK1(float k1) {
		K1 = k1;
	}

	/**
	 * Load field average length from a file and set idfField value, the file
	 * must have the next format: <BR>
	 * FIELD_NAME <BR>
	 * FLOAT_VALUE <BR>
	 * ANOTHER_FIELD_NAME <BR>
	 * ANOTHER_FIELD_VALUE<BR>
	 * for example:<BR>
	 * CONTENT<BR>
	 * 459.2903f<BR>
	 * ANCHOR<BR>
	 * 84.55523f<BR>
	 * 
	 * @param path
	 *            absolute path of the file
	 * @throws NumberFormatException
	 * @throws IOException
	 */

	public static void load(String path) throws NumberFormatException, IOException {
		BufferedReader in = new BufferedReader(new FileReader(path));
		String line;
		float max = -1;
		String maxField = "";
		while (null != (line = in.readLine())) {
			String field = line;
			Float avg = new Float(in.readLine());
			if (avg > max) {
				max = avg;
				maxField = field;
			}
			BM25FParameters.setAverageLength(field, avg);
		}
		BM25FParameters.idfField = maxField;
	}

}
