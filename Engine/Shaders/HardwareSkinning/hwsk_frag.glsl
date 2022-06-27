#version 130
in vec4 color;
in vec2 texcoord;
out vec4 fragColor;
uniform sampler2D p3d_Texture0;

void main() {
  fragColor = color * texture(p3d_Texture0, texcoord);
}