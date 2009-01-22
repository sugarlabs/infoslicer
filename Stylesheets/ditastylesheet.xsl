<?xml version="1.0"?>
<!-- Copyright (C) IBM Corporation 2008 -->
<html xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xsl:version="1.0">
<head>
	<title><xsl:value-of select="reference/title" /></title>
	<link rel="stylesheet" type="text/css" href="ditastyle.css" title="Selected Stylesheet" />
</head>
<body>
	<p>
		<a href="librarymap.ditamap">Return to index</a>
	</p>
	<h1>
		<xsl:value-of select="reference/title" />
	</h1>

	<p>
		<xsl:copy-of select="reference/shortdesc" />
		<xsl:if test="contains(reference/section/p/@id,'shortdesc')">
			<xsl:for-each select="reference/section/p">
				<xsl:for-each select="image">
					<img>
					<xsl:attribute name="src">
				        <xsl:value-of select="@href" />
				        </xsl:attribute>
					</img>
				</xsl:for-each>
			<xsl:copy-of select="ph" />
			</xsl:for-each>
		</xsl:if>
	</p>

	<xsl:for-each select="reference/refbody">
		<p>
			<xsl:copy-of select="p" />
		</p>
	</xsl:for-each>

	<xsl:for-each select="reference/reference">
		<h2>
			<xsl:value-of select="title" />
		</h2>

		<xsl:for-each select="refbody">
			<h3>
				<xsl:value-of select="title" />
			</h3>
			<p>
				<xsl:value-of select="p" />
			</p>
		</xsl:for-each>

		<xsl:for-each select="refbody/section">
			<h3>
				<xsl:value-of select="title" />
			</h3>
		<xsl:for-each select="p">
			<p>
			<xsl:for-each select="image">
				<img>
				<xsl:attribute name="src">
			        <xsl:value-of select="@href" />
			        </xsl:attribute>
				</img>
			</xsl:for-each>
			<xsl:copy-of select="ph" />
			</p>
		</xsl:for-each>
		</xsl:for-each>
<xsl:comment>
		<xsl:copy-of select="refbody/section/ul" />
		<xsl:copy-of select="refbody/section/ol" />
</xsl:comment>
	</xsl:for-each>

	<xsl:if test="not(contains(reference/section/p/@id,'shortdesc'))">
	<xsl:for-each select="reference">
		<xsl:for-each select="section/p">
			<p>
			<xsl:for-each select="image">
				<img>
				<xsl:attribute name="src">
			        <xsl:value-of select="@href" />
			        </xsl:attribute>
				</img>
			</xsl:for-each>
			<xsl:copy-of select="ph" />
			</p>
		</xsl:for-each>
	</xsl:for-each>
	</xsl:if>
</body>
</html>
