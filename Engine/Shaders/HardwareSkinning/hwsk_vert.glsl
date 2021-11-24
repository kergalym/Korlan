#version 130

in vec4 p3d_Vertex;
in vec4 p3d_Color;
in vec2 p3d_MultiTexCoord0;

in vec4 transform_weight;
in uvec4 transform_index;

uniform mat4 p3d_ModelViewProjectionMatrix;

uniform mat4 p3d_TransformTable[100];

out vec4 color;
out vec2 texcoord;

void main() {
  mat4 matrix = p3d_TransformTable[transform_index.x] * transform_weight.x
              + p3d_TransformTable[transform_index.y] * transform_weight.y
              + p3d_TransformTable[transform_index.z] * transform_weight.z
              + p3d_TransformTable[transform_index.w] * transform_weight.w;

  gl_Position = p3d_ModelViewProjectionMatrix * matrix * p3d_Vertex;
  color = p3d_Color;
  texcoord = p3d_MultiTexCoord0;
}