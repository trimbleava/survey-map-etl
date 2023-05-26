<?xml version="1.0" encoding="ISO-8859-1"?>
<StyledLayerDescriptor version="1.0.0" 
    xsi:schemaLocation="http://www.opengis.net/sld StyledLayerDescriptor.xsd" 
    xmlns="http://www.opengis.net/sld" 
    xmlns:ogc="http://www.opengis.net/ogc" 
    xmlns:xlink="http://www.w3.org/1999/xlink" 
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <NamedLayer>
    <Name>Risers</Name>
    <UserStyle>
      <Title>Southwest</Title>
      <FeatureTypeStyle>
        <Rule>
          <Name>Anodeless</Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>RISERTYPE</ogc:PropertyName>
              <ogc:Literal>Anodeless</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>triangle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#E74C3C</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#909497</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>10</Size>
              <Rotation>270</Rotation>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>Steel</Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>RISERTYPE</ogc:PropertyName>
              <ogc:Literal>Steel</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>triangle</WellKnownName>
                <Fill>
                  <CssParameter name="fill">#D2CDCA</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#909497</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>10</Size>
              <Rotation>270</Rotation>
            </Graphic>
          </PointSymbolizer>
        </Rule>
        <Rule>
          <Name>Inactive</Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>RISERTYPE</ogc:PropertyName>
              <ogc:Literal>Inactive</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <PointSymbolizer>
            <Graphic>
              <Mark>
                <WellKnownName>triangle</WellKnownName>
                <Fill>
                  <CssParameter name="fill-opacity">0</CssParameter>
                </Fill>
                <Stroke>
                  <CssParameter name="stroke">#E5E7E9</CssParameter>
                  <CssParameter name="stroke-width">0.5</CssParameter>
                </Stroke>
              </Mark>
              <Size>10</Size>
              <Rotation>270</Rotation>
            </Graphic>
          </PointSymbolizer>
        </Rule>
      </FeatureTypeStyle>
    </UserStyle>
  </NamedLayer>
</StyledLayerDescriptor>
