#version 150

uniform sampler2D p3d_Texture0;

// Input from vertex shader
in vec2 texcoord;

// Output to the screen
out vec4 p3d_FragColor;

void main() {
  vec4 color = texture(p3d_Texture0, texcoord);
  p3d_FragColor = color.bgra;
}