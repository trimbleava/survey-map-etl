<?xml version="1.0" encoding="UTF-8"?>
<sld:StyledLayerDescriptor xmlns="http://www.opengis.net/sld" 
 xmlns:sld="http://www.opengis.net/sld" 
 xmlns:gml="http://www.opengis.net/gml" 
 xmlns:ogc="http://www.opengis.net/ogc" 
 version="1.0.0">
  <sld:NamedLayer>
    <sld:Name>MainLines</sld:Name>
    <sld:UserStyle>
      <sld:Name>MainLines</sld:Name>
      <sld:FeatureTypeStyle>
        <sld:Name>name</sld:Name>
        <sld:Rule>
          <sld:Name>Distribution</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>MAINTYPE</ogc:PropertyName>
              <ogc:Literal>Distribution</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:LineSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#03b40b</sld:CssParameter>
              <sld:CssParameter name="stroke-linecap">square</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">2</sld:CssParameter>
            </sld:Stroke>
          </sld:LineSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Feeder</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>MAINTYPE</ogc:PropertyName>
              <ogc:Literal>Feeder</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:LineSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#ff7f00</sld:CssParameter>
              <sld:CssParameter name="stroke-linecap">square</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">2</sld:CssParameter>
            </sld:Stroke>
          </sld:LineSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Transmission</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>MAINTYPE</ogc:PropertyName>
              <ogc:Literal>Transmission</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:LineSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#a84cd3</sld:CssParameter>
              <sld:CssParameter name="stroke-linecap">square</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">2</sld:CssParameter>
            </sld:Stroke>
          </sld:LineSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:Name>Transmission &gt; 20</sld:Name>
          <ogc:Filter>
            <ogc:PropertyIsEqualTo>
              <ogc:PropertyName>MAINTYPE</ogc:PropertyName>
              <ogc:Literal>Transmission &gt; 20</ogc:Literal>
            </ogc:PropertyIsEqualTo>
          </ogc:Filter>
          <sld:LineSymbolizer>
            <sld:Stroke>
              <sld:CssParameter name="stroke">#00FFFF</sld:CssParameter>
              <sld:CssParameter name="stroke-linecap">square</sld:CssParameter>
              <sld:CssParameter name="stroke-linejoin">bevel</sld:CssParameter>
              <sld:CssParameter name="stroke-width">2</sld:CssParameter>
            </sld:Stroke>
          </sld:LineSymbolizer>
        </sld:Rule>
        <sld:Rule>
          <sld:TextSymbolizer>
            <sld:Label>
              <ogc:PropertyName>SWGUID</ogc:PropertyName>
            </sld:Label>
            <sld:Font>
              <sld:CssParameter name="font-family">Serif</sld:CssParameter>
              <sld:CssParameter name="font-size">13</sld:CssParameter>
              <sld:CssParameter name="font-style">normal</sld:CssParameter>
              <sld:CssParameter name="font-weight">normal</sld:CssParameter>
            </sld:Font>
            <sld:LabelPlacement>
              <sld:LinePlacement>
                <sld:PerpendicularOffset>0.0</sld:PerpendicularOffset>
              </sld:LinePlacement>
            </sld:LabelPlacement>
            <sld:Fill>
              <sld:CssParameter name="fill">#000000</sld:CssParameter>
            </sld:Fill>
            <sld:VendorOption name="followLine">true</sld:VendorOption>
            <sld:VendorOption name="maxAngleDelta">90</sld:VendorOption>
            <sld:VendorOption name="maxDisplacement">400</sld:VendorOption>
            <sld:VendorOption name="repeat">150</sld:VendorOption>
          </sld:TextSymbolizer>
        </sld:Rule>
      </sld:FeatureTypeStyle>
    </sld:UserStyle>
  </sld:NamedLayer>
</sld:StyledLayerDescriptor>

