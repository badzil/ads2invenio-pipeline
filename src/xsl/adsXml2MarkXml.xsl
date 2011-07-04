<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
    <xsl:output method="xml" version="1.0" encoding="UTF-8" indent="yes" omit-xml-declaration="yes"/>
    <xsl:variable name="smallcase" select="'abcdefghijklmnopqrstuvwxyz'" />
	<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'" />
	<xsl:template match="/">
		<collection>
			<xsl:for-each select="/records/record">
				<record>
					<!-- main collections: databases -->
					<xsl:if test="databases">
						<xsl:for-each select="databases/database">
							<datafield tag="980" ind1="" ind2="">
								<xsl:choose>
									<xsl:when test=". = 'AST'">
										<subfield code="a">ASTRONOMY</subfield>
									</xsl:when>
									<xsl:when test=". = 'PHY'">
										<subfield code="a">PHYSICS</subfield>
									</xsl:when>
									<xsl:when test=". = 'GEN'">
										<subfield code="a">GENERAL</subfield>
									</xsl:when>
									<xsl:when test=". = 'PRE'">
										<subfield code="a">EPRINT</subfield>
									</xsl:when>
									<xsl:otherwise>
										<subfield code="a"><xsl:value-of select="." /></subfield>
									</xsl:otherwise>
								</xsl:choose>
							</datafield>
						</xsl:for-each>
					</xsl:if>
		            <!-- other collections -->
		            <xsl:if test="@collection = '1'">
		             <datafield tag="980" ind1="" ind2="">
		             	<subfield code="a">COLLECTION</subfield>
		             </datafield>
		            </xsl:if>
		            <xsl:if test="@nonarticle = '1'">
		             <datafield tag="980" ind1="" ind2="">
		             	<subfield code="a">NONARTICLE</subfield>
		             </datafield>
		            </xsl:if>
		            <xsl:if test="@ocrabstract = '1'">
		             <datafield tag="980" ind1="" ind2="">
		             	<subfield code="a">OCRABSTRACT</subfield>
		             </datafield>
		            </xsl:if>
		            <xsl:if test="@openaccess = '1'">
		             <datafield tag="980" ind1="" ind2="">
		             	<subfield code="a">OPENACCESS</subfield>
		             </datafield>
		            </xsl:if>
		            <xsl:if test="@private = '1'">
		             <datafield tag="980" ind1="" ind2="">
		             	<subfield code="a">PRIVATE</subfield>
		             </datafield>
		            </xsl:if>
		            <xsl:if test="@refereed = '1'">
		             <datafield tag="980" ind1="" ind2="">
		             	<subfield code="a">REFEREED</subfield>
		             </datafield>
		            </xsl:if>
		            <!-- Special collection for eprints -->
		            <xsl:if test="arxivcategories">
		            	<xsl:for-each select="arxivcategories/arxivcategory">
		            		<datafield tag="980" ind1="" ind2="">
		             			<subfield code="a"><xsl:value-of select="."/></subfield>
		             			<xsl:if test="@type = 'main'">
		             				<subfield code="n">Main arXiv collection</subfield>
		             			</xsl:if>
		             			<xsl:if test="@type = ''">
		             				<subfield code="n">arXiv collection</subfield>
		             			</xsl:if>
		             		</datafield>
		            	</xsl:for-each>
		            </xsl:if>
		            <!-- Special collection "type" -->
		            <xsl:if test="@type">
			            <xsl:if test="translate(@type, $smallcase, $uppercase) != 'EPRINT'">
				             <datafield tag="980" ind1="" ind2="">
				             	<subfield code="a"><xsl:value-of select="translate(@type, $smallcase, $uppercase)" /></subfield>
				             </datafield>
			            </xsl:if>
		             <datafield tag="690" ind1="C" ind2="">
		                    <subfield code="a"><xsl:value-of select="translate(@type, $smallcase, $uppercase)" /></subfield>
		                </datafield>
		            </xsl:if>
		            
					<!-- bibcode -->
		            <xsl:if test="bibcode">
		                <datafield tag="970" ind1="" ind2="">
		                    <subfield code="a"><xsl:value-of select="bibcode"/></subfield>
		                </datafield>
		                <datafield tag="037" ind1="" ind2="">
		                    <subfield code="a"><xsl:value-of select="bibcode"/></subfield>
		                    <subfield code="9">ADS bibcode</subfield>
		                </datafield>
		            </xsl:if>
		            
		            <!-- Alternate bibcodes -->
		            <xsl:if test="alternates">
		            	<xsl:variable name="mainbibcode" select="bibcode" />
		            	<xsl:for-each select="alternates/alternate">
		            		<xsl:if test=". != $mainbibcode">
			            		<datafield tag="037" ind1="" ind2="">
				                    <subfield code="a"><xsl:value-of select="."/></subfield>
				                    <subfield code="9"><xsl:value-of select="@type"/></subfield>
			                	</datafield>
			                </xsl:if>
		            	</xsl:for-each>
		            </xsl:if>
		            
		            <!-- other codes: arXiv and DOI -->
		            <xsl:if test="DOI">
		            	<datafield tag="037" ind1="" ind2="">
		                    <subfield code="a"><xsl:value-of select="DOI"/></subfield>
		                    <subfield code="9">DOI</subfield>
		                </datafield>
		            </xsl:if>
		            <xsl:if test="preprintid">
		            	<datafield tag="037" ind1="" ind2="">
		                    <subfield code="a"><xsl:value-of select="preprintid"/></subfield>
		                    <subfield code="9">arXiv</subfield>
		                </datafield>
		            </xsl:if>
		            <!-- title -->
		            <xsl:if test="title">
		            	<xsl:choose>
		            		<xsl:when test="count(title) = 1">
			            		<datafield tag="245" ind1="" ind2="">
			                    	<subfield code="a"><xsl:value-of select="title"/></subfield>
			                    	<xsl:if test="@lang">
			                    		<subfield code="y"><xsl:value-of select="@lang"/></subfield>
			                    	</xsl:if>
			                	</datafield>
		            		</xsl:when>
		            		<!-- In case I have more then one title -->
		            		<xsl:when test="count(title) > 1">
		            			<xsl:choose>
			            			<!-- If there is one or more title with a specific language not English I split the nodes between the (not English) and the 
			            			(English + unknown + title without lang attribute)
			            			-->
		            				<xsl:when test="title[(@lang != '') and (@lang != 'en')]">
		            					<xsl:for-each select="title[(@lang != '') and (@lang != 'en')]">
			            					<!-- If there are more then one not English title, only the first is 245 -->
			            					<xsl:choose>
			            						<xsl:when test="position() = 1">
			            							<datafield tag="245" ind1="" ind2="">
							                    		<subfield code="a"><xsl:value-of select="."/></subfield>
							                    		<subfield code="y"><xsl:value-of select="@lang"/></subfield>
					                				</datafield>
			            						</xsl:when>
			            						<xsl:otherwise>
			            							<datafield tag="242" ind1="" ind2="">
							                    		<subfield code="a"><xsl:value-of select="."/></subfield>
							                    		<subfield code="y"><xsl:value-of select="@lang"/></subfield>
					                				</datafield>
			            						</xsl:otherwise>
			            					</xsl:choose>
			            				</xsl:for-each>
			            				<xsl:for-each select="title[(@lang = '') or (@lang = 'en') or not(@lang)]">
			            					<datafield tag="242" ind1="" ind2="">
					                    		<subfield code="a"><xsl:value-of select="."/></subfield>
					                    		<xsl:if test="(@lang) and (@lang != '')">
				                    				<subfield code="y"><xsl:value-of select="@lang"/></subfield>
				                    			</xsl:if>
					                		</datafield>
			            				</xsl:for-each>
		            				</xsl:when>
		            				<!-- Otherwise I set as 245 the first one and all the others as 242 -->
		            				<xsl:otherwise>
		            					<xsl:for-each select="title">
			            					<xsl:choose>
			            						<xsl:when test="position() = 1">
			            							<datafield tag="245" ind1="" ind2="">
							                    		<subfield code="a"><xsl:value-of select="."/></subfield>
							                    		<xsl:if test="@lang">
				                    						<subfield code="y"><xsl:value-of select="@lang"/></subfield>
				                    					</xsl:if>
					                				</datafield>
			            						</xsl:when>
			            						<xsl:otherwise>
			            							<datafield tag="242" ind1="" ind2="">
							                    		<subfield code="a"><xsl:value-of select="."/></subfield>
							                    		<xsl:if test="@lang">
				                    						<subfield code="y"><xsl:value-of select="@lang"/></subfield>
				                    					</xsl:if>
					                				</datafield>
			            						</xsl:otherwise>
			            					</xsl:choose>
		            					</xsl:for-each>
		            				</xsl:otherwise>
		            			</xsl:choose>
		            		</xsl:when>
		            	</xsl:choose>
		                
		            </xsl:if>
		            <!--Authors-->
		            <xsl:if test="author">
		                <xsl:for-each select="author">
		                	<!-- <xsl:variable name="position" select="position()" />-->
		                    <xsl:choose>
		                        <xsl:when test="@nr = 1">
		                            <datafield tag="100" ind1="" ind2="">
		                            	<!-- normal name -->
		                                <subfield code="a"><xsl:value-of select="name/western"/></subfield>
		                                <!-- normalized name -->
		                                <xsl:if test="name/normalized">
		                                	<subfield code="b"><xsl:value-of select="name/normalized"/></subfield>
		                                </xsl:if>
		                                <xsl:if test="name/native">
		                                	<subfield code="c"><xsl:value-of select="name/native"/></subfield>
		                                </xsl:if>
		                                <!-- type of author -->
		                                <xsl:if test="type">
		                                	<subfield code="t"><xsl:value-of select="type"/></subfield>
		                                </xsl:if>
		                                <!-- Affiliations -->
		                                <xsl:if test="affiliations">
		                                	<xsl:for-each select="affiliations/affiliation">
		                                		<subfield code="u"><xsl:value-of select="."/></subfield>
		                                	</xsl:for-each>
		                                </xsl:if>
		                                <!-- email -->
		                                <xsl:if test="emails">
		                                	<xsl:for-each select="emails/email">
		                                		<subfield code="m"><xsl:value-of select="."/></subfield>
		                                	</xsl:for-each>
		                                </xsl:if>
		                            </datafield>
		                        </xsl:when>
		                        <xsl:otherwise>
		                            <datafield tag="700" ind1="" ind2="">
		                                <!-- normal name -->
		                                <subfield code="a"><xsl:value-of select="name/western"/></subfield>
		                                <!-- normalized name -->
		                                <xsl:if test="name/normalized">
		                                	<subfield code="b"><xsl:value-of select="name/normalized"/></subfield>
		                                </xsl:if>
		                                <xsl:if test="name/native">
		                                	<subfield code="c"><xsl:value-of select="name/native"/></subfield>
		                                </xsl:if>
		                                <!-- type of author -->
		                                <xsl:if test="type">
		                                	<subfield code="t"><xsl:value-of select="type"/></subfield>
		                                </xsl:if>
		                                <!-- Affiliations -->
		                                <xsl:if test="affiliations">
		                                	<xsl:for-each select="affiliations/affiliation">
		                                		<subfield code="u"><xsl:value-of select="."/></subfield>
		                                	</xsl:for-each>
		                                </xsl:if>
		                                <!-- email -->
		                                <xsl:if test="emails">
		                                	<xsl:for-each select="emails/email">
		                                		<subfield code="m"><xsl:value-of select="."/></subfield>
		                                	</xsl:for-each>
		                                </xsl:if>
		                            </datafield>
		                        </xsl:otherwise>
		                    </xsl:choose>
		                </xsl:for-each>
					</xsl:if>
		            <!-- 
		                    Journal
		                        I consider the name of the journal only before the 1st ",". To consider correctly we have to split the value into more subfields
		            -->
	               	<xsl:if test="journal">
	                	<datafield tag="773" ind1="" ind2="">
	                       <subfield code="p"><xsl:value-of select="substring-before(journal,',')"/></subfield>
	                       <xsl:if test="volume">
	                           <subfield code="v"><xsl:value-of select="volume"/></subfield>
	                       </xsl:if>
	                       <xsl:if test="page">
	                           <subfield code="c"><xsl:value-of select="page"/><xsl:if test="lastpage"><xsl:text>-</xsl:text><xsl:value-of select="lastpage"/></xsl:if></subfield>
	                       </xsl:if>
	                       <subfield code="y"><xsl:value-of select="substring(bibcode, 1, 4)"/></subfield>
	                       <!-- Full string of the journal -->
	                       <subfield code="f"><xsl:value-of select="journal"/></subfield>
	                	</datafield>
					</xsl:if>
	                <!-- Publication date -->
	                <xsl:if test="numpubdate">
	                    <datafield tag="269" ind1="" ind2="">
	                       <subfield code="c"><xsl:value-of select="substring(numpubdate, 4, 4)"/><xsl:text>-</xsl:text><xsl:value-of select="substring(numpubdate, 1, 2)"/><xsl:text>-00</xsl:text></subfield>
	                    </datafield>
		                <!--Publication year-->
		                <datafield tag="260" ind1="" ind2="">
		                    <subfield code="c"><xsl:value-of select="substring(numpubdate, 4, 4)"/></subfield>
		                </datafield>
	                </xsl:if>
	                <!-- Keywords -->
	                <xsl:if test="keywords">
	                   <xsl:for-each select="keywords">
	                       <xsl:variable name="institute" select="@type" />
	                       <xsl:for-each select="keyword">
	                           <xsl:if test="string-length(.) != 0">
		                           <datafield tag="653" ind1="1" ind2="">
		                               <subfield code="a"><xsl:value-of select="."/></subfield>
		                               <xsl:if test="$institute != ''">
		                                   <subfield code="9"><xsl:value-of select="$institute"/></subfield>
		                               </xsl:if>
		                           </datafield>
	                           </xsl:if>
	                       </xsl:for-each>
	                   </xsl:for-each>
	                </xsl:if>
	                <!-- Copyright -->
	                <xsl:if test="copyright">
	                    <datafield tag="598" ind1="" ind2="">
	                        <subfield code="a"><xsl:value-of select="copyright"/></subfield>
	                    </datafield>
	                </xsl:if>
	               <!-- Abstract -->
	                <xsl:if test="abstract">
	                	<xsl:for-each select="abstract">
		                	<xsl:if test=". != 'Not Available'">
			                    <datafield tag="520" ind1="" ind2="">
			                        <subfield code="a"><xsl:value-of select="."/></subfield>
			                        <xsl:if test="(@lang) and (@lang != '')">
                  						<subfield code="y"><xsl:value-of select="@lang"/></subfield>
                  					</xsl:if>
			                    </datafield>
		                    </xsl:if>
	                    </xsl:for-each>
	                </xsl:if>
	                <!-- Associate papers -->
	                <xsl:if test="associates">
	                	<xsl:for-each select="associates/associate">
	                		<datafield tag="591" ind1="" ind2="">
	                            <subfield code="a"><xsl:value-of select="."/></subfield>
	                            <subfield code="c"><xsl:value-of select="@comment"/></subfield>
	                        </datafield>
	                	</xsl:for-each>
	                </xsl:if>
	                <!-- Links -->
	                <xsl:for-each select="link">
	                    <xsl:if test="(@type != 'ABSTRACT') and (@type != 'CUSTOM') and (@type != 'REFERENCES') and (@type != 'CITATIONS') and (@type != 'REFCIT') and (@type != 'ASSOCIATED') and (@type != 'AR')">
	                        <datafield tag="856" ind1="4" ind2="">
	                            <subfield code="u"><xsl:value-of select="url"/></subfield>
	                            <subfield code="y"><xsl:value-of select="name"/></subfield>
	                        </datafield>
	                    </xsl:if>  
	                </xsl:for-each>
	                <xsl:if test="(count(link[@type='ARTICLE']) = 0) and (count(link[@type='GIF']) &gt; 0)">
	                    <datafield tag="856" ind1="4" ind2="^">
	                        <subfield code="u"><xsl:value-of select="substring-before(link[@type='GIF']/url, 'GIF')"/><xsl:text>ARTICLE</xsl:text></subfield>
	                        <subfield code="y">Full Printable Article (PDF/Postscript)</subfield>
	                    </datafield>
	                </xsl:if>
	                <!-- References -->
	                <xsl:if test="reference">
	               		<xsl:for-each select="reference">
	               			<datafield tag="999" ind1="C" ind2="5">
	                        	<subfield code="o"><xsl:text>[</xsl:text><xsl:value-of select="position()"/><xsl:text>]</xsl:text></subfield>
	                        	<!-- control if I have a resolved references -->
	                        	<!-- <xsl:choose>
	                        		<xsl:when test="(string(number(substring(., 1, 4))) != 'NaN') and not(contains(.,' ')) and (string-length(.) = 19)">
	                        			<subfield code="r"><xsl:value-of select="."/></subfield>
	                        		</xsl:when>
	                        		<xsl:otherwise>
	                        			<subfield code="m"><xsl:value-of select="."/></subfield>
	                        		</xsl:otherwise>
	                        	</xsl:choose> -->
	                        	<xsl:if test="@bibcode != ''">
	                        		<subfield code="r"><xsl:value-of select="@bibcode"/></subfield>
	                        	</xsl:if>
	                        	<xsl:if test="@arxid != ''">
	                        		<subfield code="i">arxiv: <xsl:value-of select="@arxid"/></subfield>
	                        	</xsl:if>
	                        	<xsl:if test="@doi != ''">
	                        		<subfield code="i">doi: <xsl:value-of select="@doi"/></subfield>
	                        	</xsl:if>
	                        	<xsl:if test="@score != ''">
	                        		<subfield code="e"><xsl:value-of select="@score"/></subfield>
	                        	</xsl:if>
	                        	<xsl:if test="@source != ''">
	                        		<subfield code="f"><xsl:value-of select="@source"/></subfield>
	                        	</xsl:if>
	                        	<xsl:if test="not(string-length(.) = 0)">
	                        		<subfield code="m"><xsl:value-of select="."/></subfield>
	                        	</xsl:if>
	                        </datafield>
	               		</xsl:for-each>
	                </xsl:if>
	                <!-- Origin -->
	                <xsl:if test="origin">
	                	<xsl:for-each select="origin">
	                		<datafield tag="907" ind1="" ind2="">
	                        	<subfield code="a"><xsl:value-of select="."/></subfield>
	                    	</datafield>
	                	</xsl:for-each>
	                </xsl:if>
					<!-- Comments -->
					<xsl:if test="comment">
						<datafield tag="500" ind1="" ind2="">
							<subfield code="a"><xsl:value-of select="comment"/></subfield>
							<subfield code="9"><xsl:value-of select="comment/@origin"/></subfield>
						</datafield>
					</xsl:if>
					<!-- Timestamp signature -->
					<xsl:if test="ADStimestamp">
						<datafield tag="995" ind1="" ind2="">
							<subfield code="a"><xsl:value-of select="ADStimestamp"/></subfield>
							<subfield code="9"><xsl:value-of select="ADStimestamp/@origin"/></subfield>
						</datafield>
					</xsl:if>
				</record>	
			</xsl:for-each>
		</collection>
	</xsl:template>
</xsl:stylesheet>