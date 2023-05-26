<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0"
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd"
    xmlns="http://www.opengis.net/sld"
    xmlns:ogc="http://www.opengis.net/ogc"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
    <!-- a named layer is the basic building block of an sld document -->

  <NamedLayer>
    <Name>BusinessDistricts</Name>
    <UserStyle>
        <!-- they have names, titles and abstracts -->

      <Title>Grey Polygon</Title>
      <Abstract>A sample style that just prints out a %transparent grey interior with a black outline</Abstract>
      <!-- FeatureTypeStyles describe how to render different features -->
      <!-- a feature type for polygons -->

      <FeatureTypeStyle>
        <!--FeatureTypeName>Feature</FeatureTypeName-->
        <Rule>
          <Name>Rule 1</Name>
          <Title>Grey Fill with transparency and Grey Outline</Title>
          <Abstract>Grey Fill with transparency and Grey Outline 2 pixel in width</Abstract>

          <!-- like a linesymbolizer but with a fill too -->
          <PolygonSymbolizer>
            <Fill>
              <CssParameter name="fill">#AAAAAA</CssParameter>
              <CssParameter name="fill-opacity">0.25</CssParameter>
            </Fill>
            <Stroke>
              <CssParameter name="stroke">#AAAAAA</CssParameter>
              <CssParameter name="stroke-width">2</CssParameter>
            </Stroke>
          </PolygonSymbolizer>
        </Rule>
        </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>