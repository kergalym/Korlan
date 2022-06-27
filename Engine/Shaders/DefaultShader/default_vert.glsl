#version 150

// Uniform inputs
uniform mat4 p3d_ModelViewProjectionMatrix;

// Vertex inputs
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

// Output to fragment shader
out vec2 texcoord;
out vec4 position;

void main() {
  position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    if ( position.x < 0.0 ) position = vec4(2.0, 0.0, 0.0, 1.0);
  texcoord = p3d_MultiTexCoord0;
}
