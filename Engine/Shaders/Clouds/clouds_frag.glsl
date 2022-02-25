#version 130

in float time;
uniform sampler2D p3d_Texture0;
in vec4 texcoord0;
in vec4 texcoord1;
uniform vec4 p3d_Color;
uniform vec4 p3d_ColorScale;
in vec4 color;
out vec4 o_color;

void main() {
    // Fetch all textures.
    vec4 tex0 = texture2D(p3d_Texture0, texcoord0.xy);
    vec4 tex1 = texture2D(p3d_Texture0, texcoord1.xy);
    o_color = vec4(color.rgb+p3d_Color.rgb, mix(tex0.a, tex1.a, time))*p3d_ColorScale;
}
