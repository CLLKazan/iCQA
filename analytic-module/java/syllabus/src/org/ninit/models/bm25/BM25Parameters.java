package org.ninit.models.bm25;

/**
 * BM25Parameters.java
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
import java.util.HashMap;
import java.util.Map;

/**
 * Parameters needed to calculate the BM25 relevance.
 * 
 * @author "Joaquin Perez-Iglesias"
 * 
 */
public class BM25Parameters {

	private static float B = 0.75f;
	private static float K1 = 2f;

	protected BM25Parameters() {
	};

	/**
	 * @return the BM25 length normalization parameter b, generally b =[0,1], by
	 *         default is equals to 0.75
	 */
	public static float getB() {
		return B;
	}

	/**
	 * Set the BM25 length normalization parameter
	 * 
	 * @param b
	 *            the b parameter, generally b =[0,1], by default is equals to
	 *            0.75
	 */
	public static void setB(float b) {
		B = b;
	}

	/**
	 * 
	 * @return the k1 parameter, by default is equivalent to 2
	 */
	public static float getK1() {
		return K1;
	}

	/**
	 * Set the k1 parameter, by default is equivalent to 2
	 * 
	 * @param k1
	 */
	public static void setK1(float k1) {
		K1 = k1;
	}

	protected static Map<String, Float> avgLength = new HashMap<String, Float>();

	/**
	 * Load field average length from a file with the next format: <BR>
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
	public static void load(String path) throws NumberFormatException,
			IOException {
		BufferedReader in = new BufferedReader(new FileReader(path));
		String line;
		while (null != (line = in.readLine())) {
			String field = line;
			Float avg = new Float(in.readLine());
			BM25Parameters.setAverageLength(field, avg);
		}
		in.close();
	}

	/**
	 * Set the average length for the field 'field'
	 * 
	 * @param field
	 * @param avg
	 */
	public static void setAverageLength(String field, float avg) {
		BM25Parameters.avgLength.put(field, avg);
	}

	/**
	 * Return the field 'field' average length
	 * 
	 * @param field
	 * @return field average length
	 */
	public static float getAverageLength(String field) {
		try {
			return BM25Parameters.avgLength.get(field);
		} catch (NullPointerException e) {
			System.out
					.println("Can't find average length for field '"
							+ field
							+ "' you have to set field average length values, before execute a search.");
			throw e;
		}
	}

}
