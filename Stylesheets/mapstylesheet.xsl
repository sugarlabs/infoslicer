<?xml version="1.0"?>
<!-- Copyright (C) IBM Corporation 2008 -->
<html xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xsl:version="1.0">
<head>
	<title><xsl:value-of select="map/@title" /></title>
	<link rel="stylesheet" type="text/css" href="mapstyle.css" title="Selected Stylesheet" />
</head>
<body>
	<h1>
		<xsl:value-of select="map/@title" />
	</h1>

	<xsl:for-each select="map">
		<li>
		<xsl:for-each select="topicref">
			<ul><a><xsl:attribute name="href">
				<xsl:value-of select="@href" />
			</xsl:attribute> 
			<xsl:value-of select="@navtitle" /></a></ul>
		</xsl:for-each>
		</li>
	</xsl:for-each>
</body>
</html>
